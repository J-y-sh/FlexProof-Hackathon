# FlexProof Architecture Specification

## 1. System Overview

FlexProof is structured as a modular, decoupled simulation and coordination platform for neighbourhood distribution grids. The platform evaluates and visualizes three distinct control paradigms (Baseline, Reactive, and Predictive) across identical physical feeder conditions.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA SOURCE LAYER                                    │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │  SyntheticDataSource (30 Days • 2,880 Intervals @ 15-min)                      │   │
│   │  - Residential Peak (1,635 kW) • Commercial (650 kW) • Industrial (450 kW)      │   │
│   │  - Solar PV Generation (800 kW Envelope with Cloud Attenuation)                │   │
│   │  - Baseline Flexible Fleets (EV, Water Pumping, HVAC, Agri, Refrigeration)     │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Telemetry (Demand, Solar, Timestamp)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THREE-TIER CONTROLLER LAYER                               │
│                                                                                        │
│   ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐   │
│   │   BaselineController   │  │   ReactiveController   │  │  PredictiveController  │   │
│   │   - Zero intervention  │  │   - Real-time breaches │  │   - 1-Hr lookahead     │   │
│   │   - Idle storage (70%) │  │   - Unforecasted cap   │  │   - Advance pre-shift  │   │
│   │   - Unmitigated peaks  │  │   - Actuator delay lag │  │   - Storage buffer     │   │
│   └───────────┬────────────┘  └───────────┬────────────┘  └───────────┬────────────┘   │
└───────────────┼───────────────────────────┼───────────────────────────┼────────────────┘
                │                           │                           │
                ▼                           ▼                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              PHYSICAL ASSET & MODEL LAYER                              │
│                                                                                        │
│   ┌──────────────────────────────────┐      ┌──────────────────────────────────────┐   │
│   │  CommunityBattery (500 kWh)      │      │  FlexibleLoadManager (362 kW Fleet)  │   │
│   │  - Charge/Discharge: 150 kW max  │      │  - HVAC (45 kW flex, 15m delay)      │   │
│   │  - SOC Envelope: [50%, 90%]      │      │  - EV Charging (140 kW, 15m delay)   │   │
│   │  - Efficiency: 95% Charge/Dis    │      │  - Water Pumps (105 kW, 30m delay)   │   │
│   │  - Conservation: Strict Wh/kWh   │      │  - Agri Pumps (60 kW, 30m delay)     │   │
│   │  - Throughput Tracking           │      │  - Refrigeration (12 kW, 15m delay)  │   │
│   └──────────────────────────────────┘      │  - Valley Energy Restoration Window  │   │
│                                             └──────────────────────────────────────┘   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              EVALUATION & AUDIT LAYER                                  │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │  Feeder State & Metrics Engine (simulator/feeder.py, simulator/metrics.py)     │   │
│   │  - Deficit Energy Integration • Peak Feeder Loading • Stress Duration          │   │
│   │  - Battery Cycling Burden • Multi-Scenario Percentage Improvements             │   │
│   ├────────────────────────────────────────────────────────────────────────────────┤   │
│   │  Verification & Audit Suite (audits/full_audit.py, audits/audit_trace.py)      │   │
│   │  - Zero Lookahead Leakage • Imperfect Forecast Tracking • Actuator Delay Lag   │   │
│   │  - Scenario Independence • Deterministic Reproducibility                       │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ CSV Exports (data/processed/)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            STREAMLIT COMMAND CENTER DASHBOARD                          │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │  Executive Hero Banner • 3-Stage Progression Story • Scenario Scorecard        │   │
│   │  Predictive Forecast Radar • Battery Longevity • Fleet Waterfalls              │   │
│   │  Interactive Peak Stress Event Replay & Dynamic Control Causality Breakdown    │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Directory & Module Responsibilities

### Core Domain Models (`models/`)
* **`models/schemas.py`**:
  * Centralized type contracts, dataclasses, and Enums.
  * Enums: `RiskLevel` (`NORMAL`, `WATCH`, `WARNING`, `CRITICAL`), `BatteryAction` (`IDLE`, `CHARGING`, `DISCHARGING`, `RESERVED`), `ResourceType`, `ResourceStatus`.
  * Data schemas: `FlexibleResource`, `BatteryState`, `FeederState`, `ForecastResult`, `ControllerEvent`, `IntervalRecord`, `SimulationMetrics`, `ScenarioResult`, `ImprovementMetrics`.

---

### Simulation Engine (`simulator/`)
* **`simulator/config.py`**:
  * Pydantic validation layer for `config.yaml`. Enforces physical parameter checks (e.g. $\text{min\_soc} < \text{max\_soc}$, resolution consistency, non-negative power bounds).
* **`simulator/data_sources/`**:
  * `base.py`: Defines the abstract `DataSource` interface.
  * `synthetic.py`: Implements deterministic Indian neighbourhood demand decomposition (residential evening cooking/AC peak, commercial business hours, steady industrial daytime) and solar irradiance with cloud disturbances using `np.random.RandomState(seed=42)`.
* **`simulator/feeder.py`**:
  * Models the $11\text{ kV} / 415\text{ V}$ distribution substation transformer with a $2,300\text{ kW}$ firm thermal capacity limit.
  * Evaluates instantaneous loading percentage, deficit power, and four risk tiers (`NORMAL < 75%`, `WATCH 75-85%`, `WARNING 85-95%`, `CRITICAL ≥ 95%`).
* **`simulator/battery.py`**:
  * High-fidelity thermodynamic battery storage model.
  * Tracks internal energy ($E = \text{SOC} \times C$), enforcing minimum ($50\%$) and maximum ($90\%$) SOC thresholds.
  * Accurately accounts for $95\%$ round-trip charge/discharge efficiency losses:
    $$\Delta E_{\text{charge}} = P_{\text{grid}} \times \Delta t \times \eta_{\text{charge}}$$
    $$\Delta E_{\text{discharge}} = \frac{P_{\text{delivered}} \times \Delta t}{\eta_{\text{discharge}}}$$
* **`simulator/flexible_loads.py`**:
  * Implements `FlexibleLoadManager` managing 5 resource fleets (362 kW total flexible capacity).
  * Enforces `ShiftRecord` objects with explicit duration tracking and physical actuator response-time delays ($15\text{ to }30\text{ minutes}$).
  * Handles safe off-peak energy restoration during night valley hours ($00:00\text{ to }05:30$).
* **`simulator/forecasting.py`**:
  * Implements `ForecastingEngine` with a $1\text{-hour}$ ($4\text{ intervals}$) lookahead horizon.
  * Combines historical lagged patterns (1-day, 2-day, 7-day lags), 4-interval rolling averages, and recent trend extrapolation.
  * Tracks online prediction errors (MAE / RMSE) across demand and solar generation independently.
* **`simulator/stress.py`**:
  * Implements `StressPredictionEngine` analyzing future forecast arrays against the $2,300\text{ kW}$ feeder limit to calculate `forecast_gap_kw` and `time_to_stress_intervals`.
* **`simulator/flexibility.py`**:
  * Implements `FlexibilityCoordinator` orchestrating the dispatch sequence:
    1. Off-peak solar charging during daytime surplus.
    2. Advance preparation / pre-shifting when stress is predicted.
    3. Coordinated peak dispatch prioritizing zero-carbon load flexibility ahead of storage.
* **`simulator/controller.py`**:
  * Encapsulates the three operational strategies: `BaselineController`, `ReactiveController`, and `PredictiveController`.
  * Outputs standardized `ScenarioResult` containers.
* **`simulator/metrics.py`**:
  * Formulates numerical metrics: Deficit Energy ($\text{kWh}$), Peak Net Demand ($\text{kW}$), Battery Throughput ($\text{kWh}$), and relative percentage improvements.
* **`simulator/reporting.py`**:
  * Serializes simulation dataframes and discrete controller event logs to `data/processed/`.
* **`simulator/validation.py`**:
  * Mathematical invariant verification engine (bounds, non-negativity, energy conservation, no NaNs).

---

### Audit & Verification Layer (`audits/`)
* **`audits/audit_trace.py`**:
  * Performs interval-by-interval telemetry and control state extraction around peak historical stress events (e.g. Jan 12 18:00).
* **`audits/full_audit.py`**:
  * Automated 6-point verification script proving zero lookahead data leakage, non-zero forecast errors, lookback boundary enforcement, reactive controller blind state, baseline zero dispatch, and physical actuator lag compliance.

---

### Visualization Layer (`dashboard/`)
* **`dashboard/data_loader.py`**:
  * Cached loader for processed CSVs and configuration; computes dynamic comparative metrics.
* **`dashboard/components/`**:
  * `kpi_cards.py`: Executive hero banner & 3-stage control progression narrative.
  * `scenario_comparison.py`: Benchmark scorecard, 30-day timelines, and cumulative deficit curves.
  * `predictive_view.py`: 5-stage predictive pipeline, forecast radar, and error residuals.
  * `battery_view.py`: Battery SOC trajectories, operating bounds, and cycling burden analysis.
  * `flexibility_view.py`: Fleet dispatch waterfalls and resource coordination comparison.
  * `event_explainer.py`: Interactive stress event replay with step-by-step causality audit.
* **`dashboard/app.py`**:
  * Streamlit application entrypoint supporting Hackathon Live Pitch Mode and Full Command Center Mode.

---

## 3. Dataflow & Execution Lifecycle

```
1. CLI Entrypoint (run.py)
   │
   ├──> load_config("config.yaml")
   ├──> SyntheticDataSource(config) [Deterministically generates 2,880 intervals]
   │
   ├──> BaselineController.run(ds)   ──> ScenarioResult('Baseline')
   ├──> ReactiveController.run(ds)   ──> ScenarioResult('Reactive')
   └──> PredictiveController.run(ds) ──> ScenarioResult('Predictive FlexProof')
   │
   ├──> calculate_improvements()
   ├──> export_all_scenarios()       ──> data/processed/*.csv
   └──> export_events_csv()          ──> data/processed/*_events.csv

2. Validation Entrypoint (validate.py)
   │
   ├──> run_all_scenarios()
   └──> run_full_validation()        ──> Asserts Invariants (Exit Code 0/1)

3. Dashboard Entrypoint (streamlit run dashboard/app.py)
   │
   ├──> load_configuration() (cached)
   ├──> load_all_data() (cached from data/processed/)
   ├──> compute_comparative_summary() (dynamic evaluation)
   └──> Renders Interactive Plotly Visualizations & Executive Pitch
```
