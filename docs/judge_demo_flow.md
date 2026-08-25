# FlexProof — Live Judge Demonstration Click-by-Click Flow

> **Target Time:** 5 Minutes  
> **Interface:** Streamlit Command Center (`streamlit run dashboard/app.py`)

---

## 🖥️ Step-by-Step Screenplay

### STEP 1: Launch the Application
* **Action:** Open terminal and run:
  ```bash
  streamlit run dashboard/app.py
  ```
* **Verify:** Browser opens to `http://localhost:8501`. Ensure the dark slate industrial energy theme is visible.

---

### STEP 2: Verify Sidebar State
* **Action:** Check the sidebar on the left.
* **Confirm:**
  * `🎯 Hackathon Live Pitch Mode` toggle is **ON** (default).
  * `Pitch Navigation` is set to `🏆 Executive / Judge Pitch` (default).
  * Feeder Specifications are visible (Firm Limit: `2,300 kW`, Solar: `800 kW`, Battery: `500 kWh`).

---

### STEP 3: Hero Section & Problem Statement
* **Action:** Point your cursor to the **Executive Hero Section** at the top of the main viewport.
* **Point at:**
  1. Title: *FLEXPROOF COMMAND CENTER — "Predict feeder stress before it becomes a distribution transformer failure."*
  2. The 3 Outcome Cards:
     * 🔴 Baseline: **125 stress intervals | 2,707.6 kWh deficit**
     * 🟡 Reactive: **14 stress intervals | 83.8 kWh deficit**
     * 🟢 Predictive: **1 residual stress interval | 1.67 kWh deficit**
  3. Core Breakthrough Callout: **99.94% deficit reduction | 52.2% less battery throughput**.
* **Say:**
  > *"Judges, distribution feeders across India face severe evening congestion as EV charging and AC loads spike right as solar generation drops. Reactive systems only detect overloads after they happen, but water pumps and agricultural wells have 15 to 30-minute response delays. By the time reactive control responds, transformers overheat and batteries are drained. FlexProof forecasts net demand 1 hour ahead to pre-shift loads and coordinate storage before stress arrives."*

---

### STEP 4: "Why FlexProof?" Control Progression Story
* **Action:** Scroll down slightly to the 3 **"Why FlexProof?"** strategy cards.
* **Point at:**
  * Stage 1: *Baseline (Unmanaged)* $\rightarrow$ 125 intervals of unmitigated overload.
  * Stage 2: *Reactive Control* $\rightarrow$ The Actuator Delay Trap & emergency battery drain.
  * Stage 3: *Predictive FlexProof* $\rightarrow$ 1-hour lookahead, advance pre-shifting, and gentle precision buffering.
* **Say:**
  > *"Here is the architectural progression: Baseline absorbs uncontrolled peaks. Reactive control senses the breach at the limit, but actuator delays leave 14 stress intervals and force heavy battery cycling. Predictive FlexProof pre-shifts slow loads ahead of response delays, cutting unserved deficit by 99.94% with half the battery cycling."*

---

### STEP 5: Replay the Peak Stress Event (Jan 12)
* **Action:** In the sidebar navigation, click on **`🔍 Stress Event Replay`** (or scroll to the Event Replay section on the main pitch page).
* **Point at:**
  * Dropdown selector: Pre-selected to **`Jan 12, 2024 (Fri) 18:45 — Peak Overload: 321.1 kW`**.
  * Multi-subplot timeline:
    1. *Top Subplot*: Red dotted line (Baseline = 2,621 kW) vs. Yellow line (Reactive = 2,350 kW) vs. Green line (FlexProof = 2,300 kW).
    2. *Middle Subplot*: Green bars showing flexibility dispatched in advance at 17:45 before the peak hits.
    3. *Bottom Subplot*: Battery SOC dipping smoothly under FlexProof vs. aggressive reactive plunge.
  * Step-by-step Causality Audit Cards below the chart.
* **Say:**
  > *"Here is our worst stress event of the month on January 12th. Baseline demand surges to 2,621 kW—a 321 kW overload. Reactive control detected the overload at 18:00, but pump delays kept demand at 2,350 kW (a 50.5 kW deficit). FlexProof anticipated the ramp at 17:30 and pre-shifted loads at 17:45. When the peak arrived, all 5 flexible fleets were active, holding net demand exactly at 2,300 kW with zero deficit. Advance preparation beats reactive response every single time."*

---

### STEP 6: Multi-Scenario Scorecard & Battery Longevity
* **Action:** In the sidebar, click on **`📊 Full Benchmark Scorecard`** (or return to pitch view).
* **Point at:**
  * Scorecard Table:
    * Deficit Energy: `2,707.6 kWh` $\rightarrow$ `83.8 kWh` $\rightarrow$ `1.67 kWh` (**↓ 99.94%**).
    * Stress Duration: `31.25 hrs` $\rightarrow$ `3.50 hrs` $\rightarrow$ `0.25 hrs` (**↓ 99.20%**).
    * Battery Cycling: `1,551 kWh` $\rightarrow$ `741 kWh` (**↓ 52.2%**).
    * Flexible Energy Shifted: `5,163 kWh` $\rightarrow$ `12,075 kWh` (**↑ 2.3×**).
  * 30-Day Cumulative Deficit Curve: Red and Yellow lines rising steeply; Green line staying flat along the x-axis.
* **Say:**
  > *"Notice how the cumulative deficit curve for FlexProof remains essentially flat across the entire 30 days. And FlexProof achieves this not by relying on a massive battery, but by shifting 2.3× more flexible load energy. This cuts battery cycling throughput by 52.2%, directly extending the operating life of expensive substation storage cells."*

---

### STEP 7: Transparent Engineering Boundaries & Conclusion
* **Action:** Point to the footer and wrap up.
* **Say:**
  > *"We pride ourselves on transparent engineering: our model evaluates a 30-day calibrated synthetic scenario at 15-minute resolution with 24 passing unit tests. We report our 1 residual stress interval honestly. FlexProof provides electric utilities with a software-defined path to defer substation capex, protect community storage, and keep neighbourhood grids resilient. Thank you."*
