### CONTRIBUTING.md

This document outlines the protocol for submitting pull requests and modifying the **Normative Stress Dynamics (NSD)** framework. Because the system is a tightly coupled slow-fast dynamical model, all contributions must undergo a "topological review" to ensure they do not introduce artificial instabilities.

---

## 1. Submission Categories

### I. Mathematical Refinements

Updates to the **Continuous Four-Equation Dynamical System**.

* **Stress Evolution:** Proposed changes to Law I ($\frac{dS_i}{dt}$) must maintain **Global Leaky Conservation**.
* **Cascade Activation:** New activation functions ($F_i$) must be differentiable to allow for **Lyapunov Stability Analysis**.
* **Homeostatic Tuning:** Any modifications to Equation IV ($\eta$) must prove that the system still self-organizes to a critical branching ratio of $b=1$.

### II. Forensic Case Studies

Retrodictive analyses of organizational collapses (e.g., the Enron study).

* **Data Requirements:** Must include a timestamped stress signal (e.g., sentiment analysis or volume metadata).
* **Diagnostics:** Submissions must include **Critical Slowing Down** (AR1) and **Power Law Scaling** ($\alpha$) visualizations.

### III. Simulation & Tooling

Development of Monte Carlo or agent-based approximations of the NSD laws.

* **Separation of Scales:** Code must strictly separate the slow continuous drive from the fast-time avalanche resolution.
* **MLE Verification:** Power-law exponents must be fitted using Maximum Likelihood Estimation.

---

## 2. Review Process: The "Topological Audit"

Each contribution will be evaluated against the **Theorems of Systemic Collapse**:

1. **Axiom Check:** Does the code violate **Stress Conservation** or **Finite Integration**?
2. **Phase Analysis:** Does the contribution inadvertently push the system from the **SOC Regime** into **Chaotic Oscillation** (excessive $\eta$)?
3. **Hysteresis Validation:** If the code affects capacity degradation, does it correctly model the **Saddle-Node Bifurcation** and the resulting recovery hysteresis?

---

## 3. Communication Conduct

* **Citations Required:** All theoretical assertions must cite the relevant NSD axiom or dynamical law.
* **Thermodynamic Work:** Be prepared to perform "institutional recovery" (editing) if your PR introduces high systemic entropy (disorder) into the codebase.