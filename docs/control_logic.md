# FlexProof Control Logic & Operational Strategies

## 1. Introduction & Strategy Overview

FlexProof evaluates three operational control paradigms under identical feeder loading and solar irradiance conditions:

1. **Baseline (Unmanaged)**: Traditional distribution network with zero active demand response or storage automation.
2. **Reactive Control (Threshold-Driven)**: Rule-based controller that intervenes only *after* feeder loading breaches the firm capacity limit.
3. **Predictive FlexProof (Forecast-Driven)**: Proactive coordination platform that looks ahead 1 hour, pre-positions flexible resources ahead of physical response lags, and orchestrates storage buffering.

---

## 2. Detailed Controller Logic

### A. Baseline Controller (`simulator/controller.py::BaselineController`)
* **Operating Logic**:
  * For every interval $t \in [1, 2880]$, telemetry ($P_{\text{demand}}(t), P_{\text{solar}}(t)$) is read.
  * No flexibility dispatch commands are issued ($\Delta P_{\text{flex}}(t) = 0.0\text{ kW}$).
  * Community battery remains idle at its initial State of Charge ($\text{SOC} = 0.70$).
* **Outcome**:
  * Unmitigated net demand peaks directly impact the distribution transformer.
  * Generates **125 stress intervals** ($31.25\text{ hours}$ of overload) and **$2,707.64\text{ kWh}$** of unserved energy deficit, peaking at $2,621.11\text{ kW}$ ($321.11\text{ kW}$ over limit).

---

### B. Reactive Controller (`simulator/controller.py::ReactiveController`)
* **Operating Logic**:
  1. **Blind State**: Has no lookahead or predictive horizon ($H = 0$).
  2. **Stress Detection**: Evaluates current effective net demand at interval $t$:
     $$P_{\text{effective}}(t) = P_{\text{demand}}(t) - P_{\text{solar}}(t) - \Delta P_{\text{active\_flex}}(t) + P_{\text{restoration}}(t)$$
  3. **Threshold Reaction**: If $P_{\text{effective}}(t) > P_{\text{limit}}$ ($2,300\text{ kW}$):
     * Calculate immediate deficit: $\Delta P_{\text{def}} = P_{\text{effective}}(t) - P_{\text{limit}}$.
     * Dispatch flexible loads: Calls `shift_load(deficit, t)`.
     * **The Actuator Delay Trap**: Due to physical response delays ($15\text{--}30\text{ min}$), water pumps ($105\text{ kW}$) and agricultural wells ($60\text{ kW}$) cannot deliver immediate power reduction in interval $t$.
     * Battery emergency discharge: For any remaining unmitigated deficit, battery discharges up to its unforecasted reactive limit ($P_{\text{bat\_max}} \times 0.55 = 82.5\text{ kW}$).
       > *Why the Reactive Discharge Cap (55%)?* Without a forecast of the peak's duration, a real-world reactive battery cannot safely dump its full $150\text{ kW}$ in the first 15 minutes, as doing so would exhaust all stored energy before the multi-hour evening peak concludes.
  4. **Off-Peak Valley Restoration**: During safe night hours ($00:00\text{--}05:30$), restores deferred load energy at a maximum safe rate of $60.0\text{ kW}$.
* **Outcome**:
  * Reduces baseline deficits significantly (**96.91% reduction**), but still leaves **14 stress intervals** ($83.78\text{ kWh}$ deficit) during fast-ramping evening periods where actuator delays prevent instant load shedding.
  * Forces high battery cycling burden (**$1,551.02\text{ kWh}$ throughput**).

---

### C. Predictive FlexProof Controller (`simulator/controller.py::PredictiveController`)
* **Operating Logic**:
  1. **Historical-Lag Forecasting (1-Hour Lookahead)**:
     * Reads past demand and solar history: $h_d = [t - 96 : t]$, $h_s = [t - 96 : t]$.
     * Forecasts $H = 4$ future intervals ($15, 30, 45, 60\text{ minutes}$ ahead) using lag-1d, lag-2d, lag-7d, 4-interval rolling means, and trend extrapolation.
  2. **Stress Prediction & Risk Radar**:
     * Calculates future forecast net demand: $\hat{P}_{\text{net}}(t + k) = \hat{P}_{\text{demand}}(t + k) - \hat{P}_{\text{solar}}(t + k)$.
     * Evaluates future gaps: $\hat{G}(t + k) = \max(0, \hat{P}_{\text{net}}(t + k) - P_{\text{limit}})$.
     * Determines `time_to_stress_intervals` and assigns risk level (`NORMAL`, `WATCH`, `WARNING`, `CRITICAL`).
  3. **Advance Flexibility Preparation (Pre-Shifting)**:
     * When upcoming stress is predicted ($\hat{G} > 0$ and `time_to_stress` $\le 3$ intervals):
     * The controller marks community battery as `RESERVED` (preventing daytime drain).
     * Pre-shifts flexible loads **ahead of their response delays** (e.g. initiating pump shutdown at $17:30$ so the full $105\text{ kW}$ reduction is active when the peak arrives at $18:00$).
  4. **Precision Storage Buffering**:
     * When the actual peak arrives, flexible load reductions are already fully active at the grid level.
     * The battery only needs to supply a small, gentle precision buffer to absorb minor residual forecast errors.
  5. **Safe Valley Night Restoration**:
     * Restores deferred energy gradually during off-peak valley hours ($00:00\text{--}05:30$).
* **Outcome**:
  * Achieves **$99.94\%$ deficit reduction** ($1.67\text{ kWh}$ residual deficit across 30 days) and **$99.20\%$ stress reduction** ($1\text{ residual interval}$).
  * Reduces battery cycling burden by **$52.2\%$** ($741.14\text{ kWh}$ vs $1,551.02\text{ kWh}$) by letting flexible loads bear the peak.

---

## 3. Deep Causality Case Study: The January 12 Peak Event

The deep event audit (`audits/audit_trace.py`) examines the critical evening peak on **January 12, 2024**:

```
Time (Jan 12)       Baseline ND     Reactive ND     Reactive Bat     Predictive ND   Predictive Bat   Predictive Gap
17:00:00            2,043.6 kW      2,043.6 kW      SOC: 0.900       2,043.6 kW      SOC: 0.900       0.0 kW
17:15:00            2,107.7 kW      2,107.7 kW      SOC: 0.900       2,107.7 kW      SOC: 0.900       0.0 kW
17:30:00            2,262.9 kW      2,262.9 kW      SOC: 0.900       2,262.9 kW      SOC: 0.900       0.0 kW (Watch)
17:45:00            2,277.4 kW      2,277.4 kW      SOC: 0.900       2,277.4 kW      SOC: 0.900       0.0 kW (Pre-shift)
18:00:00 (PEAK)     2,456.7 kW      2,374.2 kW      SOC: 0.857       2,306.7 kW      SOC: 0.821       0.0 kW
18:15:00            2,488.1 kW      2,300.0 kW      SOC: 0.840       2,300.0 kW      SOC: 0.805       0.0 kW
18:30:00            2,471.3 kW      2,286.3 kW      SOC: 0.840       2,286.3 kW      SOC: 0.805      55.4 kW (Pre-shift)
18:45:00 (MAX)      2,621.1 kW      2,350.5 kW      SOC: 0.797       2,300.0 kW      SOC: 0.764      26.5 kW
19:00:00            2,515.8 kW      2,300.0 kW      SOC: 0.758       2,247.5 kW      SOC: 0.764      99.0 kW
```

### Key Causality Findings:
1. **At 18:00:00 (Baseline = 2,456.7 kW, Overload = 156.7 kW)**:
   * **Reactive**: Detects overload at 18:00. Dispatches loads, but water pumps (30 min delay) deliver 0 kW. Battery discharges at its 82.5 kW cap, leaving **$2,374.2\text{ kW}$ ($74.2\text{ kW}$ deficit)**.
   * **Predictive FlexProof**: Began load pre-shifting at 17:45. At 18:00, EV and HVAC reductions are already fully active, and the battery provides $150\text{ kW}$ precision discharge, keeping demand at **$2,306.7\text{ kW}$ ($6.69\text{ kW}$ minor residual deficit)**.
2. **At 18:45:00 (Baseline = 2,621.1 kW, Overload = 321.1 kW)**:
   * **Reactive**: Suffering cumulative strain, demand spikes to **$2,350.5\text{ kW}$ ($50.5\text{ kW}$ deficit)**.
   * **Predictive FlexProof**: All 5 flexible fleets ($321.1\text{ kW}$ flex dispatched) are active simultaneously in advance, holding net demand exactly at **$2,300.0\text{ kW}$ ($0.0\text{ kW}$ deficit)**.

---

## 4. Summary of Strategy Comparison

| Feature | 🔴 Baseline | 🟡 Reactive Control | 🟢 Predictive FlexProof |
| :--- | :---: | :---: | :---: |
| **Forecasting Lookahead** | None | None ($0\text{ min}$) | **1 Hour** ($4\text{ intervals}$) |
| **Actuator Lag Management** | None | Suffers full delay | **Pre-shifts with lead time** |
| **Storage Strategy** | Idle | Emergency uncoordinated discharge | **Coordinated precision buffer** |
| **Flexible Fleet Utilization** | $0\text{ kWh}$ | $5,163.4\text{ kWh}$ | **$12,074.9\text{ kWh}$ (2.3×)** |
| **30-Day Deficit Energy** | $2,707.64\text{ kWh}$ | $83.78\text{ kWh}$ | **$1.67\text{ kWh}$** |
| **30-Day Battery Throughput** | $0\text{ kWh}$ | $1,551.02\text{ kWh}$ | **$741.14\text{ kWh}$ (-52.2%)** |
