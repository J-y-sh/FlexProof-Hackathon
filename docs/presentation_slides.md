# FlexProof — Hackathon Presentation Slide Deck Outline

> **Event:** Schneider Electric / Yuva Yodha Energy Tech Hackathon  
> **Topic:** Predictive Neighbourhood Grid Flexibility Platform  
> **Format:** 10 Slide Executive & Technical Deck Structure

---

## 📽️ Slide 1: Title & Value Proposition
* **Header:** **FlexProof** — Predictive Neighbourhood Grid Flexibility Platform
* **Tagline:** *"Predict feeder stress before it becomes a distribution transformer failure."*
* **Team / Track:** Schneider Electric / Yuva Yodha Energy Tech Hackathon
* **Visual:** Dark slate industrial command center theme with the 5-stage coordination loop icon.

---

## 📽️ Slide 2: The Grid-Edge Problem
* **Header:** Urban Distribution Feeders Are Hitting Thermal Limits
* **Key Points:**
  * Rapid simultaneous growth in residential EV charging, rooftop solar PV, and heavy air conditioning / refrigeration.
  * Evening solar drop coincides directly with commuter arrivals and cooking/cooling spikes.
  * Local 11 kV / 415 V substation transformers experience recurrent overloads, leading to insulation degradation, tripping, and outages.
* **Metric Callout:** Unmitigated feeder peak reaches **2,621 kW** on a **2,300 kW** transformer limit (321 kW overload).

---

## 📽️ Slide 3: Why Reactive Control Falls Short
* **Header:** The Actuator Latency Trap
* **Key Points:**
  * **Reactive DERMS Flaw:** Senses overloads only *after* the transformer thermal threshold is breached.
  * **Physical Delay:** Municipal water pumps and agricultural tube-wells require **15 to 30 minutes** to spool down safely.
  * **Emergency Battery Burden:** Because slow loads cannot ramp down instantly, reactive controllers dump battery storage at emergency rates, rapidly burning cell throughput while still leaving residual unserved deficits.
* **Evidence:** In reactive mode, **14 stress intervals** remain, and battery throughput surges to **1,551 kWh**.

---

## 📽️ Slide 4: The Predictive FlexProof Solution
* **Header:** Predict $\rightarrow$ Prepare $\rightarrow$ Coordinate $\rightarrow$ Dispatch $\rightarrow$ Learn
* **Architecture Stages:**
  1. **Telemetry & Lag Ingestion:** 96-interval (24-hr) historical lookback buffer.
  2. **1-Hour Lookahead Forecaster:** Statistical multi-lag + rolling trend model ($\text{MAE} = 54.4\text{ kW}$).
  3. **Feeder Risk Radar:** Computes forecast gap over 2,300 kW limit; classifies risk into Normal, Watch, Warning, Critical.
  4. **Advance Pre-Shifting:** Deferrable loads are dispatched with 15–30 min lead time.
  5. **Precision Storage Buffering:** Community battery acts as a smooth buffer for forecast residuals.

---

## 📽️ Slide 5: System Specifications & Multi-Fleet Model
* **Header:** Grounded Physical Modeling & Asset Constraints
* **Feeder & Generation:**
  * 30 Days | 2,880 Intervals @ 15-min resolution | Firm Limit = 2,300 kW.
  * 800 kW Rooftop Solar PV with dynamic cloud attenuation.
* **Community Battery (BESS):**
  * 500 kWh Capacity | 150 kW Max Inverter Power | Safe SOC $[50\%, 90\%]$ | 95% Efficiency.
* **Flexible Load Pool (362 kW Total Flex across 5 Fleets):**
  * EV Smart Charging (140 kW flex, 15m delay)
  * Municipal Water Pumping (105 kW flex, 30m delay)
  * Agricultural Tube-Wells (60 kW flex, 30m delay)
  * HVAC Fleet (45 kW flex, 15m delay)
  * Commercial Refrigeration (12 kW flex, 15m delay)

---

## 📽️ Slide 6: 30-Day Multi-Scenario Benchmark Results
* **Header:** Proven Across 2,880 Continuous Intervals

| Operational Metric | 🔴 Baseline (Unmanaged) | 🟡 Reactive Control | 🟢 Predictive FlexProof | Predictive Advantage |
| :--- | :---: | :---: | :---: | :---: |
| **Deficit Energy** | **2,707.64 kWh** | **83.78 kWh** | **1.67 kWh** | **↓ 99.94%** *(98.00% vs. Reactive)* |
| **Stress Intervals** | **125** (31.25 hrs) | **14** (3.50 hrs) | **1** (0.25 hrs) | **↓ 99.20%** *(92.86% vs. Reactive)* |
| **Peak Feeder Demand** | **2,621.11 kW** | **2,374.19 kW** | **2,306.69 kW** | **↓ 314.42 kW** peak shaving |
| **Battery Throughput** | **0 kWh** | **1,551.02 kWh** | **741.14 kWh** | **↓ 52.2%** cycling burden reduction |
| **Flexible Energy Shifted** | **0 kWh** | **5,163.42 kWh** | **12,074.94 kWh** | **↑ 2.3×** more load flexibility |

---

## 📽️ Slide 7: Deep Causality Replay (January 12 Peak Event)
* **Header:** Advance Preparation Beats Emergency Reaction
* **Case Study Details (Jan 12 @ 18:45):**
  * **Baseline (2,621 kW):** Unmanaged demand creates a 321 kW transformer overload.
  * **Reactive (2,350 kW):** Overload detected at 18:00, but pump delay prevents relief $\rightarrow$ 50.5 kW residual deficit.
  * **Predictive FlexProof (2,300 kW):** Pre-shifted loads at 17:45. When the 18:45 peak hit, all 5 flexible fleets were active, holding net demand exactly at 2,300 kW with **zero deficit**.

---

## 📽️ Slide 8: Battery Health & Load Coordination Dividend
* **Header:** More Intelligent Coordination, Not Simply More Storage
* **Key Findings:**
  * FlexProof shifts **2.3× more flexible load energy** (12,075 kWh vs 5,163 kWh) across 256 proactive events.
  * Battery cycling throughput drops by **52.2%** (741 kWh vs 1,551 kWh), significantly reducing electrochemical cell stress.
  * **Strict Energy Conservation:** 100% of deferred load energy is safely restored during night valley hours (00:00–05:30) without triggering secondary peaks.

---

## 📽️ Slide 9: Transparent Engineering Boundaries & Safety
* **Header:** Defensible Science & Zero Exaggerated Claims
* **Explicit Limits:**
  * **Simulation Scope:** Calibrated 30-day synthetic scenario ($15\text{-min}$ resolution); proof of architectural concept.
  * **Residual Stress State:** Transparently reports **1 residual stress interval** ($1.67\text{ kWh}$, $6.69\text{ kW}$ peak) during an extreme multi-fleet coincidence peak.
  * **No Data Leakage:** Verified that forecaster receives only historical slices ($t' \le t$), with actual online $\text{MAE} = 54.38\text{ kW}$.
  * **Validation Suite:** 24 automated unit & invariant tests passing with 100% success.

---

## 📽️ Slide 10: Utility Value Proposition & Future Roadmap
* **Header:** Software-Defined Grid Resilience for the Energy Transition
* **Commercial Impact for Utilities (e.g., Schneider Electric Customers):**
  1. **Substation Capex Deferral:** Defers $\$250\text{k}\text{--}\$500\text{k}$ transformer upgrades by 5–10 years.
  2. **Storage Longevity:** Doubles community BESS cell life by eliminating unnecessary cycling bursts.
  3. **Renewable Hosting Capacity:** Maximizes local rooftop solar absorption while keeping feeders within safe thermal limits.
* **Next Engineering Steps:** Integration with OpenADR 2.0b / IEEE 2030.5 telemetry protocols and field pilot testing.
