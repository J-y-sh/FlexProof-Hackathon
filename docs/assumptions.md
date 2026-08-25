# FlexProof Engineering Assumptions & Boundary Conditions

## 1. Introduction & Engineering Philosophy

To ensure scientific integrity and defensibility for the Schneider Electric / Yuva Yodha Energy Tech Hackathon, this document transparently defines all physical, mathematical, and operational assumptions embedded within the FlexProof simulation and evaluation framework.

---

## 2. Categorized Assumptions

### A. Distribution Grid & Feeder Modeling Assumptions
1. **Lumped Single-Node Feeder Model**:
   * The distribution feeder is modeled as a lumped single-node system constrained by the continuous thermal power rating of the substation transformer ($P_{\text{firm\_limit}} = 2,300.0\text{ kW}$).
   * Spatial network topology (e.g. branch line impedances, node-by-node voltage drops, reactive power flow $Q$, power factor $\cos\phi$, phase unbalance) is not explicitly solved using AC power flow (e.g. OpenDSS/GridLAB-D). All values are active power ($P$ in $\text{kW}$).
2. **Firm Thermal Limit Enforcement**:
   * Transformer thermal inertia is approximated via the 15-minute discrete integration timestep. Transient overload capability (e.g. 110% rating for 5 minutes) is conservatively treated as a limit violation to prioritize transformer asset protection.

### B. Battery Storage Modeling Assumptions
1. **Electrochemical Representation**:
   * Community battery storage ($500.0\text{ kWh}$, $150.0\text{ kW}$) is modeled using a linear energy reservoir model with constant Coulombic/inverter efficiency ($\eta_{\text{ch}} = 0.95$, $\eta_{\text{dis}} = 0.95$).
   * Internal resistance variation ($R_{\text{int}}(T)$), open-circuit voltage curves ($V_{\text{oc}}(\text{SOC})$), and thermal runaway dynamics are not modeled.
2. **Operational Boundaries**:
   * Strict operational boundaries $\text{SOC} \in [0.50, 0.90]$ are maintained at all times to prevent deep discharge degradation and high-voltage saturation.
3. **Throughput as Cycling Burden Proxy**:
   * Cumulative throughput ($\text{kWh}$) is tracked as a proxy for battery cycling and operational stress. Cell degradation (capacity fade / SEI layer growth) is assumed proportional to throughput under identical C-rate and temperature conditions.

### C. Flexible Load & Fleet Assumptions
1. **Aggregated Fleet Control**:
   * Flexible resources are aggregated into 5 fleet categories (HVAC, EV Charging, Water Pumping, Agricultural Tube-Wells, Commercial Refrigeration) totaling $362.0\text{ kW}$ of flexible capacity.
   * Individual device switching (e.g. individual compressor duty cycles) is aggregated into continuous fleet-level power commands.
2. **Actuator Latency & Response Lags**:
   * Actuator communication and startup delays are modeled as discrete interval lags ($15\text{ minutes}$ for EV/HVAC/refrigeration, $30\text{ minutes}$ for heavy municipal water and agricultural pumps).
3. **Strict Energy Conservation**:
   * Load flexibility is strictly modeled as **deferral, not permanent curtailment**. $100\%$ of deferred energy is restored during off-peak night valley hours ($00:00\text{--}05:30$) at a rate capped at $60.0\text{ kW}$.

### D. Forecasting & Lookahead Assumptions
1. **Statistical Historical-Lag Model**:
   * The forecasting engine utilizes multi-lag features (1-day, 2-day, 7-day lags), rolling means, and trend extrapolation over a $1\text{-hour}$ horizon ($4\text{ intervals}$).
2. **Zero Look-Ahead Ground-Truth Leakage**:
   * The forecaster strictly ingests historical observations ($t' \le t$). Online tracking yields realistic forecast errors ($\text{MAE} = 54.38\text{ kW}$, $\text{RMSE} = 85.81\text{ kW}$).
3. **Lookback Cold Start**:
   * A minimum history of $96\text{ intervals}$ ($24\text{ hours}$) is required before generating predictions. During interval $0\text{--}95$, controllers operate without forecast lookahead.

### E. Synthetic Data Generation Assumptions
1. **Calibrated Indian Feeder Profiles**:
   * Demand profiles reflect characteristic Indian urban/peri-urban distributions (evening residential peak at $18:30\text{--}21:00$, commercial business day, daytime industrial load).
   * Weather variability factor ($0.90\text{--}1.10$) and solar cloud disturbances ($15\%$ probability, $30\text{--}80\%$ attenuation) simulate realistic tropical weather fluctuations.
2. **Deterministic Reproducibility**:
   * Generated with a fixed pseudorandom seed (`seed=42`), guaranteeing identical data inputs across Baseline, Reactive, and Predictive scenarios.

---

## 3. Explicit Limitations & Boundaries of Validity

| Dimension | Simulated Model (FlexProof) | Real-World Utility Deployment Requirement |
| :--- | :--- | :--- |
| **Grid Telemetry** | Deterministic synthetic time series | Substation SCADA / AMI Smart Meter streaming protocols (IEC 61850 / OpenADR) |
| **Power Flow** | Lumped active power ($P$ in $\text{kW}$) | 3-Phase unbalanced AC power flow, voltage regulation, reactive power ($Q$) support |
| **Asset Interfaces** | Simulated `FlexibleLoadManager` | IoT gateways, EVSE OCPP 2.0.1 protocols, Smart Inverter IEEE 2030.5 standards |
| **Consumer Behavior** | $100\%$ fleet compliance | Dynamic tariff pricing, customer opt-out probabilities, comfort band constraints |
| **Validation Stage** | Software-in-the-Loop simulation & invariant testing | Hardware-in-the-Loop (HIL) microgrid testbed / field pilot |
| **Forecast Engine** | Lightweight statistical lag model | Advanced ML / TFT with numerical weather prediction (NWP) API integration |

---

## 4. Claim Safety Standards

1. **No Exaggerated Prevention Claims**: FlexProof does not claim "100% outage prevention" or "zero grid failures". Across the 30-day simulation, **1 residual stress interval** ($1.67\text{ kWh}$ deficit, $6.69\text{ kW}$ peak) remains during an extreme multi-fleet coincidence peak.
2. **Defensible Battery Longevity**: FlexProof demonstrates a **$52.2\%$ reduction in battery cycling throughput**, which reduces cycling stress but is not represented as an absolute electro-chemical cell lifespan guarantee.
3. **Simulation Distinction**: All figures and findings in FlexProof documents and dashboard visualizers are clearly identified as **simulated 30-day scenario outcomes**.
