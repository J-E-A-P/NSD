# Normative Stress Dynamics (NSD)

**A Unified Thermodynamic Theory of Systemic Stability and Collapse**



Normative Stress Dynamics (NSD) is a continuous-time, multiplex dynamical framework that models systemic stress as a leaky, partially conserved quantity. By bridging the physics of Self-Organized Criticality (SOC) with dynamic capacity degradation (burnout), NSD provides the mathematical foundation for predicting cascading failures in highly optimized socio-technical systems. 

The framework mathematically proves that highly optimized, tightly coupled networks do not fail gradually. In the relentless pursuit of maximum operational efficiency, these systems actively self-organize toward critical thresholds, ensuring that collapse manifests as a sudden, power-law distributed topological phase transition.

## 📚 Repository Structure

This repository contains both the formal mathematical manuscripts and the empirical Python implementations of the theory.

### Theoretical Framework
1. **[Axioms of Normative Thermodynamics](_pages/01_Axioms.md):** The 4 foundational rules of leaky stress conservation and finite integration.
2. **[System Definitions & Topology](_pages/02_Definitions.md):** Formulating the multiplex directed graphs.
3. **[The Dynamical Laws](_pages/03_Dynamical_Laws.md):** The core 4-equation slow-fast dynamical system governing accumulation, non-linear activation, structural fatigue, and homeostatic tuning.
4. **[Thermodynamic Interpretation](_pages/04_Thermodynamics.md):** Defining Systemic Entropy ($H$) and Normative Free Energy ($\mathcal{F}_{NSD}$) as early-warning indicators.
5. **[Theorems of Systemic Collapse](_pages/05_Theorems.md):** Falsifiable theorems, including the Paradox of Hyper-Efficiency and Hub-Induced Hysteresis.
6. **[Full Manuscript](_pages/Normative_Stress_Dynamics_Manuscript.md):** The complete, unified whitepaper detailing the theory, proofs, and interdisciplinary applications to neurobiology and macro-governance.

### Empirical Validation
* **[Enron Case Study (Jupyter Notebook)](_pages/Enron_case_study.md):** A forensic retrodiction of the 2001 Enron collapse. This notebook maps NLP sentiment analysis (FinBERT) to physical stress dynamics, proving the organization exhibited Critical Slowing Down and Self-Organized Criticality prior to bankruptcy.

---

## Getting Started (Enron Simulation)

To run the Enron Case Study and simulate the NSD slow-fast dynamical system, you will need Python 3.10+ and the following dependencies.

### Installation

Clone the repository and install the required data science, network, and NLP libraries:

```bash
git clone [https://github.com/J-E-A-P/NSD.git](https://github.com/J-E-A-P/NSD.git)
cd NSD
pip install transformers torch pandas numpy networkx powerlaw datasets tqdm matplotlib