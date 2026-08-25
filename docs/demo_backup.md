# FlexProof — Live Demonstration Backup & Recovery Protocol

> **Purpose:** Disaster Recovery & Quick-Reference Manual for Live Judging Sessions  
> **Platform:** Streamlit Command Center (`dashboard/app.py`)

---

## ⚡ 1. Primary Demo Launch Procedure

### Standard Launch Command
```bash
python -m streamlit run dashboard/app.py
```
* **Browser URL:** `http://localhost:8501`
* **Default Mode:** `🎯 Hackathon Live Pitch Mode` is active by default.

---

## 🛠️ 2. Disaster Recovery & Troubleshooting

### Scenario A: "Port 8501 is not available"
If another process or a previous Streamlit session is holding port 8501:
```bash
# Option 1: Launch on an alternative port
python -m streamlit run dashboard/app.py --server.port 8502

# Option 2: Kill existing python processes (PowerShell)
Get-Process -Name python | Stop-Process -Force
```

### Scenario B: "Processed scenario data not found"
If `data/processed/` files are accidentally removed or deleted:
```bash
# Regenerate all 5 scenario CSVs in ~1.5 seconds
python run.py
```
* **Required Files Verified in `data/processed/`:**
  * `baseline.csv` (2,880 intervals of unmanaged telemetry)
  * `reactive.csv` (2,880 intervals of threshold control)
  * `predictive.csv` (2,880 intervals of FlexProof coordination)
  * `reactive_events.csv` (95 discrete reactive controller actions)
  * `predictive_events.csv` (256 discrete predictive pre-shift actions)

### Scenario C: Offline Network Environment
* **FlexProof is 100% Local & Self-Contained:**
  * Zero external API dependencies (no OpenAI/Gemini/Cloud calls during live simulation).
  * Plotly and Streamlit render locally without requiring internet access.

---

## 📊 3. Verbal Metric Cheat Sheet (If Display Fails)

If a screen-sharing or projector glitch occurs during judging, recite these locked figures:

| Metric | 🔴 Baseline (Unmanaged) | 🟡 Reactive Control | 🟢 Predictive FlexProof | Key Takeaway |
| :--- | :---: | :---: | :---: | :--- |
| **Deficit Energy** | **2,707.64 kWh** | **83.78 kWh** | **1.67 kWh** | **↓ 99.94% reduction** (98.0% vs. Reactive) |
| **Stress Intervals** | **125** (31.25 hrs) | **14** (3.50 hrs) | **1** (0.25 hrs) | **↓ 99.20% reduction** in overload time |
| **Peak Feeder Demand** | **2,621.11 kW** | **2,374.19 kW** | **2,306.69 kW** | **↓ 314.42 kW** peak shaving |
| **Battery Throughput** | **0.00 kWh** | **1,551.02 kWh** | **741.14 kWh** | **↓ 52.2% less battery cycling burden** |
| **Flexible Energy Shifted** | **0.00 kWh** | **5,163.42 kWh** | **12,074.94 kWh** | **2.3× more flexible load energy used** |
| **Dispatch Events** | **0** | **95** | **256** | Proactive pre-shifts vs. reactive panic |

---

## 🎯 4. Peak Event Reference (January 12 @ 18:45)

* **Baseline Peak:** $2,621.11\text{ kW}$ ($321.11\text{ kW}$ overload over $2,300\text{ kW}$ firm limit).
* **Reactive Peak:** $2,350.50\text{ kW}$ ($50.50\text{ kW}$ residual deficit due to $30\text{-minute}$ pump latency).
* **Predictive FlexProof:** $2,300.00\text{ kW}$ ($0.00\text{ kW}$ deficit via $17:45$ advance load pre-shifting).
* **Core Takeaway:** *"Advance resource preparation beats emergency reaction every single time."*
