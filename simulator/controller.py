"""Controllers for FlexProof simulation.

Three controllers implementing different operational strategies:
- BaselineController: No flexibility intervention (unmanaged grid)
- ReactiveController: Reacts to actual stress events only (no foresight)
- PredictiveController: Forecasts upcoming stress and prepares flexibility in advance

All controllers consume the same DataSource interface and return ScenarioResult objects.
"""
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from models.schemas import (
    RiskLevel, BatteryAction, ControllerEvent, ControllerAction,
    IntervalRecord, SimulationMetrics, ScenarioResult, ForecastResult
)
from .battery import CommunityBattery
from .flexible_loads import FlexibleLoadManager
from .feeder import Feeder
from .forecasting import ForecastingEngine
from .stress import StressPredictionEngine
from .flexibility import FlexibilityCoordinator
from .data_sources.base import DataSource


def records_to_dataframe(records: List[IntervalRecord]) -> pd.DataFrame:
    """Convert a list of IntervalRecord objects to a pandas DataFrame."""
    if not records:
        return pd.DataFrame()
    data = []
    for r in records:
        data.append({
            'timestamp': r.timestamp,
            'demand_kw': r.demand_kw,
            'renewable_kw': r.renewable_kw,
            'net_demand_kw': r.net_demand_kw,
            'forecast_demand_kw': r.forecast_demand_kw,
            'forecast_renewable_kw': r.forecast_renewable_kw,
            'forecast_net_demand_kw': r.forecast_net_demand_kw,
            'forecast_gap_kw': r.forecast_gap_kw,
            'stress': r.stress,
            'risk_level': r.risk_level,
            'battery_soc': r.battery_soc,
            'battery_action': r.battery_action,
            'flexibility_available_kw': r.flexibility_available_kw,
            'flexibility_reserved_kw': r.flexibility_reserved_kw,
            'flexibility_dispatched_kw': r.flexibility_dispatched_kw,
            'deficit_kw': r.deficit_kw,
            'controlled_net_demand_kw': r.controlled_net_demand_kw
        })
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df


class BaselineController:
    """No-intervention baseline controller.
    
    Runs the feeder with no active flexibility dispatch.
    The battery remains idle at its configured initial SOC.
    Records all metrics for scientific comparison.
    """
    
    def __init__(self, config):
        self.config = config
        self.feeder = Feeder(
            config.feeder.firm_limit_kw,
            config.feeder.warning_threshold,
            config.feeder.watch_threshold
        )
    
    def run(self, data_source: DataSource) -> ScenarioResult:
        """Run baseline simulation."""
        demand_df = data_source.get_demand()
        renewable_df = data_source.get_renewable()
        timestamps = data_source.get_timestamps()
        dt = self.config.simulation.resolution_minutes / 60.0
        initial_soc = self.config.battery.initial_soc
        
        records = []
        
        for i in range(len(timestamps)):
            ts = timestamps[i]
            demand_kw = float(demand_df['total_kw'].iloc[i])
            renewable_kw = float(renewable_df['solar_kw'].iloc[i])
            net_demand_kw = demand_kw - renewable_kw
            
            state = self.feeder.calculate_state(ts, demand_kw, renewable_kw)
            
            record = IntervalRecord(
                timestamp=ts,
                demand_kw=demand_kw,
                renewable_kw=renewable_kw,
                net_demand_kw=net_demand_kw,
                stress=state.stress,
                risk_level=state.risk_level.value,
                battery_soc=initial_soc,
                battery_action="IDLE",
                flexibility_available_kw=0.0,
                flexibility_reserved_kw=0.0,
                flexibility_dispatched_kw=0.0,
                deficit_kw=state.deficit_kw,
                controlled_net_demand_kw=net_demand_kw
            )
            records.append(record)
        
        df = records_to_dataframe(records)
        
        net_demand = df['net_demand_kw'].values
        stress_metrics = Feeder.calculate_stress_metrics(
            net_demand, self.config.feeder.firm_limit_kw, dt
        )
        
        metrics = SimulationMetrics(
            stress_intervals=stress_metrics['stress_intervals'],
            stress_duration_hours=stress_metrics['stress_duration_hours'],
            deficit_energy_kwh=stress_metrics['deficit_energy_kwh'],
            max_deficit_kw=stress_metrics['max_deficit_kw'],
            avg_deficit_kw=stress_metrics['avg_deficit_kw'],
            stress_percentage=stress_metrics['stress_percentage'],
            peak_net_demand_kw=stress_metrics['peak_net_demand_kw'],
            peak_demand_kw=float(df['demand_kw'].max()),
            total_renewable_kwh=float(df['renewable_kw'].sum() * dt),
            battery_throughput_kwh=0.0,
            flexibility_events=0,
            shifted_energy_kwh=0.0,
            avoided_deficit_kwh=0.0,
            min_battery_soc=initial_soc,
            max_battery_soc=initial_soc,
            forecast_mae=0.0,
            forecast_rmse=0.0
        )
        
        return ScenarioResult(
            name='Baseline',
            dataframe=df,
            metrics=metrics
        )


class ReactiveController:
    """Reactive controller - responds only to actual stress.
    
    IMPORTANT: Does NOT use forecast information to prepare resources.
    Only activates flexibility when net_demand exceeds the feeder firm limit.
    """
    
    def __init__(self, config):
        self.config = config
        self.feeder = Feeder(
            config.feeder.firm_limit_kw,
            config.feeder.warning_threshold,
            config.feeder.watch_threshold
        )
    
    def run(self, data_source: DataSource) -> ScenarioResult:
        """Run reactive simulation."""
        demand_df = data_source.get_demand()
        renewable_df = data_source.get_renewable()
        timestamps = data_source.get_timestamps()
        dt = self.config.simulation.resolution_minutes / 60.0
        n = len(timestamps)
        hours = np.array([(t.hour + t.minute / 60) for t in timestamps])
        feeder_limit = self.config.feeder.firm_limit_kw
        
        battery = CommunityBattery(
            capacity_kwh=self.config.battery.capacity_kwh,
            max_charge_power_kw=self.config.battery.max_charge_power_kw,
            max_discharge_power_kw=self.config.battery.max_discharge_power_kw,
            min_soc=self.config.battery.min_soc,
            max_soc=self.config.battery.max_soc,
            initial_soc=self.config.battery.initial_soc,
            charge_efficiency=self.config.battery.charge_efficiency,
            discharge_efficiency=self.config.battery.discharge_efficiency
        )
        flex_manager = FlexibleLoadManager(self.config.flexible_loads)
        coordinator = FlexibilityCoordinator(battery, flex_manager, dt)
        
        records = []
        events = []
        battery_history = []
        flexibility_history = []
        
        for i in range(n):
            ts = timestamps[i]
            h = hours[i]
            demand_kw = float(demand_df['total_kw'].iloc[i])
            renewable_kw = float(renewable_df['solar_kw'].iloc[i])
            net_demand_kw = demand_kw - renewable_kw
            
            battery.set_idle()
            flex_manager.update_interval(i)
            active_reduction = flex_manager.get_active_reduction(i)
            
            # 1. Safe restoration during off-peak night
            is_safe_window = (h < 5.5 or h >= 22.5)
            restoration_power = flex_manager.get_restoration_power(
                i, is_safe_window=is_safe_window, max_safe_restore_kw=60.0
            )
            effective_net_demand = net_demand_kw - active_reduction + restoration_power
            
            # 2. Battery off-peak / solar charging
            if not is_safe_window and renewable_kw > demand_kw:
                surplus = renewable_kw - demand_kw
                c_res = coordinator.handle_charging(surplus, ts)
                events.extend(c_res['events'])
            elif h < 5.5 or (10.5 <= h < 14.5 and effective_net_demand < 0.50 * feeder_limit):
                headroom = max(0.0, 0.55 * feeder_limit - effective_net_demand)
                c_res = coordinator.handle_charging(headroom, ts)
                effective_net_demand += c_res['charged_kw']
                events.extend(c_res['events'])
            
            # 3. REACTIVE: Activate ONLY if effective net demand breaches feeder limit
            flex_dispatched = active_reduction
            if effective_net_demand > feeder_limit:
                deficit = effective_net_demand - feeder_limit
                risk = RiskLevel.CRITICAL if deficit > 100 else RiskLevel.WARNING
                
                # Shift loads
                shifted_kw, act_list = flex_manager.shift_load(deficit, i, duration_intervals=8)
                flex_dispatched += shifted_kw
                
                # Re-check active reduction
                new_active_red = flex_manager.get_active_reduction(i)
                effective_net_demand = net_demand_kw - new_active_red + restoration_power
                
                # Discharge battery for any residual deficit (capped by unforecasted reactive limit)
                if effective_net_demand > feeder_limit:
                    rem_deficit = effective_net_demand - feeder_limit
                    max_react_pwr = battery.max_discharge_power_kw * self.config.controller.reactive.max_battery_discharge_fraction
                    actual_bat, _ = battery.discharge(min(rem_deficit, max_react_pwr), dt)
                    effective_net_demand -= actual_bat
                    flex_dispatched += actual_bat
                    
                    if actual_bat > 0:
                        events.append(ControllerEvent(
                            timestamp=ts,
                            decision="Battery discharge initiated",
                            reason=f"Mitigating reactive deficit of {rem_deficit:.1f} kW",
                            predicted_gap_kw=deficit,
                            required_flexibility_kw=rem_deficit,
                            resource_selected="community_battery",
                            power_requested_kw=rem_deficit,
                            power_delivered_kw=actual_bat,
                            battery_soc_before=battery.soc + actual_bat * dt / battery.discharge_efficiency / battery.capacity_kwh,
                            battery_soc_after=battery.soc
                        ))
            
            controlled_deficit = max(0.0, effective_net_demand - feeder_limit)
            state = self.feeder.calculate_state(ts, demand_kw + restoration_power, renewable_kw)
            flex_summary = flex_manager.get_summary()
            
            record = IntervalRecord(
                timestamp=ts,
                demand_kw=demand_kw,
                renewable_kw=renewable_kw,
                net_demand_kw=net_demand_kw,
                stress=effective_net_demand > feeder_limit,
                risk_level=state.risk_level.value,
                battery_soc=battery.soc,
                battery_action=battery.action.value,
                flexibility_available_kw=flex_summary['total_available_kw'],
                flexibility_reserved_kw=0.0,
                flexibility_dispatched_kw=flex_dispatched,
                deficit_kw=controlled_deficit,
                controlled_net_demand_kw=effective_net_demand
            )
            records.append(record)
            
            battery_history.append({
                'timestamp': ts,
                'soc': battery.soc,
                'action': battery.action.value,
                'power_kw': battery.current_power_kw
            })
            
            flexibility_history.append({
                'timestamp': ts,
                'available_kw': flex_summary['total_available_kw'],
                'shifted_kw': flex_summary['total_shifted_kw'],
                'dispatched_kw': flex_dispatched
            })
        
        df = records_to_dataframe(records)
        
        controlled_nd = df['controlled_net_demand_kw'].values
        stress_metrics = Feeder.calculate_stress_metrics(
            controlled_nd, feeder_limit, dt
        )
        
        metrics = SimulationMetrics(
            stress_intervals=stress_metrics['stress_intervals'],
            stress_duration_hours=stress_metrics['stress_duration_hours'],
            deficit_energy_kwh=stress_metrics['deficit_energy_kwh'],
            max_deficit_kw=stress_metrics['max_deficit_kw'],
            avg_deficit_kw=stress_metrics['avg_deficit_kw'],
            stress_percentage=stress_metrics['stress_percentage'],
            peak_net_demand_kw=stress_metrics['peak_net_demand_kw'],
            peak_demand_kw=float(df['demand_kw'].max()),
            total_renewable_kwh=float(df['renewable_kw'].sum() * dt),
            battery_throughput_kwh=battery.throughput_kwh,
            flexibility_events=flex_manager.flexibility_events,
            shifted_energy_kwh=flex_manager.total_shifted_energy_kwh,
            min_battery_soc=battery.min_soc_reached,
            max_battery_soc=battery.max_soc_reached
        )
        
        return ScenarioResult(
            name='Reactive',
            dataframe=df,
            metrics=metrics,
            controller_events=events,
            battery_history=battery_history,
            flexibility_history=flexibility_history
        )


class PredictiveController:
    """Predictive FlexProof controller.
    
    1. Reads current feeder telemetry
    2. Generates demand and renewable forecasts across horizon
    3. Predicts upcoming feeder stress events
    4. Reserves community battery energy
    5. Pre-shifts flexible loads in advance of response time lags
    6. Smoothly dispatches battery and load flexibility during stress
    7. Restores deferred energy strictly during safe off-peak hours
    """
    
    def __init__(self, config):
        self.config = config
        self.feeder = Feeder(
            config.feeder.firm_limit_kw,
            config.feeder.warning_threshold,
            config.feeder.watch_threshold
        )
    
    def run(self, data_source: DataSource) -> ScenarioResult:
        """Run predictive FlexProof simulation."""
        demand_df = data_source.get_demand()
        renewable_df = data_source.get_renewable()
        timestamps = data_source.get_timestamps()
        dt = self.config.simulation.resolution_minutes / 60.0
        n = len(timestamps)
        hours = np.array([(t.hour + t.minute / 60) for t in timestamps])
        feeder_limit = self.config.feeder.firm_limit_kw
        
        battery = CommunityBattery(
            capacity_kwh=self.config.battery.capacity_kwh,
            max_charge_power_kw=self.config.battery.max_charge_power_kw,
            max_discharge_power_kw=self.config.battery.max_discharge_power_kw,
            min_soc=self.config.battery.min_soc,
            max_soc=self.config.battery.max_soc,
            initial_soc=self.config.battery.initial_soc,
            charge_efficiency=self.config.battery.charge_efficiency,
            discharge_efficiency=self.config.battery.discharge_efficiency
        )
        flex_manager = FlexibleLoadManager(self.config.flexible_loads)
        coordinator = FlexibilityCoordinator(battery, flex_manager, dt)
        forecasting = ForecastingEngine(self.config)
        stress_engine = StressPredictionEngine(
            feeder_limit,
            self.config.stress.risk_thresholds.watch,
            self.config.stress.risk_thresholds.warning,
            self.config.stress.risk_thresholds.critical
        )
        
        demand_values = demand_df['total_kw'].values
        renewable_values = renewable_df['solar_kw'].values
        
        records = []
        events = []
        battery_history = []
        flexibility_history = []
        
        lookback = max(96, self.config.forecasting.lookback_intervals)
        
        for i in range(n):
            ts = timestamps[i]
            h = hours[i]
            demand_kw = float(demand_values[i])
            renewable_kw = float(renewable_values[i])
            net_demand_kw = demand_kw - renewable_kw
            
            battery.set_idle()
            flex_manager.update_interval(i)
            active_reduction = flex_manager.get_active_reduction(i)
            
            # 1. Safe restoration during off-peak night (00:00 to 05:30)
            is_safe_window = (h < 5.5 or h >= 23.0)
            restoration_power = flex_manager.get_restoration_power(
                i, is_safe_window=is_safe_window, max_safe_restore_kw=60.0
            )
            effective_net_demand = net_demand_kw - active_reduction + restoration_power
            
            # 2. Forecasting & Stress Prediction
            forecast_demand = demand_kw
            forecast_renewable = renewable_kw
            forecast_net = net_demand_kw
            forecast_gap = 0.0
            stress_predicted = False
            max_gap = 0.0
            time_to_stress = self.config.forecasting.horizon_intervals
            risk_level = RiskLevel.NORMAL
            
            if i >= lookback:
                d_hist = demand_values[i - lookback:i]
                r_hist = renewable_values[i - lookback:i]
                fc = forecasting.forecast(d_hist, r_hist, horizon=self.config.forecasting.horizon_intervals)
                
                if i > 0:
                    forecasting.update_errors(fc.forecast_demand_kw[0], demand_kw, is_demand=True)
                    forecasting.update_errors(fc.forecast_renewable_kw[0], renewable_kw, is_demand=False)
                
                forecast_demand = float(fc.forecast_demand_kw[0])
                forecast_renewable = float(fc.forecast_renewable_kw[0])
                forecast_net = float(fc.forecast_net_demand_kw[0])
                forecast_gap = float(fc.forecast_gap_kw[0])
                
                sp = stress_engine.predict_stress(fc)
                stress_predicted = sp['stress_predicted']
                max_gap = sp['max_gap_kw']
                time_to_stress = sp['time_to_stress_intervals']
                risk_level = sp['max_risk']
            
            # 3. Off-peak / Solar charging (only when no stress is imminent)
            if not stress_predicted:
                if renewable_kw > demand_kw:
                    surplus = renewable_kw - demand_kw
                    c_res = coordinator.handle_charging(surplus, ts)
                    events.extend(c_res['events'])
                elif h < 5.5 or (10.5 <= h < 14.5 and effective_net_demand < 0.50 * feeder_limit):
                    headroom = max(0.0, 0.55 * feeder_limit - effective_net_demand)
                    c_res = coordinator.handle_charging(headroom, ts)
                    effective_net_demand += c_res['charged_kw']
                    events.extend(c_res['events'])
            
            # 4. PREDICTIVE PREPARATION: Reserve battery and pre-shift loads
            flex_reserved = 0.0
            flex_dispatched = active_reduction
            
            if stress_predicted and max_gap > 0:
                prep_res = coordinator.prepare_for_stress(max_gap, time_to_stress, i, ts)
                events.extend(prep_res['events'])
                flex_reserved = flex_manager.get_summary()['total_reserved_kw']
                
                # Update active reduction with lead time
                new_active_red = flex_manager.get_active_reduction(i)
                effective_net_demand = net_demand_kw - new_active_red + restoration_power
                flex_dispatched = new_active_red
            
            # 5. DISPATCH ON ACTUAL / RESIDUAL STRESS
            if effective_net_demand > feeder_limit:
                deficit = effective_net_demand - feeder_limit
                shifted_kw, _ = flex_manager.shift_load(deficit, i, duration_intervals=8)
                
                new_active_red = flex_manager.get_active_reduction(i)
                effective_net_demand = net_demand_kw - new_active_red + restoration_power
                flex_dispatched = new_active_red
                
                if effective_net_demand > feeder_limit:
                    rem_deficit = effective_net_demand - feeder_limit
                    actual_bat, _ = battery.discharge(rem_deficit, dt)
                    effective_net_demand -= actual_bat
                    flex_dispatched += actual_bat
                    
                    if actual_bat > 0:
                        events.append(ControllerEvent(
                            timestamp=ts,
                            decision="Battery predictive dispatch",
                            reason=f"Mitigating residual deficit of {rem_deficit:.1f} kW",
                            predicted_gap_kw=deficit,
                            required_flexibility_kw=rem_deficit,
                            resource_selected="community_battery",
                            power_requested_kw=rem_deficit,
                            power_delivered_kw=actual_bat,
                            battery_soc_before=battery.soc + actual_bat * dt / battery.discharge_efficiency / battery.capacity_kwh,
                            battery_soc_after=battery.soc
                        ))
            
            controlled_deficit = max(0.0, effective_net_demand - feeder_limit)
            flex_summary = flex_manager.get_summary()
            
            record = IntervalRecord(
                timestamp=ts,
                demand_kw=demand_kw,
                renewable_kw=renewable_kw,
                net_demand_kw=net_demand_kw,
                forecast_demand_kw=forecast_demand,
                forecast_renewable_kw=forecast_renewable,
                forecast_net_demand_kw=forecast_net,
                forecast_gap_kw=forecast_gap,
                stress=effective_net_demand > feeder_limit,
                risk_level=risk_level.value if isinstance(risk_level, RiskLevel) else str(risk_level),
                battery_soc=battery.soc,
                battery_action=battery.action.value,
                flexibility_available_kw=flex_summary['total_available_kw'],
                flexibility_reserved_kw=flex_reserved,
                flexibility_dispatched_kw=flex_dispatched,
                deficit_kw=controlled_deficit,
                controlled_net_demand_kw=effective_net_demand
            )
            records.append(record)
            
            battery_history.append({
                'timestamp': ts,
                'soc': battery.soc,
                'action': battery.action.value,
                'power_kw': battery.current_power_kw
            })
            
            flexibility_history.append({
                'timestamp': ts,
                'available_kw': flex_summary['total_available_kw'],
                'reserved_kw': flex_summary['total_reserved_kw'],
                'shifted_kw': flex_summary['total_shifted_kw'],
                'dispatched_kw': flex_dispatched
            })
        
        df = records_to_dataframe(records)
        
        controlled_nd = df['controlled_net_demand_kw'].values
        stress_metrics = Feeder.calculate_stress_metrics(
            controlled_nd, feeder_limit, dt
        )
        
        forecast_metrics = forecasting.get_forecast_metrics()
        
        metrics = SimulationMetrics(
            stress_intervals=stress_metrics['stress_intervals'],
            stress_duration_hours=stress_metrics['stress_duration_hours'],
            deficit_energy_kwh=stress_metrics['deficit_energy_kwh'],
            max_deficit_kw=stress_metrics['max_deficit_kw'],
            avg_deficit_kw=stress_metrics['avg_deficit_kw'],
            stress_percentage=stress_metrics['stress_percentage'],
            peak_net_demand_kw=stress_metrics['peak_net_demand_kw'],
            peak_demand_kw=float(df['demand_kw'].max()),
            total_renewable_kwh=float(df['renewable_kw'].sum() * dt),
            battery_throughput_kwh=battery.throughput_kwh,
            flexibility_events=flex_manager.flexibility_events,
            shifted_energy_kwh=flex_manager.total_shifted_energy_kwh,
            min_battery_soc=battery.min_soc_reached,
            max_battery_soc=battery.max_soc_reached,
            forecast_mae=forecast_metrics.get('overall_mae', 0.0),
            forecast_rmse=forecast_metrics.get('overall_rmse', 0.0)
        )
        
        return ScenarioResult(
            name='Predictive FlexProof',
            dataframe=df,
            metrics=metrics,
            controller_events=events,
            battery_history=battery_history,
            flexibility_history=flexibility_history,
            forecast_metrics=forecast_metrics
        )
