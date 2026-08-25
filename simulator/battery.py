"""Community battery storage model for FlexProof.

Implements a physically consistent battery model with:
- State of charge (SOC) tracking
- Charge/discharge efficiency losses
- Power and energy capacity limits
- SOC floor/ceiling enforcement
"""
import numpy as np
from typing import Tuple
from models.schemas import BatteryState, BatteryAction


class CommunityBattery:
    """Community battery storage system.
    
    Physical model with correct energy accounting.
    SOC is tracked as a fraction [0, 1].
    
    Args:
        capacity_kwh: Total battery capacity (kWh)
        max_charge_power_kw: Maximum charging power (kW)
        max_discharge_power_kw: Maximum discharging power (kW)
        min_soc: Minimum allowed SOC (fraction)
        max_soc: Maximum allowed SOC (fraction)
        initial_soc: Starting SOC (fraction)
        charge_efficiency: Charging efficiency (fraction, e.g., 0.95)
        discharge_efficiency: Discharging efficiency (fraction, e.g., 0.95)
    """
    
    def __init__(self, capacity_kwh: float = 500,
                 max_charge_power_kw: float = 150,
                 max_discharge_power_kw: float = 150,
                 min_soc: float = 0.50,
                 max_soc: float = 0.90,
                 initial_soc: float = 0.70,
                 charge_efficiency: float = 0.95,
                 discharge_efficiency: float = 0.95):
        if min_soc >= max_soc:
            raise ValueError(f"min_soc ({min_soc}) must be less than max_soc ({max_soc})")
        if not (0 <= initial_soc <= 1):
            raise ValueError(f"initial_soc ({initial_soc}) must be between 0 and 1")
        
        self.capacity_kwh = capacity_kwh
        self.max_charge_power_kw = max_charge_power_kw
        self.max_discharge_power_kw = max_discharge_power_kw
        self.min_soc = min_soc
        self.max_soc = max_soc
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency
        
        self.soc = initial_soc
        self.initial_soc = initial_soc
        self.action = BatteryAction.IDLE
        self.current_power_kw = 0.0
        
        # Tracking
        self.total_charged_kwh = 0.0
        self.total_discharged_kwh = 0.0
        self.min_soc_reached = initial_soc
        self.max_soc_reached = initial_soc
    
    @property
    def energy_kwh(self) -> float:
        """Current stored energy (kWh)."""
        return self.soc * self.capacity_kwh
    
    @property
    def available_energy_kwh(self) -> float:
        """Energy available for discharge above min_soc (kWh)."""
        return max(0.0, (self.soc - self.min_soc) * self.capacity_kwh)
    
    @property  
    def available_charge_energy_kwh(self) -> float:
        """Energy capacity available for charging below max_soc (kWh)."""
        return max(0.0, (self.max_soc - self.soc) * self.capacity_kwh)
    
    @property
    def available_discharge_power_kw(self) -> float:
        """Maximum discharge power given current SOC and limits."""
        if self.soc <= self.min_soc:
            return 0.0
        return self.max_discharge_power_kw
    
    @property
    def available_charge_power_kw(self) -> float:
        """Maximum charge power given current SOC and limits."""
        if self.soc >= self.max_soc:
            return 0.0
        return self.max_charge_power_kw
    
    def charge(self, power_kw: float, dt_hours: float = 0.25) -> Tuple[float, float]:
        """Charge the battery.
        
        Args:
            power_kw: Requested charging power (kW), positive value
            dt_hours: Duration of time step (hours)
            
        Returns:
            Tuple of (actual_power_kw, energy_stored_kwh)
            actual_power_kw is the grid-side power consumed
            energy_stored_kwh is what actually goes into the battery
        """
        if power_kw <= 0 or self.soc >= self.max_soc:
            return 0.0, 0.0
        
        # Limit to max charge power
        actual_power = min(power_kw, self.max_charge_power_kw)
        
        # Energy at the grid side
        grid_energy = actual_power * dt_hours
        
        # Energy stored in battery (after efficiency loss)
        stored_energy = grid_energy * self.charge_efficiency
        
        # Check if we would exceed max_soc
        max_storable = (self.max_soc - self.soc) * self.capacity_kwh
        if stored_energy > max_storable:
            stored_energy = max_storable
            grid_energy = stored_energy / self.charge_efficiency
            actual_power = grid_energy / dt_hours
        
        # Update SOC
        self.soc += stored_energy / self.capacity_kwh
        self.soc = min(self.soc, self.max_soc)  # Safety clamp
        
        # Update tracking
        self.total_charged_kwh += stored_energy
        self.max_soc_reached = max(self.max_soc_reached, self.soc)
        self.action = BatteryAction.CHARGING
        self.current_power_kw = actual_power
        
        return actual_power, stored_energy
    
    def discharge(self, power_kw: float, dt_hours: float = 0.25) -> Tuple[float, float]:
        """Discharge the battery.
        
        Args:
            power_kw: Requested discharge power (kW), positive value
            dt_hours: Duration of time step (hours)
            
        Returns:
            Tuple of (actual_power_delivered_kw, energy_from_battery_kwh)
            actual_power_delivered_kw is net power delivered to grid
            energy_from_battery_kwh is energy removed from battery
        """
        if power_kw <= 0 or self.soc <= self.min_soc:
            return 0.0, 0.0
        
        # Limit to max discharge power
        actual_power = min(power_kw, self.max_discharge_power_kw)
        
        # Energy removed from battery
        battery_energy = actual_power * dt_hours / self.discharge_efficiency
        
        # Wait - let me reconsider. The power_kw requested is what we want delivered.
        # Battery must provide more internally due to efficiency.
        # Actually, let's think of it as:
        # - We want to deliver `power_kw` to the grid
        # - Battery internally loses energy: energy_from_battery = delivered_energy / efficiency
        # OR
        # - Battery outputs `power_kw` internally, grid receives `power_kw * efficiency`
        # 
        # Convention: power_kw is what we want DELIVERED to grid.
        # Battery must deplete: delivered / efficiency
        
        delivered_energy = actual_power * dt_hours
        battery_energy_consumed = delivered_energy / self.discharge_efficiency
        
        # Check if we have enough energy above min_soc
        available = self.available_energy_kwh
        if battery_energy_consumed > available:
            battery_energy_consumed = available
            delivered_energy = battery_energy_consumed * self.discharge_efficiency
            actual_power = delivered_energy / dt_hours if dt_hours > 0 else 0.0
        
        # Update SOC
        self.soc -= battery_energy_consumed / self.capacity_kwh
        self.soc = max(self.soc, self.min_soc)  # Safety clamp
        
        # Update tracking
        self.total_discharged_kwh += delivered_energy
        self.min_soc_reached = min(self.min_soc_reached, self.soc)
        self.action = BatteryAction.DISCHARGING
        self.current_power_kw = actual_power
        
        return actual_power, battery_energy_consumed
    
    def set_idle(self):
        """Set battery to idle state."""
        self.action = BatteryAction.IDLE
        self.current_power_kw = 0.0
    
    def set_reserved(self):
        """Set battery to reserved state (holding energy for predicted stress)."""
        self.action = BatteryAction.RESERVED
        self.current_power_kw = 0.0
    
    def get_state(self) -> BatteryState:
        """Get current battery state."""
        return BatteryState(
            soc=self.soc,
            energy_kwh=self.energy_kwh,
            available_energy_kwh=self.available_energy_kwh,
            available_power_kw=self.available_discharge_power_kw,
            action=self.action,
            power_kw=self.current_power_kw
        )
    
    def reset(self):
        """Reset battery to initial state."""
        self.soc = self.initial_soc
        self.action = BatteryAction.IDLE
        self.current_power_kw = 0.0
        self.total_charged_kwh = 0.0
        self.total_discharged_kwh = 0.0
        self.min_soc_reached = self.initial_soc
        self.max_soc_reached = self.initial_soc
    
    @property
    def throughput_kwh(self) -> float:
        """Total battery throughput (kWh)."""
        return self.total_charged_kwh + self.total_discharged_kwh
