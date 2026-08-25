"""Flexible load management for FlexProof.

Manages EV charging, water pumping, HVAC, commercial refrigeration,
and agricultural pumping as flexible demand resources.

CRITICAL: Load shifting is strictly energy-conserving.
When a fleet shifts power for a given duration, that reduction remains active
across all intervals of the shift window (accounting for resource response time lags).
All deferred energy is restored during safe off-peak / valley hours.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import numpy as np
from models.schemas import FlexibleResource, ResourceType, ResourceStatus


@dataclass
class ShiftRecord:
    """Tracks an active or completed load shift."""
    resource_id: str
    resource_type: ResourceType
    power_kw: float
    start_interval: int
    duration_intervals: int
    response_time_intervals: int
    energy_kwh: float


class FlexibleLoadManager:
    """Manages flexible load resources for demand flexibility.
    
    Handles:
    - Resource registration and availability tracking
    - Continuous duration load shifting with response-time modeling
    - Strict energy conservation tracking
    - Safe-window load restoration during off-peak hours
    """
    
    def __init__(self, config):
        """Initialize with FlexibleLoadsConfig."""
        self.resources: List[FlexibleResource] = []
        self.active_shifts: List[ShiftRecord] = []
        self.total_shifted_energy_kwh = 0.0
        self.total_restored_energy_kwh = 0.0
        self.flexibility_events = 0
        self._dt_hours = 0.25
        self._config = config
        
        self._initialize_resources(config)
    
    def _initialize_resources(self, config):
        """Create flexible resources from configuration."""
        load_types = [
            ('hvac', ResourceType.HVAC, config.hvac),
            ('ev_charging', ResourceType.EV_CHARGING, config.ev_charging),
            ('water_pumping', ResourceType.WATER_PUMPING, config.water_pumping),
            ('agricultural_pumping', ResourceType.AGRICULTURAL_PUMPING, config.agricultural_pumping),
            ('commercial_refrigeration', ResourceType.COMMERCIAL_REFRIGERATION, config.commercial_refrigeration),
        ]
        
        for type_name, resource_type, type_config in load_types:
            total_power = type_config.count * type_config.power_per_unit_kw
            available_power = total_power * type_config.flexibility_fraction
            max_duration = type_config.max_shift_intervals
            available_energy = available_power * max_duration * self._dt_hours
            
            resource = FlexibleResource(
                resource_id=f"{type_name}_fleet",
                resource_type=resource_type,
                baseline_power_kw=total_power,
                available_power_kw=available_power,
                available_energy_kwh=available_energy,
                minimum_duration=type_config.min_shift_intervals,
                maximum_duration=type_config.max_shift_intervals,
                response_time=type_config.response_time_intervals,
                availability=type_config.flexibility_fraction,
                priority=type_config.priority
            )
            self.resources.append(resource)
    
    def get_active_reduction(self, current_interval: int) -> float:
        """Calculate the total active power reduction at current_interval across all shifts.
        
        Takes into account each shift's response-time lag.
        """
        reductions_by_resource: Dict[str, float] = {}
        for s in self.active_shifts:
            if s.start_interval <= current_interval < s.start_interval + s.duration_intervals:
                # Active only after response time lag has elapsed
                if current_interval >= s.start_interval + s.response_time_intervals:
                    reductions_by_resource[s.resource_id] = (
                        reductions_by_resource.get(s.resource_id, 0.0) + s.power_kw
                    )
        
        total_reduction = 0.0
        for r in self.resources:
            r_active = reductions_by_resource.get(r.resource_id, 0.0)
            capped = min(r_active, r.available_power_kw)
            total_reduction += capped
            
            # Update live resource status
            if capped > 0:
                r.status = ResourceStatus.SHIFTED
            elif r.status == ResourceStatus.SHIFTED:
                r.status = ResourceStatus.AVAILABLE
                
        return total_reduction
    
    def get_available_flexibility(self, current_interval: int) -> float:
        """Get remaining unshifted flexibility power (kW)."""
        active_by_res: Dict[str, float] = {}
        for s in self.active_shifts:
            if s.start_interval <= current_interval < s.start_interval + s.duration_intervals:
                active_by_res[s.resource_id] = active_by_res.get(s.resource_id, 0.0) + s.power_kw
        
        total_avail = 0.0
        for r in self.resources:
            used = active_by_res.get(r.resource_id, 0.0)
            total_avail += max(0.0, r.available_power_kw - used)
        return total_avail
    
    def shift_load(self, required_kw: float, current_interval: int,
                   duration_intervals: int = 8) -> Tuple[float, List[Dict]]:
        """Shift/defer flexible loads for a continuous duration.
        
        Args:
            required_kw: Power reduction needed (kW)
            current_interval: Current simulation interval
            duration_intervals: Number of intervals to maintain reduction
            
        Returns:
            Tuple of (total_shifted_kw, list of action dicts)
        """
        active_by_res: Dict[str, float] = {}
        for s in self.active_shifts:
            if s.start_interval <= current_interval < s.start_interval + s.duration_intervals:
                active_by_res[s.resource_id] = active_by_res.get(s.resource_id, 0.0) + s.power_kw
        
        shifted_total = 0.0
        actions = []
        rem = required_kw
        
        # Sort by priority
        sorted_resources = sorted(self.resources, key=lambda r: r.priority)
        
        for r in sorted_resources:
            if rem <= 0:
                break
            currently_used = active_by_res.get(r.resource_id, 0.0)
            can_shift = max(0.0, r.available_power_kw - currently_used)
            
            if can_shift > 0.1:
                pwr = min(rem, can_shift)
                dur = min(max(duration_intervals, r.minimum_duration), r.maximum_duration)
                energy = pwr * dur * self._dt_hours
                
                shift_rec = ShiftRecord(
                    resource_id=r.resource_id,
                    resource_type=r.resource_type,
                    power_kw=pwr,
                    start_interval=current_interval,
                    duration_intervals=dur,
                    response_time_intervals=r.response_time,
                    energy_kwh=energy
                )
                self.active_shifts.append(shift_rec)
                self.total_shifted_energy_kwh += energy
                self.flexibility_events += 1
                r.status = ResourceStatus.SHIFTED
                
                shifted_total += pwr
                rem -= pwr
                
                actions.append({
                    'resource_id': r.resource_id,
                    'resource_type': r.resource_type.value,
                    'action': 'SHIFT',
                    'power_kw': pwr,
                    'energy_kwh': energy,
                    'duration_intervals': dur,
                    'response_time_intervals': r.response_time
                })
        
        return shifted_total, actions
    
    def reserve_resources(self, required_kw: float, current_interval: int) -> float:
        """Mark available resources as RESERVED for upcoming stress."""
        reserved = 0.0
        for r in sorted(self.resources, key=lambda r: r.priority):
            if r.status == ResourceStatus.AVAILABLE and reserved < required_kw:
                r.status = ResourceStatus.RESERVED
                reserved += r.available_power_kw
        return reserved
    
    def get_restoration_power(self, current_interval: int, 
                              is_safe_window: bool = False,
                              max_safe_restore_kw: float = 60.0) -> float:
        """Restore deferred energy gradually during safe off-peak hours."""
        if not is_safe_window:
            return 0.0
        
        needed_energy = self.total_shifted_energy_kwh - self.total_restored_energy_kwh
        if needed_energy <= 1e-4:
            return 0.0
        
        pwr = min(needed_energy / self._dt_hours, max_safe_restore_kw)
        self.total_restored_energy_kwh += pwr * self._dt_hours
        return pwr
    
    def update_interval(self, current_interval: int):
        """Clean expired shifts and update states."""
        self.active_shifts = [
            s for s in self.active_shifts
            if current_interval < s.start_interval + s.duration_intervals
        ]
        active_ids = {s.resource_id for s in self.active_shifts}
        for r in self.resources:
            if r.resource_id not in active_ids and r.status == ResourceStatus.SHIFTED:
                r.status = ResourceStatus.AVAILABLE
    
    def reset(self):
        """Reset all state."""
        self.active_shifts.clear()
        self.total_shifted_energy_kwh = 0.0
        self.total_restored_energy_kwh = 0.0
        self.flexibility_events = 0
        for r in self.resources:
            r.status = ResourceStatus.AVAILABLE
            r.shifted_energy_kwh = 0.0
            r.shift_remaining_intervals = 0
    
    def get_summary(self) -> Dict:
        """Get resource fleet status summary."""
        total_available = sum(r.available_power_kw for r in self.resources if r.status in (ResourceStatus.AVAILABLE, ResourceStatus.RESERVED))
        total_shifted = sum(r.available_power_kw for r in self.resources if r.status == ResourceStatus.SHIFTED)
        
        return {
            'total_available_kw': total_available,
            'total_reserved_kw': sum(r.available_power_kw for r in self.resources if r.status == ResourceStatus.RESERVED),
            'total_shifted_kw': total_shifted,
            'total_resources': len(self.resources),
            'flexibility_events': self.flexibility_events,
            'total_shifted_energy_kwh': self.total_shifted_energy_kwh,
            'total_restored_energy_kwh': self.total_restored_energy_kwh
        }
