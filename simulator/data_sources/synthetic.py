"""Deterministic synthetic data source for FlexProof.

Generates realistic Indian neighbourhood feeder load profiles,
solar PV generation with cloud disturbances, and flexible load fleet baselines.
"""
import numpy as np
import pandas as pd
from .base import DataSource


class SyntheticDataSource(DataSource):
    """Generates deterministic synthetic feeder data for Indian distribution network."""
    
    def __init__(self, config):
        """Initialize with FlexProofConfig."""
        self._config = config
        self._rng = np.random.RandomState(config.simulation.random_seed)
        self._timestamps = None
        self._demand = None
        self._renewable = None
        self._flex_profiles = None
        self._generate_all()
    
    def _generate_all(self):
        """Generate all data deterministically."""
        self._generate_timestamps()
        self._generate_demand()
        self._generate_renewable()
        self._generate_flexible_load_profiles()
    
    def _generate_timestamps(self):
        """Generate time index for 30 days at 15-minute resolution."""
        self._timestamps = pd.date_range(
            start='2024-01-01',
            periods=self._config.simulation.intervals,
            freq=f'{self._config.simulation.resolution_minutes}min'
        )
    
    def _generate_demand(self):
        """Generate realistic Indian residential + commercial + industrial demand."""
        n = self._config.simulation.intervals
        hours = np.array([(t.hour + t.minute / 60) for t in self._timestamps])
        day_of_week = np.array([t.dayofweek for t in self._timestamps])
        n_days = self._config.simulation.duration_days
        intervals_per_day = int(24 * 60 / self._config.simulation.resolution_minutes)
        
        # Daily temperature/weather variation factor across 30 days (0.90 to 1.10)
        daily_temp_factor = 0.90 + 0.20 * self._rng.random(n_days)
        daily_temp_expanded = np.repeat(daily_temp_factor, intervals_per_day)[:n]
        
        # 1. RESIDENTIAL demand pattern (Indian household with evening peak)
        # Night base (00:00-05:00), morning rise (05:00-09:00), daytime moderate (09:00-16:00),
        # evening cooking/lighting/cooling peak (18:00-21:30), late night drop (21:30-24:00)
        res_base = np.zeros(n)
        for i in range(n):
            h = hours[i]
            if h < 5:
                b = 0.25
            elif h < 7:
                b = 0.25 + 0.45 * (h - 5) / 2
            elif h < 9:
                b = 0.70 + 0.10 * (h - 7) / 2
            elif h < 16:
                b = 0.50
            elif h < 17.5:
                b = 0.50 + 0.30 * (h - 16) / 1.5
            elif h < 19:
                b = 0.80 + 0.20 * (h - 17.5) / 1.5
            elif h < 21.5:
                b = 1.00 - 0.05 * ((h - 20.0)**2)
            elif h < 23:
                b = 0.88 - 0.53 * (h - 21.5) / 1.5
            else:
                b = 0.35 - 0.10 * (h - 23)
            res_base[i] = b
        
        # Weekend residential slight boost
        weekend_boost = np.where((day_of_week >= 5), 0.05, 0.0)
        residential = (res_base + weekend_boost) * daily_temp_expanded * self._config.demand.residential_peak_kw
        residential += self._rng.normal(0, self._config.demand.noise_std * self._config.demand.residential_peak_kw, n)
        residential = np.maximum(residential, 50.0)
        
        # 2. COMMERCIAL demand pattern (markets, offices, shops)
        com_base = np.zeros(n)
        for i in range(n):
            h = hours[i]
            dow = day_of_week[i]
            if dow >= 6:  # Sunday (reduced market activity)
                b = 0.35 if 10 <= h < 20 else 0.12
            elif dow >= 5:  # Saturday (partial commercial)
                b = 0.60 if 9 <= h < 19 else 0.15
            else:  # Weekday
                if h < 7:
                    b = 0.12
                elif h < 9:
                    b = 0.12 + 0.70 * (h - 7) / 2  # Morning opening
                elif h < 12:
                    b = 0.88
                elif h < 14:
                    b = 0.82  # Lunch dip
                elif h < 17:
                    b = 0.92  # Afternoon peak (AC + commercial)
                elif h < 19.5:
                    b = 0.92 - 0.45 * (h - 17) / 2.5
                elif h < 21.5:
                    b = 0.47 - 0.25 * (h - 19.5) / 2
                else:
                    b = 0.22
            com_base[i] = b
        
        commercial = com_base * self._config.demand.commercial_peak_kw
        commercial += self._rng.normal(0, self._config.demand.noise_std * self._config.demand.commercial_peak_kw, n)
        commercial = np.maximum(commercial, 20.0)
        
        # 3. INDUSTRIAL demand pattern (workshops, small manufacturing)
        ind_base = np.zeros(n)
        for i in range(n):
            h = hours[i]
            if h < 6:
                b = 0.65
            elif h < 8:
                b = 0.65 + 0.25 * (h - 6) / 2
            elif h < 19:
                b = 0.90
            elif h < 21.5:
                b = 0.90 - 0.20 * (h - 19) / 2.5
            else:
                b = 0.70
            ind_base[i] = b
        
        ind_weekend = np.where((day_of_week >= 6), -0.15, 0.0)
        industrial = (ind_base + ind_weekend) * self._config.demand.industrial_peak_kw
        industrial += self._rng.normal(0, self._config.demand.noise_std * self._config.demand.industrial_peak_kw, n)
        industrial = np.maximum(industrial, 50.0)
        
        total = residential + commercial + industrial
        
        self._demand = pd.DataFrame({
            'residential_kw': residential,
            'commercial_kw': commercial,
            'industrial_kw': industrial,
            'total_kw': total
        }, index=self._timestamps)
    
    def _generate_renewable(self):
        """Generate realistic solar generation for Indian conditions."""
        n = self._config.simulation.intervals
        hours = np.array([(t.hour + t.minute / 60) for t in self._timestamps])
        n_days = self._config.simulation.duration_days
        intervals_per_day = int(24 * 60 / self._config.simulation.resolution_minutes)
        
        # Solar envelope: sunrise ~06:00, solar noon ~12:15, sunset ~18:30
        solar = np.zeros(n)
        for i in range(n):
            h = hours[i]
            if h < 6.0 or h > 18.5:
                solar[i] = 0.0
            else:
                solar[i] = np.cos((h - 12.25) / 6.25 * np.pi / 2) ** 1.5
        
        # Cloud disturbances
        cloud_mask = self._rng.random(n) < self._config.renewable.cloud_probability
        cloud_reduction = self._rng.uniform(0.3, 0.8, n)
        solar = np.where(cloud_mask & (solar > 0), solar * cloud_reduction, solar)
        
        # Daily solar irradiance factor (0.85 to 1.00)
        daily_solar_factor = 0.85 + 0.15 * self._rng.random(n_days)
        daily_solar_expanded = np.repeat(daily_solar_factor, intervals_per_day)[:n]
        solar = solar * daily_solar_expanded * self._config.renewable.solar_capacity_kw
        
        # Small noise
        noise = self._rng.normal(0, self._config.renewable.noise_std, n)
        solar = solar + noise * solar
        
        # Physical constraint: non-negative
        solar = np.maximum(solar, 0.0)
        
        max_solar = self._config.renewable.solar_capacity_kw
        irradiance = solar / max_solar if max_solar > 0 else solar
        
        self._renewable = pd.DataFrame({
            'solar_kw': solar,
            'irradiance': irradiance
        }, index=self._timestamps)
    
    def _generate_flexible_load_profiles(self):
        """Generate baseline flexible load profiles for fleet components."""
        n = self._config.simulation.intervals
        hours = np.array([(t.hour + t.minute / 60) for t in self._timestamps])
        flex_config = self._config.flexible_loads
        
        # EV charging - evening concentration when commuters return home
        ev_profile = np.zeros(n)
        for i in range(n):
            h = hours[i]
            if 18 <= h < 23:
                ev_profile[i] = 0.7 + 0.3 * np.sin(np.pi * (h - 18) / 5)
            elif 23 <= h or h < 6:
                ev_profile[i] = 0.25
            elif 8 <= h < 17:
                ev_profile[i] = 0.20
            else:
                ev_profile[i] = 0.15
        ev_total = ev_profile * flex_config.ev_charging.count * flex_config.ev_charging.power_per_unit_kw
        
        # Water pumping - municipal schedules
        wp_profile = np.zeros(n)
        for i in range(n):
            h = hours[i]
            if 5 <= h < 8:
                wp_profile[i] = 0.80
            elif 8 <= h < 16:
                wp_profile[i] = 0.30
            elif 16 <= h < 20:
                wp_profile[i] = 0.70
            else:
                wp_profile[i] = 0.10
        wp_total = wp_profile * flex_config.water_pumping.count * flex_config.water_pumping.power_per_unit_kw
        
        # HVAC - temperature correlated
        hvac_profile = np.zeros(n)
        for i in range(n):
            h = hours[i]
            if 10 <= h < 16:
                hvac_profile[i] = 0.90
            elif 16 <= h < 22:
                hvac_profile[i] = 0.65
            elif 7 <= h < 10:
                hvac_profile[i] = 0.40
            else:
                hvac_profile[i] = 0.20
        hvac_total = hvac_profile * flex_config.hvac.count * flex_config.hvac.power_per_unit_kw
        
        # Commercial refrigeration - steady with small thermal cycle
        cr_profile = 0.70 + 0.30 * np.sin(2 * np.pi * hours / 24)
        cr_total = cr_profile * flex_config.commercial_refrigeration.count * flex_config.commercial_refrigeration.power_per_unit_kw
        
        # Agricultural pumping - daytime / early morning
        ap_profile = np.zeros(n)
        for i in range(n):
            h = hours[i]
            if 6 <= h < 10:
                ap_profile[i] = 0.80
            elif 15 <= h < 18:
                ap_profile[i] = 0.70
            else:
                ap_profile[i] = 0.05
        ap_total = ap_profile * flex_config.agricultural_pumping.count * flex_config.agricultural_pumping.power_per_unit_kw
        
        # Add controlled noise
        ev_total = np.maximum(ev_total + self._rng.normal(0, 1.5, n), 0.0)
        wp_total = np.maximum(wp_total + self._rng.normal(0, 2.0, n), 0.0)
        hvac_total = np.maximum(hvac_total + self._rng.normal(0, 1.0, n), 0.0)
        cr_total = np.maximum(cr_total + self._rng.normal(0, 0.8, n), 0.0)
        ap_total = np.maximum(ap_total + self._rng.normal(0, 1.5, n), 0.0)
        
        self._flex_profiles = pd.DataFrame({
            'ev_charging_kw': ev_total,
            'water_pumping_kw': wp_total,
            'hvac_kw': hvac_total,
            'commercial_refrigeration_kw': cr_total,
            'agricultural_pumping_kw': ap_total
        }, index=self._timestamps)
    
    def get_timestamps(self) -> pd.DatetimeIndex:
        return self._timestamps
    
    def get_demand(self) -> pd.DataFrame:
        return self._demand.copy()
    
    def get_renewable(self) -> pd.DataFrame:
        return self._renewable.copy()
    
    def get_flexible_load_profiles(self) -> pd.DataFrame:
        return self._flex_profiles.copy()
    
    @property
    def num_intervals(self) -> int:
        return self._config.simulation.intervals
    
    @property
    def resolution_minutes(self) -> int:
        return self._config.simulation.resolution_minutes
