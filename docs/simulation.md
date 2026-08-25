# FlexProof Simulation Methodology & Mathematical Specifications

## 1. Simulation Setup & Environmental Parameters

The FlexProof simulation framework models a representative $11\text{ kV} / 415\text{ V}$ distribution transformer feeder supplying an urban/peri-urban Indian neighbourhood over a **30-day continuous period**.

| Parameter | Configuration Value | Description |
| :--- | :---: | :--- |
| **Duration ($T$)** | `30 days` | Full monthly operational cycle |
| **Time Resolution ($\Delta t$)** | `15 minutes` ($0.25\text{ hours}$) | Standard smart meter / SCADA interval |
| **Total Intervals ($N$)** | `2,880 intervals` | $30 \text{ days} \times 24 \text{ hrs/day} \times 4 \text{ int/hr}$ |
| **Random Seed** | `42` | Enforces deterministic bit-for-bit reproducibility |
| **Feeder Firm Limit ($P_{\text{limit}}$)** | `2,300.0 kW` | Substation transformer continuous thermal limit |
| **Watch Threshold** | `75%` ($1,725.0\text{ kW}$) | Feeder loading early advisory threshold |
| **Warning Threshold** | `85%` ($1,955.0\text{ kW}$) | Predictive pre-dispatch preparation threshold |
| **Critical Threshold** | `95%` ($2,185.0\text{ kW}$) | High-urgency load shifting threshold |

---

## 2. Demand & Renewable Generation Models

### A. Synthetic Feeder Demand Decomposition
Total feeder baseline demand at interval $t$ is the sum of three distinct sectoral components:

$$P_{\text{demand}}(t) = P_{\text{res}}(t) + P_{\text{com}}(t) + P_{\text{ind}}(t)$$

1. **Residential Demand ($P_{\text{res}}$)**:
   * Peak Capacity: $1,635.0\text{ kW}$.
   * Diurnal Profile: Off-peak night ($00:00\text{--}05:00$), morning breakfast ramp ($05:00\text{--}09:00$), moderate daytime ($09:00\text{--}16:00$), and prominent evening peak ($17:30\text{--}21:30$) reflecting cooking, lighting, and cooling loads.
   * Multipliers: Daily weather/temperature variation factor ($0.90\text{--}1.10$) and weekend lifestyle uplift ($+5\%$).
   * Additive Gaussian noise: $\sigma = 2\%$.
2. **Commercial Demand ($P_{\text{com}}$)**:
   * Peak Capacity: $650.0\text{ kW}$.
   * Diurnal Profile: Business hours opening ramp ($07:00\text{--}09:00$), afternoon commercial peak ($12:00\text{--}17:00$), post-market drop ($19:30\text{--}22:00$).
   * Multipliers: Reduced activity on Saturday ($60\%$) and Sunday ($35\%$).
   * Additive Gaussian noise: $\sigma = 2\%$.
3. **Industrial Demand ($P_{\text{ind}}$)**:
   * Peak Capacity: $450.0\text{ kW}$.
   * Diurnal Profile: Consistent single/double shift manufacturing ($08:00\text{--}19:00$) with reduced weekend operation.
   * Additive Gaussian noise: $\sigma = 2\%$.

### B. Distributed Solar PV Generation
Solar generation is modeled using a solar zenith angle approximation over daylight hours ($06:00\text{--}18:30$):

$$P_{\text{solar\_ideal}}(t) = P_{\text{solar\_cap}} \times \left[ \cos\left( \frac{h(t) - 12.25}{6.25} \times \frac{\pi}{2} \right) \right]^{1.5}$$

* **Solar PV Capacity ($P_{\text{solar\_cap}}$)**: $800.0\text{ kW}$.
* **Cloud Attenuation**: Cloud events occur with probability $p = 0.15$, reducing irradiance by $30\%\text{ to }80\%$.
* **Daily Irradiance Factor**: Multiplier in the range $[0.85, 1.00]$.
* **Physical Constraint**: $P_{\text{solar}}(t) \ge 0.0\text{ kW}$ strictly enforced.

### C. Unmitigated Net Demand
The net electrical load imposed on the substation feeder is:

$$P_{\text{net\_baseline}}(t) = P_{\text{demand}}(t) - P_{\text{solar}}(t)$$

---

## 3. Physical Asset Specifications

### A. Community Battery Storage System (BESS)
The feeder is equipped with a centralized community battery modeled with thermodynamic energy conservation:

| Battery Parameter | Value | Constraint / Formula |
| :--- | :---: | :--- |
| **Energy Capacity ($C$)** | `500.0 kWh` | Nominal nameplate storage capacity |
| **Max Charge Power ($P_{\text{ch\_max}}$)** | `150.0 kW` | Power electronics inverter rating |
| **Max Discharge Power ($P_{\text{dis\_max}}$)** | `150.0 kW` | Power electronics inverter rating |
| **Minimum Safe SOC ($\text{SOC}_{\min}$)** | `0.50` ($50\%$) | Operational lower boundary constraint |
| **Maximum Safe SOC ($\text{SOC}_{\max}$)** | `0.90` ($90\%$) | Operational upper boundary constraint |
| **Initial SOC ($\text{SOC}_0$)** | `0.70` ($70\%$) | Starting state of charge |
| **Charge Efficiency ($\eta_{\text{charge}}$)** | `0.95` ($95\%$) | Electrochemical & thermal charging efficiency |
| **Discharge Efficiency ($\eta_{\text{discharge}}$)** | `0.95` ($95\%$) | Electrochemical & thermal discharging efficiency |

**Energy Transition Dynamics**:
* **Charging ($P_{\text{ch}} > 0$)**:
  $$E(t + \Delta t) = \min\left( E(t) + P_{\text{ch}}(t) \cdot \Delta t \cdot \eta_{\text{charge}}, \ \text{SOC}_{\max} \cdot C \right)$$
* **Discharging ($P_{\text{dis}} > 0$)**:
  $$E(t + \Delta t) = \max\left( E(t) - \frac{P_{\text{dis}}(t) \cdot \Delta t}{\eta_{\text{discharge}}}, \ \text{SOC}_{\min} \cdot C \right)$$

### B. Flexible Load Fleets
Flexible loads represent aggregated deferrable equipment distributed across the neighbourhood:

| Resource Fleet | Fleet Size | Unit Power | Total Power | Flex Fraction | Available Flex | Duration Range | Response Delay | Priority |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **HVAC Fleet** | 30 units | $3.0\text{ kW}$ | $90.0\text{ kW}$ | $50\%$ | **$45.0\text{ kW}$** | $1\text{--}4\text{ int}$ ($15\text{--}60\text{ min}$) | $1\text{ int}$ ($15\text{ min}$) | 1 (First) |
| **EV Smart Charging** | 25 chargers | $7.0\text{ kW}$ | $175.0\text{ kW}$ | $80\%$ | **$140.0\text{ kW}$** | $2\text{--}8\text{ int}$ ($30\text{--}120\text{ min}$) | $1\text{ int}$ ($15\text{ min}$) | 2 |
| **Municipal Water Pumping** | 10 pumps | $15.0\text{ kW}$ | $150.0\text{ kW}$ | $70\%$ | **$105.0\text{ kW}$** | $4\text{--}16\text{ int}$ ($1\text{--}4\text{ hrs}$) | $2\text{ int}$ ($30\text{ min}$) | 3 |
| **Agricultural Tube-Wells** | 5 pumps | $20.0\text{ kW}$ | $100.0\text{ kW}$ | $60\%$ | **$60.0\text{ kW}$** | $4\text{--}12\text{ int}$ ($1\text{--}3\text{ hrs}$) | $2\text{ int}$ ($30\text{ min}$) | 3 |
| **Commercial Refrigeration** | 8 units | $5.0\text{ kW}$ | $40.0\text{ kW}$ | $30\%$ | **$12.0\text{ kW}$** | $1\text{--}2\text{ int}$ ($15\text{--}30\text{ min}$) | $1\text{ int}$ ($15\text{ min}$) | 4 (Last) |
| **TOTAL FLEET POOL** | **78 assets** | — | **$555.0\text{ kW}$** | — | **$362.0\text{ kW}$** | — | — | — |

**Actuator Response Time Lag Enforcement**:
For any shift requested at interval $t_{\text{start}}$ with response delay $d$ intervals:

$$\Delta P_{\text{flex}}(t) = 0 \quad \forall \ t < t_{\text{start}} + d$$

$$\Delta P_{\text{flex}}(t) = P_{\text{shift}} \quad \forall \ t_{\text{start}} + d \le t < t_{\text{start}} + D$$

---

## 4. Performance Metric Formulas

### A. Instantaneous Deficit Power ($P_{\text{deficit}}$)
$$P_{\text{deficit}}(t) = \max\left( 0, \ P_{\text{controlled\_net}}(t) - P_{\text{limit}} \right)$$

### B. Total Deficit Energy ($E_{\text{deficit}}$)
$$E_{\text{deficit}} = \sum_{t=1}^{N} P_{\text{deficit}}(t) \cdot \Delta t \quad [\text{kWh}]$$

### C. Feeder Stress Intervals & Duration
$$N_{\text{stress}} = \sum_{t=1}^{N} \mathbb{I}\left( P_{\text{controlled\_net}}(t) > P_{\text{limit}} \right) \quad [\text{intervals}]$$

$$T_{\text{stress}} = N_{\text{stress}} \cdot \Delta t \quad [\text{hours}]$$

### D. Battery Cycling Throughput ($E_{\text{throughput}}$)
$$E_{\text{throughput}} = \sum_{t=1}^{N} \left( E_{\text{stored}}(t) + E_{\text{delivered}}(t) \right) \quad [\text{kWh}]$$

### E. Relative Scenario Improvements
$$\text{Deficit Reduction (\%)} = \frac{E_{\text{def, baseline}} - E_{\text{def, controlled}}}{E_{\text{def, baseline}}} \times 100\%$$

$$\text{Predictive Advantage (\%)} = \frac{E_{\text{def, reactive}} - E_{\text{def, predictive}}}{E_{\text{def, reactive}}} \times 100\%$$

$$\text{Battery Throughput Reduction (\%)} = \frac{E_{\text{thr, reactive}} - E_{\text{thr, predictive}}}{E_{\text{thr, reactive}}} \times 100\%$$
