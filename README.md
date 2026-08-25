# FlexProof — Predictive Neighbourhood Grid Flexibility Platform

> **"Predict feeder stress before it becomes a distribution transformer failure."**  
> *Developed for the Schneider Electric / Yuva Yodha Energy Tech Hackathon.*

---

## ⚡ Executive Summary

Distribution grid infrastructure in growing urban and peri-urban neighbourhoods faces severe operational stress. The rapid penetration of electric vehicles (EVs), distributed rooftop solar PV, and heavy thermal/cooling loads causes steep evening demand ramps that frequently breach local substation and distribution transformer thermal limits.

Traditional distribution management relies on **reactive control**—detecting overloads only *after* the feeder capacity is breached. However, municipal water pumps, agricultural tube-wells, and commercial refrigeration systems exhibit **physical response-time delays (15 to 30 minutes)**. Under reactive control, these slow-acting assets cannot ramp down in time, forcing emergency battery discharge that rapidly depletes community storage, accelerates cell degradation, and still leaves residual unserved energy deficits.

**FlexProof** is a predictive neighbourhood grid flexibility platform that operates at the 11 kV / 415 V feeder level. By forecasting demand and solar generation **1 hour in advance (4 intervals at 15-minute resolution)** from historical telemetry, FlexProof transitions grid operations from reactive emergency response to **coordinated, advance flexibility preparation**:

$$\text{Predict} \longrightarrow \text{Prepare} \longrightarrow \text{Coordinate} \longrightarrow \text{Dispatch} \longrightarrow \text{Learn}$$

1. **Predict**: Forecasts net demand and identifies upcoming capacity breaches.
2. **Prepare**: Pre-shifts flexible deferrable loads *before* peak arrival, overcoming physical actuator latency.
3. **Coordinate**: Reserves community battery capacity and prioritizes zero-carbon load flexibility ahead of storage.
4. **Dispatch**: Delivers smooth, precision peak shaving while strictly maintaining energy conservation during valley hours.
5. **Learn**: Continuously tracks forecast error residuals (MAE/RMSE) to refine risk margins.

---

## 📊 Key Verified Simulation Results (30-Day Scenario)

*Evaluation across a 30-day synthetic Indian neighbourhood feeder scenario (2,880 intervals, 15-min resolution, 2,300 kW firm feeder limit, 800 kW solar PV, 500 kWh battery, 362 kW flexible fleet).*

| Operational Metric | 🔴 Baseline (Unmanaged) | 🟡 Reactive Control | 🟢 Predictive FlexProof | Predictive Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Deficit Energy** | **2,707.64 kWh** | **83.78 kWh** | **1.67 kWh** | **↓ 99.94%** *(98.00% vs. Reactive)* |
| **Stress Intervals (15-min)** | **125** (31.25 hrs) | **14** (3.50 hrs) | **1** (0.25 hrs) | **↓ 99.20%** *(92.86% vs. Reactive)* |
| **Peak Feeder Net Demand** | **2,621.11 kW** | **2,374.19 kW** | **2,306.69 kW** | **↓ 314.42 kW** peak shaving |
| **Maximum Overload Deficit** | **321.11 kW** | **74.19 kW** | **6.69 kW** | **↓ 314.42 kW** overload reduction |
| **Battery Cycling Throughput** | **0.00 kWh** | **1,551.02 kWh** | **741.14 kWh** | **↓ 52.2%** cycling burden reduction |
| **Flexible Energy Shifted** | **0.00 kWh** | **5,163.42 kWh** | **12,074.94 kWh** | **↑ 2.3×** more load flexibility utilized |
| **Flexibility Dispatch Events** | **0** | **95** | **256** | **+161** advance pre-shift actions |
| **Forecast Error (MAE / RMSE)** | — | — | **54.38 kW / 85.81 kW** | Grounded statistical lookahead |

> **⭐ The Storage Longevity Dividend:** FlexProof does not achieve superior grid protection by simply adding more batteries. By pre-shifting deferrable loads with advance lead time, FlexProof shifts **2.3× more flexible load energy**, reducing battery cycling throughput by **52.2%** compared to reactive control.

---

## 🏛️ System Architecture

```
                                  [ Historical Telemetry & Solar Data ]
                                                    │
                                                    ▼
                                     ┌─────────────────────────────┐
                                     │   Forecasting Engine (1-Hr) │
                                     │  (Lag-1d/2d/7d, Trend, Roll) │
                                     └──────────────┬──────────────┘
                                                    │
                                                    ▼
                                     ┌─────────────────────────────┐
                                     │   Stress Prediction Engine  │
                                     │   (Risk Radar: Watch/Warn)  │
                                     └──────────────┬──────────────┘
                                                    │
                       ┌────────────────────────────┴────────────────────────────┐
                       ▼                                                         ▼
       ┌───────────────────────────────┐                         ┌───────────────────────────────┐
       │   Advance Load Pre-Shifting   │                         │   Community Battery Storage   │
       │  (EV, Pumps, HVAC: 362 kW)    │                         │   (500 kWh, 150 kW, [50-90%]) │
       └───────────────┬───────────────┘                         └───────────────┬───────────────┘
                       │                                                         │
                       └────────────────────────────┬────────────────────────────┘
                                                    │
                                                    ▼
                                     ┌─────────────────────────────┐
                                     │    Flexibility Coordinator  │
                                     │   (Feeder Limit: 2300 kW)   │
                                     └──────────────┬──────────────┘
                                                    │
                                                    ▼
                                     ┌─────────────────────────────┐
                                     │  Controlled Feeder Loading  │
                                     │   (1 Residual Stress Int)   │
                                     └─────────────────────────────┘
```

---

## 🔬 Audit & Data-Integrity Guarantees

FlexProof enforces strict physical invariants and verification gates:

1. **No Look-Ahead Data Leakage**: The forecasting model receives strictly historical observations (`history[t - lookback:t]`). Forecasts exhibit realistic error residuals (MAE 54.38 kW, RMSE 85.81 kW) and do not access future ground-truth data.
2. **Actuator Response Time Enforcement**: Flexible resources obey physical activation delays (HVAC: 15 min, EV: 15 min, Water Pumps: 30 min, Agricultural Wells: 30 min). Loads cannot deliver instantaneous relief without lead time.
3. **Strict Energy Conservation**: 100% of deferred flexible load energy is restored during safe valley night hours (00:00–05:30) without creating secondary demand peaks.
4. **Thermodynamic Battery Modeling**: State of Charge (SOC) is strictly clamped to $[50\%, 90\%]$, initial SOC is 70%, with 95% charge/discharge efficiency losses continuously accounted for.
5. **Scenario Independence & Determinism**: Baseline, Reactive, and Predictive controllers execute on bit-for-bit identical input time series (`seed=42`) with completely isolated mutable states.

---

## 💻 Quick Start & Local Execution

### 1. Prerequisites
* Python 3.10+ (tested on Python 3.12)
* Virtual environment recommended

### 2. Installation
```bash
# Clone or navigate to the workspace
cd FlexProof-Hackathon

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Automated Tests & Invariant Validation
```bash
# Run unit & scenario test suite (24 tests)
python -m pytest -v

# Run full physical invariant validation suite
python validate.py
```

### 4. Execute End-to-End Simulation & Export Data
```bash
# Runs Baseline, Reactive, and Predictive scenarios across 2,880 intervals
# Exports processed time-series and event logs to data/processed/
python run.py
```

### 5. Launch the Streamlit Command Center Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📂 Repository Structure

```
FlexProof-Hackathon/
├── config.yaml                     # Centralized simulation, feeder, and asset configuration
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Test runner configuration
├── run.py                          # CLI simulation runner & CSV data exporter
├── validate.py                     # Physical invariant & constraint validation entrypoint
│
├── models/
│   └── schemas.py                  # Domain dataclasses, Enums, and ScenarioResult schemas
│
├── simulator/
│   ├── config.py                   # Pydantic configuration loader & validators
│   ├── feeder.py                   # Substation feeder state, loading & risk classification
│   ├── battery.py                  # Physical community battery model (efficiency, SOC bounds)
│   ├── flexible_loads.py           # Fleet manager with continuous duration shifting & response lags
│   ├── forecasting.py              # Statistical lookahead forecaster (lags, rolling averages, trend)
│   ├── stress.py                   # Stress prediction engine, risk radar & gap calculation
│   ├── flexibility.py              # Coordinated dispatch priority & off-peak charging
│   ├── controller.py               # Baseline, Reactive, and Predictive controllers
│   ├── simulation.py               # Orchestrator for multi-scenario execution
│   ├── metrics.py                  # Deficit, peak shaving, and predictive advantage formulas
│   ├── reporting.py                # CSV serialization for scenario data and event audit logs
│   ├── validation.py               # Invariant checker (no NaNs, non-negativity, bounds)
│   └── data_sources/
│       ├── base.py                 # Abstract DataSource interface
│       └── synthetic.py            # Calibrated Indian feeder demand, solar PV & cloud events
│
├── audits/
│   ├── audit_trace.py              # Deep causality trace of peak stress events (Jan 12 18:00)
│   └── full_audit.py               # Automated audit for zero lookahead leakage & actuator delays
│
├── dashboard/
│   ├── app.py                      # Streamlit Command Center dashboard entrypoint
│   ├── data_loader.py              # Cached scenario loader & dynamic metrics engine
│   └── components/
│       ├── kpi_cards.py            # Executive hero banner & 3-stage control progression story
│       ├── scenario_comparison.py  # 30-Day benchmark scorecard, timelines & cumulative curves
│       ├── predictive_view.py      # 5-Stage predictive pipeline, forecast radar & error residuals
│       ├── battery_view.py         # SOC trajectories, operating bounds & cycling burden analysis
│       ├── flexibility_view.py     # Fleet dispatch waterfalls & resource coordination comparison
│       └── event_explainer.py      # Interactive stress event replay & dynamic decision audit log
│
├── data/
│   ├── raw/                        # Raw telemetry landing directory
│   └── processed/                  # Processed scenario CSVs & controller event logs
│
├── docs/
│   ├── architecture.md             # Complete system architecture & dataflow specification
│   ├── simulation.md               # Simulation methodology, feeder physics & mathematical formulas
│   ├── control_logic.md            # Detailed control logic, response times & causality analysis
│   ├── assumptions.md              # Transparent engineering assumptions & boundary conditions
│   ├── demo_script.md              # 5-to-7 minute hackathon live demonstration & pitch script
│   ├── pitch.md                    # 3-minute and 5-minute executive pitch scripts
│   ├── judge_qa.md                 # 21 categorized, technically defensible judge Q&A answers
│   ├── technical_cheatsheet.md     # One-page ultra-dense technical reference cheat sheet
│   ├── judge_demo_flow.md          # Practical click-by-click presenter demonstration flow
│   ├── presentation_slides.md      # 10-slide executive & technical hackathon deck structure
│   ├── submission_checklist.md     # Comprehensive pre-submission verification checklist
│   └── demo_backup.md              # Live demonstration backup & disaster recovery protocol
│
└── tests/
    ├── test_battery.py             # Battery charging, discharging, SOC limits & throughput tests
    ├── test_controller.py          # Baseline, Reactive, and Predictive controller behavior tests
    ├── test_flexibility.py         # Load shifting, safe restoration & energy conservation tests
    ├── test_forecasting.py         # Horizon dimensions, non-negativity & error metrics tests
    ├── test_metrics.py             # Metric calculations & percentage improvement formula tests
    ├── test_scenario_integrity.py  # Input time-series equality & determinism tests
    ├── test_simulation.py          # 2,880-interval execution & schema consistency tests
    └── test_stress.py              # Risk threshold classification & gap prediction tests
```

---

## ⚠️ Transparent Assumptions & Limitations

* **Simulated Environment**: All results reflect a calibrated 30-day synthetic simulation ($15\text{-minute}$ resolution, $2,880$ intervals). They demonstrate architectural proof-of-concept and must not be cited as empirical field measurements.
* **Residual Stress State**: Predictive control nearly eliminates feeder stress ($99.94\%$ deficit reduction), but 1 residual interval ($1.67\text{ kWh}$, max deficit $6.69\text{ kW}$) remains during an extreme multi-fleet coincidence peak.
* **Actuator Compliance**: In this model, flexible resources follow dispatch commands within their physical delay limits. Real-world deployments require user opt-in incentives and local override handling.
* **Forecasting Method**: The baseline forecasting engine utilizes historical lag features and trend extrapolation. Advanced ML models (e.g., LightGBM, Temporal Fusion Transformers) can be plugged in seamlessly via `simulator/forecasting.py`.

---

## 🏆 Hackathon Context & Innovation

FlexProof was designed for the **Schneider Electric / Yuva Yodha Energy Tech Hackathon** to demonstrate how software-defined predictive flexibility can alleviate distribution grid congestion, defer expensive substation reinforcement, and protect community storage assets under high renewable and EV penetration.
