"""Flexibility coordination engine for FlexProof.

Coordinates flexible loads and community battery storage to provide
demand flexibility for feeder stress management and off-peak charging.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from models.schemas import (
    BatteryAction, ResourceStatus, ControllerEvent,
    RiskLevel
)
from .battery import CommunityBattery
from .flexible_loads import FlexibleLoadManager


class FlexibilityCoordinator:
    """Coordinates flexibility resources for feeder stress management.
    
    Manages the interaction between flexible loads and battery
    storage, applying dispatch priority rules and off-peak charging.
    """
    
    def __init__(self, battery: CommunityBattery, 
                 flex_manager: FlexibleLoadManager,
                 dt_hours: float = 0.25):
        self.battery = battery
        self.flex_manager = flex_manager
        self.dt_hours = dt_hours
    
    def dispatch_for_stress(self, deficit_kw: float, 
                            current_interval: int,
                            risk_level: RiskLevel,
                            timestamp=None) -> Dict:
        """Dispatch flexibility resources to mitigate an active deficit.
        
        Priority order:
        1. Flexible loads (shift/defer)
        2. Community Battery discharge
        
        Args:
            deficit_kw: Power deficit to cover (kW)
            current_interval: Current simulation interval
            risk_level: Current risk level
            timestamp: Current timestamp for event logging
            
        Returns:
            Dict with dispatch results
        """
        events = []
        remaining_deficit = deficit_kw
        total_flex_kw = 0.0
        total_battery_kw = 0.0
        flex_actions = []
        battery_soc_before = self.battery.soc
        
        # Step 1: Shift flexible loads
        if remaining_deficit > 0.1:
            shifted_kw, actions = self.flex_manager.shift_load(
                remaining_deficit, current_interval, duration_intervals=8
            )
            total_flex_kw = shifted_kw
            flex_actions = actions
            remaining_deficit -= shifted_kw
            
            if shifted_kw > 0 and timestamp is not None:
                for action in actions:
                    events.append(ControllerEvent(
                        timestamp=timestamp,
                        decision=f"{action['resource_type']} shifted",
                        reason=f"Feeder stress - deficit {deficit_kw:.1f} kW",
                        predicted_gap_kw=deficit_kw,
                        required_flexibility_kw=deficit_kw,
                        resource_selected=action['resource_id'],
                        power_requested_kw=action['power_kw'],
                        power_delivered_kw=action['power_kw'],
                        battery_soc_before=battery_soc_before,
                        battery_soc_after=self.battery.soc
                    ))
        
        # Step 2: Battery discharge for remaining deficit
        if remaining_deficit > 0.1 and self.battery.available_energy_kwh > 0:
            actual_power, energy_consumed = self.battery.discharge(
                remaining_deficit, self.dt_hours
            )
            total_battery_kw = actual_power
            remaining_deficit -= actual_power
            
            if actual_power > 0 and timestamp is not None:
                events.append(ControllerEvent(
                    timestamp=timestamp,
                    decision="Battery discharge initiated",
                    reason=f"Dispatched {actual_power:.1f} kW to mitigate residual deficit",
                    predicted_gap_kw=deficit_kw,
                    required_flexibility_kw=deficit_kw,
                    resource_selected="community_battery",
                    power_requested_kw=remaining_deficit + actual_power,
                    power_delivered_kw=actual_power,
                    battery_soc_before=battery_soc_before,
                    battery_soc_after=self.battery.soc
                ))
        
        return {
            'total_flexibility_kw': total_flex_kw + total_battery_kw,
            'flex_shifted_kw': total_flex_kw,
            'battery_discharged_kw': total_battery_kw,
            'remaining_deficit_kw': max(0.0, remaining_deficit),
            'flex_actions': flex_actions,
            'events': events,
            'battery_soc_after': self.battery.soc
        }
    
    def prepare_for_stress(self, predicted_gap_kw: float,
                           time_to_stress: int,
                           current_interval: int,
                           timestamp=None) -> Dict:
        """Prepare resources for predicted upcoming stress.
        
        Called by predictive controller to:
        1. Reserve battery energy
        2. Pre-shift deferrable loads before response time lags
        
        Args:
            predicted_gap_kw: Maximum predicted deficit (kW)
            time_to_stress: Intervals until stress
            current_interval: Current simulation interval
            timestamp: Current timestamp
            
        Returns:
            Dict with preparation results
        """
        events = []
        battery_soc_before = self.battery.soc
        
        # Reserve battery energy
        if self.battery.available_energy_kwh > 0:
            self.battery.set_reserved()
            if timestamp is not None:
                events.append(ControllerEvent(
                    timestamp=timestamp,
                    decision="Battery reserve created",
                    reason=f"Predicted stress in {time_to_stress * 15} min, gap {predicted_gap_kw:.1f} kW",
                    predicted_gap_kw=predicted_gap_kw,
                    required_flexibility_kw=predicted_gap_kw,
                    resource_selected="community_battery",
                    power_requested_kw=0.0,
                    power_delivered_kw=0.0,
                    battery_soc_before=battery_soc_before,
                    battery_soc_after=self.battery.soc
                ))
        
        # Pre-shift deferrable loads (e.g. water pumping, EV, agricultural)
        pre_shifted_kw = 0.0
        if time_to_stress <= 3 and predicted_gap_kw > 0:
            shifted_kw, actions = self.flex_manager.shift_load(
                predicted_gap_kw, current_interval, duration_intervals=8
            )
            pre_shifted_kw = shifted_kw
            if pre_shifted_kw > 0 and timestamp is not None:
                for action in actions:
                    events.append(ControllerEvent(
                        timestamp=timestamp,
                        decision=f"Pre-shift: {action['resource_type']}",
                        reason=f"Upcoming stress in {time_to_stress * 15} min (lead time preparation)",
                        predicted_gap_kw=predicted_gap_kw,
                        required_flexibility_kw=predicted_gap_kw,
                        resource_selected=action['resource_id'],
                        power_requested_kw=action['power_kw'],
                        power_delivered_kw=action['power_kw'],
                        battery_soc_before=battery_soc_before,
                        battery_soc_after=self.battery.soc
                    ))
        
        return {
            'reserved_battery': self.battery.action == BatteryAction.RESERVED,
            'pre_shifted_kw': pre_shifted_kw,
            'events': events
        }
    
    def handle_charging(self, available_headroom_kw: float, timestamp=None) -> Dict:
        """Handle battery charging during off-peak or solar surplus hours."""
        events = []
        battery_soc_before = self.battery.soc
        
        if available_headroom_kw > 10.0 and self.battery.soc < self.battery.max_soc:
            request_power = min(available_headroom_kw, self.battery.max_charge_power_kw)
            actual_power, stored_energy = self.battery.charge(
                request_power, self.dt_hours
            )
            
            return {
                'charged_kw': actual_power,
                'stored_kwh': stored_energy,
                'events': events
            }
        
        return {'charged_kw': 0.0, 'stored_kwh': 0.0, 'events': events}
