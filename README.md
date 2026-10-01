# FlexProof — Predictive Neighbourhood Grid Flexibility Platform

> **"Predict feeder stress before it becomes a reliability event."**<br>
> *Developed for the Schneider Electric / Yuva Yodha Energy Tech Hackathon.*

---

## Executive Summary

Modern distribution grid infrastructure at the neighbourhood substation level (11 kV / 415 V) is experiencing accelerating operational strain. The simultaneous growth of residential electric vehicle (EV) charging, distributed rooftop solar PV, and heavy cooling/heating loads creates steep evening net demand ramps. When high domestic demand coincides with the rapid sunset collapse of solar generation, local feeder capacity limits are breached, resulting in thermal overloading, voltage degradation, and accelerated asset ageing.

Traditional distribution automation relies primarily on **reactive threshold control**—initiating curtailment or battery discharge only *after* the firm feeder threshold is breached. However, municipal water pumps, agricultural tube-wells, commercial refrigeration, and community HVAC fleets possess physical response-time latencies (15 to 30 minutes). When control actions are delayed until overloads occur, these slower flexible loads cannot respond in time. As a result, reactive controllers are forced into emergency high-rate battery discharging, rapidly consuming battery cycle life while still leaving unserved energy deficits.

**FlexProof** is an engineering prototype for predictive neighbourhood grid flexibility. By forecasting net feeder demand **1 hour in advance (4 intervals at 15-minute resolution)** from historical telemetry and load patterns, FlexProof shifts grid management from reactive emergency intervention to **coordinated advance preparation**. Slower-acting deferrable loads are pre-shifted with adequate lead time, reserving community battery storage for smooth real-time precision balancing.

---

## The Five-Stage Operating Loop

FlexProof executes a continuous closed-loop control sequence across every 15-minute dispatch interval:

```
Predict ──> Prepare ──> Coordinate ──> Dispatch ──> Learn
```

1. **Predict**: Ingests rolling 24-hour historical telemetry (96 intervals) to generate a multi-lag 1-hour lookahead forecast of net feeder demand without future data leakage.
2. **Prepare**: Scans the lookahead horizon against the firm feeder capacity limit (2,300 kW), detects upcoming capacity deficits, and calculates required flexibility volume.
3. **Coordinate**: Evaluates physical fleet response delays (15–30 min) and schedules slow-acting deferrable loads (water pumping, agricultural wells, EV charging) in advance.
4. **Dispatch**: Coordinates real-time power flows at the feeder level, prioritizing zero-carbon load flexibility and utilizing the community battery strictly as a fine-tuning precision buffer.
5. **Learn**: Tracks online forecast error residuals (MAE / RMSE) after each interval, maintaining bounded risk margins without overfitting.

---

## Validated Simulation Results

All metrics reflect a continuous 30-day simulation benchmark (2,880 intervals at 15-minute resolution) evaluating an Indian neighbourhood distribution feeder under a 2,300 kW firm capacity constraint, 800 kW rooftop solar PV fleet, 500 kWh community battery storage, and 362 kW flexible load pool. The scenario includes 24 synthetic solar intermittency events with a maximum observed solar ramp-down of approximately 285.5 kW.

### Benchmark Comparison (30 Days / 2,880 Intervals)

| Operational Metric | Baseline (Unmanaged) | Reactive Control | Predictive FlexProof | Impact vs Baseline |
| :--- | :---: | :---: | :---: | :---: |
| **Deficit Energy** | 2,707.64 kWh | 83.78 kWh | **1.67 kWh** | **↓ 99.94%** *(98.00% vs Reactive)* |
| **Feeder Stress Intervals** | 125 intervals | 14 intervals | **1 interval** | **↓ 99.2%** *(92.86% vs Reactive)* |
| **Feeder Stress Duration** | 31.25 hours | 3.50 hours | **0.25 hours** | **↓ 99.2%** |
| **Peak Feeder Net Demand** | 2,621.11 kW | 2,374.19 kW | **2,306.69 kW** | **↓ 314.41 kW** peak shaving |
| **Maximum Overload Deficit** | 321.11 kW | 74.19 kW | **6.69 kW** | **↓ 314.42 kW** overload reduction |
| **Battery Cycling Throughput** | 0.00 kWh (Idle) | 1,552.60 kWh | **721.95 kWh** | **↓ 53.50%** cycling reduction |
| **Flexible-Load Energy Shifted** | 0.00 kWh | 5,754.83 kWh | **10,073.10 kWh** | **+4,318.27 kWh** (+75.0%) |
| **Proactive Controller Events** | 0 | 63 | **392** | **+329** proactive actions |

### Key Findings
* **99.94% Deficit Reduction**: Residual unserved energy deficit drops from 2,707.64 kWh in baseline to 1.67 kWh under FlexProof.
* **99.2% Feeder Overload Reduction**: Overload duration falls from 31.25 hours (125 intervals) to a single 15-minute residual stress interval (0.25 hours).
* **314.41 kW Peak Shaving**: Peak net feeder loading is trimmed from 2,621.11 kW down to 2,306.69 kW.
* **53.50% Battery Throughput Reduction**: By activating flexible loads in advance, battery cycling throughput decreases from 1,552.60 kWh to 721.95 kWh, preserving battery electrochemical longevity.
* **10,073.10 kWh Shifted**: Load flexibility utilization increases substantially through 392 logged proactive controller actions (210 load pre-shifts, 34 battery dispatches, and 148 reserve allocations).

---

## Why Predictive Flexibility?

The core challenge in distribution-level flexibility is the **actuator latency mismatch**:

* **Battery Energy Storage Systems (BESS)** respond near-instantaneously (<1 second to inverter ramp).
* **Flexible Demand Resources** (municipal water pumping stations, agricultural irrigation tube-wells, commercial chillers) require 15 to 30 minutes of operational delay to change states without mechanical cavitation or process disruption.

Under **Reactive Control**, the system waits until net demand exceeds the 2,300 kW feeder limit before issuing curtailment signals. Because pumps require 15–30 minutes to spool down, they deliver zero immediate relief. To prevent an immediate trip, the controller forces the battery to discharge at maximum power. Even with battery intervention, residual deficits occur, and battery throughput accumulates rapidly.

Under **Predictive FlexProof**, the 1-hour lookahead forecast identifies the evening ramp in advance. At $T - 45\text{ min}$, signals are dispatched to slow-response loads. By the time peak demand arrives at the feeder, the loads have already completed their transition, holding net demand within capacity and leaving the battery as a smooth secondary buffer.

---

## System Architecture

```
Historical / Synthetic Telemetry
              │
              ▼
    Demand + Solar Model
              │
              ▼
       1-Hour Lookahead
              │
              ▼
    Predictive Controller
              │
              ▼
   Flexible Loads + Battery
              │
              ▼
      Feeder Simulation
              │
              ▼
    Verification + Metrics
              │
              ▼
    Streamlit Control Room
```

---

## What the Prototype Demonstrates

| Demonstrated in Prototype | Reserved for Future Field Production |
| :--- | :--- |
| Closed-loop 15-minute multi-scenario simulation engine | Direct hardware-in-the-loop (HIL) PLC / RTU integration |
| 1-Hour lookahead forecasting from historical lag telemetry | Real-time utility SCADA / AMI telemetry ingestion |
| Explicit actuator latency modelling across 5 distinct fleets | Multi-phase AC unbalanced optimal power flow (OPF) |
| Thermodynamic battery model with strict SOC limits ($50\%\text{--}90\%$) | Commercial OpenADR 2.0b / IEEE 2030.5 protocol adapters |
| Strict energy conservation (100% deferred energy restored off-peak) | Dynamic customer tariff settlement & opt-out incentive billing |
| Interactive command center dashboard with event causality replay | Multi-feeder mesh distribution network coordination |

---

## Verification & Physical Invariants

FlexProof includes a comprehensive verification suite ensuring mathematical and physical integrity:

* **Automated Unit & Scenario Tests**: 24 automated tests passing in `tests/`, covering battery state transitions, efficiency losses, load shifting, forecasting bounds, and metrics.
* **Physical Invariant Validator (`validate.py`)**:
  * Feeder non-negativity and capacity constraints enforced across all 2,880 intervals.
  * Battery SOC clamped strictly within safe operational limits ($50.0\% \le \text{SOC} \le 90.0\%$).
  * Round-trip charging/discharging efficiency losses ($95\%$) continuously accounted for.
  * 100% flexible-load energy conservation (all shifted load energy restored during valley hours 00:00–05:30).
  * Deterministic reproducibility across all scenarios using fixed random seed (`seed=42`).

### Running the Verification Suite

```bash
# Execute unit and scenario tests
python -m pytest

# Execute physical invariant validation
python validate.py
```

---

## Running the Dashboard

The dashboard provides an industrial energy command center interface featuring executive scorecards, multi-scenario comparisons, predictive radar visuals, battery cycling analysis, and an interactive event causality replay tool.

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit command center
streamlit run dashboard/app.py
```

---

## Technology Stack

* **Language**: Python 3.10+ (tested on Python 3.12)
* **Data Processing & Analytics**: pandas, NumPy, SciPy
* **Machine Learning & Statistics**: scikit-learn (time-series lags, trend extrapolation)
* **Visualization & UI**: Streamlit, Plotly
* **Testing & Validation**: Pytest, Pydantic, PyYAML
* **Data Formats**: YAML configuration (`config.yaml`), CSV processed datasets and event logs

---

## Repository Structure

```
FlexProof-Hackathon/
├── config.yaml                     # Simulation, feeder, battery, and fleet configuration
├── requirements.txt                # Direct runtime and test dependencies
├── pytest.ini                      # Pytest runner configuration
├── run.py                          # Simulation orchestrator and CSV data exporter
├── validate.py                     # Physical invariant validator entrypoint
├── README.md                       # Public project documentation
│
├── models/
│   └── schemas.py                  # Domain dataclasses, Enums, and ScenarioResult schemas
│
├── simulator/
│   ├── config.py                   # Pydantic configuration loader and validators
│   ├── feeder.py                   # Substation feeder state and risk classification
│   ├── battery.py                  # Physical BESS model (SOC bounds, efficiency losses)
│   ├── flexible_loads.py           # Multi-fleet manager with duration limits & response lags
│   ├── forecasting.py              # Statistical lookahead forecaster (lags, rolling averages)
│   ├── stress.py                   # Stress prediction engine & capacity gap assessment
│   ├── flexibility.py              # Flexibility coordinator and dispatch prioritizer
│   ├── controller.py               # Baseline, Reactive, and Predictive controller logic
│   ├── simulation.py               # Multi-scenario continuous execution orchestrator
│   ├── metrics.py                  # Deficit energy, peak shaving, and advantage calculators
│   ├── reporting.py                # CSV export serialization for time series & event logs
│   ├── validation.py               # Invariant validation checks
│   └── data_sources/
│       ├── base.py                 # Abstract DataSource interface
│       └── synthetic.py            # Calibrated Indian feeder demand and solar model
│
├── audits/
│   ├── audit_trace.py              # Causality trace of peak overload events
│   └── full_audit.py               # Automated audit for zero lookahead leakage
│
├── dashboard/
│   ├── app.py                      # Streamlit command center dashboard entrypoint
│   ├── data_loader.py              # Cached scenario loader & dynamic metrics engine
│   └── components/
│       ├── kpi_cards.py            # Executive hero banner & 3-stage progression cards
│       ├── scenario_comparison.py  # 30-Day benchmark scorecards and demand timelines
│       ├── predictive_view.py      # 5-Stage predictive pipeline & forecast error residuals
│       ├── battery_view.py         # SOC trajectories & cycling throughput analysis
│       ├── flexibility_view.py     # Fleet capacity breakdown & dispatch timelines
│       └── event_explainer.py      # Synchronized event replay & causal timeline annotations
│
├── data/
│   ├── raw/                        # Raw input telemetry landing directory
│   └── processed/                  # Processed scenario CSV exports and event logs
│
├── docs/
│   ├── architecture.md             # System architecture and telemetry dataflow
│   ├── assumptions.md              # Engineering assumptions and boundary conditions
│   ├── control_logic.md            # Detailed control algorithms and response delay modeling
│   └── simulation.md               # Mathematical formulations and feeder physics
│
└── tests/
    ├── test_battery.py             # Battery charging, discharging, and SOC limit tests
    ├── test_controller.py          # Baseline, Reactive, and Predictive controller tests
    ├── test_flexibility.py         # Load shifting, restoration, and energy conservation tests
    ├── test_forecasting.py         # Horizon dimensions, non-negativity, and error tracking
    ├── test_metrics.py             # KPI calculations and percentage improvement tests
    ├── test_scenario_integrity.py  # Input time-series equality and determinism tests
    ├── test_simulation.py          # 2,880-interval full execution and schema checks
    └── test_stress.py              # Risk threshold classification and gap prediction tests
```

---

## Current Scope & Limitations

* **Simulation Prototype**: FlexProof is an engineering simulation prototype designed for control-room decision support. It is **not connected to a live physical electrical grid**.
* **Model Boundaries**: Power flows are modelled on a single-bus nodal active power balance (kW / kWh). Reactive power ($Q$), voltage sag/swell dynamics, power factor variations, and line impedance are omitted from this stage of evaluation.
* **Forecast Scope**: The forecasting module utilizes statistical multi-lag regression and trend projections. It is designed to illustrate the lookahead control architecture rather than serve as a utility-grade meteorological forecasting service.
* **Actuator Compliance Assumption**: In this simulation, flexible fleets follow scheduled dispatch within their physical latency limits. Real-world implementation requires customer incentive mechanisms, telemetry acknowledgements, and local override safeguards.
* **Zero Operational Outage Claims**: FlexProof does not predict catastrophic equipment failure or guarantee complete elimination of physical grid outages; it models the coordinated avoidance of feeder capacity constraint violations.

---

## Future Direction

1. **Hardware-in-the-Loop (HIL) Testing**: Interfacing the controller with simulated microgrid digital real-time simulators (e.g., OPAL-RT / RTDS).
2. **Advanced Forecasters**: Integrating transformer-based spatio-temporal solar irradiance forecasting models.
3. **Standards-Based DER Integration**: Implementing IEEE 2030.5 / OpenADR 2.0b telemetry and dispatch profiles for smart EVSEs and inverter-based resources.
4. **Three-Phase Unbalanced Power Flow**: Coupling with OpenDSS or GridLAB-D to evaluate localized voltage constraints and phase balancing.
5. **Multi-Feeder Aggregation**: Expanding coordination across adjacent distribution feeders for inter-feeder flexibility trading during substation transformer maintenance.

---

## Team

* **Nirman Amrawanshi** — Team Leader
* **Jayesh Pate** — Team Member
* **Indian Institute of Information Technology, Nagpur (IIIT Nagpur)**
* *Developed for the Schneider Electric / Yuva Yodha Energy Tech Hackathon*
