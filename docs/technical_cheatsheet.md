# FlexProof Technical One-Page Cheat Sheet

> **Quick Reference for Live Demonstrations & Technical Audits**  
> *Schneider Electric / Yuva Yodha Energy Tech Hackathon*

---

## ⚡ 1. System Specifications & Boundaries

* **Simulation Horizon**: $30\text{ days}$ | $2,880\text{ intervals}$ | $\Delta t = 15\text{ minutes}$ ($0.25\text{ hours}$) | Seed: `42`.
* **Distribution Feeder**: $11\text{ kV} / 415\text{ V}$ substation transformer | Firm Thermal Capacity Limit = **$2,300.0\text{ kW}$**.
* **Solar PV Generation**: $800.0\text{ kW}$ peak capacity | Diurnal envelope $06:00\text{--}18:30$ | Cloud probability $15\%$ ($30\text{--}80\%$ attenuation).
* **Community Battery (BESS)**: $500.0\text{ kWh}$ capacity | $150.0\text{ kW}$ max charge/discharge | Operational SOC: $[50\%, 90\%]$ | Initial SOC: $70\%$ | Efficiency: $95\%$ charge, $95\%$ discharge.
* **Flexible Load Fleet Pool ($362.0\text{ kW}$ total flexible capacity)**:
  * *HVAC*: $30\text{ units} \times 3\text{ kW} = 90\text{ kW}$ ($50\%$ flex = $45\text{ kW}$, $15\text{ min delay}$, priority 1).
  * *EV Charging*: $25\text{ chargers} \times 7\text{ kW} = 175\text{ kW}$ ($80\%$ flex = $140\text{ kW}$, $15\text{ min delay}$, priority 2).
  * *Water Pumping*: $10\text{ pumps} \times 15\text{ kW} = 150\text{ kW}$ ($70\%$ flex = $105\text{ kW}$, $30\text{ min delay}$, priority 3).
  * *Agricultural Wells*: $5\text{ pumps} \times 20\text{ kW} = 100\text{ kW}$ ($60\%$ flex = $60\text{ kW}$, $30\text{ min delay}$, priority 3).
  * *Commercial Refrigeration*: $8\text{ units} \times 5\text{ kW} = 40\text{ kW}$ ($30\%$ flex = $12\text{ kW}$, $15\text{ min delay}$, priority 4).
* **Energy Conservation**: $100\%$ of deferred load energy is restored during safe valley night hours ($00:00\text{--}05:30$) capped at $60\text{ kW}$.

---

## 🧭 2. Three-Tier Controller Architecture

1. **🔴 Baseline (Unmanaged)**: Zero flexibility dispatch; battery idle at $70\%$ SOC; absorbs uncontrolled demand peaks.
2. **🟡 Reactive Control (Threshold-Driven)**: Senses $P_{\text{net}} > 2,300\text{ kW}$ in real time; suffers $15\text{--}30\text{ min}$ actuator response delays; applies conservative $55\%$ battery discharge cap ($82.5\text{ kW}$) to prevent blind depletion.
3. **🟢 Predictive FlexProof (Forecast-Driven)**: Looks ahead $1\text{ hour}$ ($4\text{ intervals}$); pre-shifts slow loads ahead of response delays; reserves storage capacity; dispatches storage gently as precision buffer.

---

## 🧠 3. Forecasting & Lookahead Engine

* **Input Telemetry**: Historical demand and solar power arrays.
* **Lookback Buffer**: $96\text{ intervals}$ ($24\text{ hours}$ minimum history required).
* **Horizon**: $4\text{ intervals}$ ($60\text{ minutes}$ lookahead).
* **Statistical Method**: Weighted ensemble of lag-1d ($0.35$), lag-2d ($0.15$), lag-7d ($0.10$), rolling 4-int mean ($0.25$), and 8-int linear trend ($0.15$).
* **Leakage Protection**: Strict $t' \le t$ indexing; verified online error metrics: **$\text{MAE} = 54.38\text{ kW}$**, **$\text{RMSE} = 85.81\text{ kW}$**.

---

## 📊 4. Locked 30-Day Benchmark Results

| Metric | 🔴 Baseline | 🟡 Reactive | 🟢 Predictive FlexProof | Improvement vs Baseline | Advantage vs Reactive |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Deficit Energy** | **$2,707.64\text{ kWh}$** | **$83.78\text{ kWh}$** | **$1.67\text{ kWh}$** | **↓ 99.94%** | **↓ 98.00%** |
| **Stress Intervals (15-min)** | **125** ($31.25\text{ hrs}$) | **14** ($3.50\text{ hrs}$) | **1** ($0.25\text{ hrs}$) | **↓ 99.20%** | **↓ 92.86%** |
| **Peak Net Demand** | **$2,621.11\text{ kW}$** | **$2,374.19\text{ kW}$** | **$2,306.69\text{ kW}$** | **-314.42 kW** | **-67.50 kW** |
| **Max Overload Deficit** | **$321.11\text{ kW}$** | **$74.19\text{ kW}$** | **$6.69\text{ kW}$** | **-314.42 kW** | **-67.50 kW** |
| **Battery Throughput** | **$0.00\text{ kWh}$** | **$1,551.02\text{ kWh}$** | **$741.14\text{ kWh}$** | — | **↓ 52.2% cycling burden** |
| **Flexible Energy Shifted** | **$0.00\text{ kWh}$** | **$5,163.42\text{ kWh}$** | **$12,074.94\text{ kWh}$** | — | **↑ 2.3× more load flex** |
| **Flexibility Dispatch Events**| **0** | **95** | **256** | — | **+161 proactive actions** |

---

## 🔬 5. Verification & Test Suite Reference

* **Compilation**: `python -m compileall simulator models tests audits dashboard` $\rightarrow$ **PASS (100%)**.
* **Pytest Suite**: `python -m pytest -v` $\rightarrow$ **24 passed in 10.74s** (0 failed).
* **Physical Invariant Validation**: `python validate.py` $\rightarrow$ **ALL invariants passed (exit code 0)**.
* **Audit Scripts**:
  * `audits/full_audit.py`: Confirms zero lookahead leakage, non-zero errors, lookback boundary, reactive blind state, baseline zero dispatch, and actuator delay compliance.
  * `audits/audit_trace.py`: Deep interval trace of January 12 peak overload event.

---

## 🎯 6. Live Presentation Quick Reference

* **Launch Dashboard**: `streamlit run dashboard/app.py`
* **Default Mode**: `🎯 Hackathon Live Pitch Mode` $\rightarrow$ `🏆 Executive / Judge Pitch`
* **Strongest Historical Stress Event**: **January 12, 2024 @ 18:00 / 18:45**
  * Baseline Peak: $2,621.1\text{ kW}$ ($321.1\text{ kW}$ overload).
  * Reactive Peak: $2,350.5\text{ kW}$ ($50.5\text{ kW}$ residual deficit due to pump delay).
  * Predictive FlexProof: $2,300.0\text{ kW}$ ($0.0\text{ kW}$ deficit via advance pre-shifting).
* **Key Soundbite to Recite**: *"FlexProof shifts 2.3× more flexible load energy in advance, reducing unserved deficit by 99.94% while cutting battery cycling throughput by 52.2%."*
