---
layout: page
title: Quick Review
nav: true
nav_order: 6
math: true
permalink: /07_Quick_Review.html
---
<script>
  MathJax = {
    tex: {
      inlineMath: [['$$', '$$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true
    }
  };
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

## 1. Core State Variables

Every node $$i$$ at time $$t$$ is governed by four interacting state variables:

| Variable | Notation | Definition | Biological Analog |
| --- | --- | --- | --- |
| **Continuous Stress** | $$S_i(t)$$ | Instantaneous operational load on node $$i$$. | Membrane Potential |
| **Cascade Activation** | $$F_i(t)$$ | Rate of externalizing overflow stress. | Action Potential |
| **Dynamic Capacity** | $$C_i(t)$$ | Immediate structural resilience. | Synaptic Depression |
| **Baseline Target** | $$C_i^*(t)$$ | Long-term homeostatic capacity goal. | Homeostatic Plasticity |

---

## 2. The Four Continuous Dynamical Laws

These coupled, non-linear differential equations govern the microscopic behavior of the socio-technical system.

### Law I: Stress Evolution

Governs the accumulation, dissipation, and externalization of operational stress:


$$\frac{dS_i}{dt} = L_i(t) - \gamma S_i(t) + \sum_{k} \sum_{j} W_{ji}^{(k)} F_j^{(k)}(t) - \sum_{k} F_i^{(k)}(t)$$

### Law II: Differentiable Cascade Activation

Replaces the rigid step-function of classical SOC with a bounded, differentiable sigmoid threshold:


$$F_i^{(k)}(t) = \kappa^{(k)} (S_i(t) - C_i(t)) \sigma(a(S_i(t) - C_i(t)))$$


*(Where the logistic sigmoid function is $$\sigma(x) = \frac{1}{1+e^{-x}}$$)*

### Law III: Dynamic Capacity Degradation

Calculates the immediate mathematical degradation of capacity (the burnout penalty) during an active stress cascade:


$$\frac{dC_i}{dt} = \mu(C_i^*(t) - C_i(t)) - \eta \sum_{k} F_i^{(k)}(t)$$

### Law IV: Homeostatic Adaptation

The algorithmic governor that drives the system toward self-organized criticality by tuning the baseline capacity against global activity $$A(t) = \frac{1}{N}\sum_i F_i(t)$$:


$$\frac{dC_i^*}{dt} = \zeta(A_0 - A(t))$$

---

## 3. Network Topology and Conservation

### Multiplex Directed Graph

The organization is modeled across $$k$$ interaction layers (e.g., formal hierarchy vs. informal email networks):


$$G = (V, E^{(k)})$$

### Strict Normalization Condition

Ensures stress is not artificially lost during a cascade transfer:


$$\sum_i W_{ji}^{(k)} = 1$$

### Global Leaky Conservation

Summing Law I over all $$N$$ nodes cancels out internal propagation, proving the system is bounded exclusively by exogenous input and natural leak:


$$\sum_{i=1}^{N} \frac{dS_i}{dt} = \sum_{i=1}^{N} L_i(t) - \gamma \sum_{i=1}^{N} S_i(t)$$

---

## 4. Macroscopic Thermodynamics and Stability

### Systemic Entropy ($$H$$)

Quantifies the macroscopic disorder and spatial diffusion of stress. A violent spike ($$\frac{dH}{dt} \gg 0$$) serves as an early warning for network percolation:


$$H(t) = - \sum_{i=1}^{N} p_i(t) \ln(p_i(t))$$


*(Where stress probability mass is $$p_i(t) = \frac{S_i(t)}{\sum S_j(t)}$$)*

### Normative Free Energy ($$\mathcal{F}_{NSD}$$)

A pseudo-Lyapunov function measuring distance from critical energy depletion. Temperature $$\tau$$ is strictly proportional to the variance of the exogenous load ($$\tau \propto \text{Var}(L)$$):


$$\mathcal{F}_{NSD}(t) = \sum_{i=1}^{N} C_i(t) - \tau H(t)$$

### Stability Boundary Equation

The time derivative of Free Energy defines absolute Lyapunov bounds:


$$\frac{d\mathcal{F}_{NSD}}{dt} = \sum_{i=1}^{N} \left[ \mu(C_i^* - C_i(t)) - \eta \sum_{k} F_i^{(k)}(t) \right] - \tau \frac{dH}{dt}$$

### Saddle-Node Burnout Bifurcation

Setting capacity degradation to equilibrium ($$\frac{dC_i}{dt} = 0$$) reveals the deterministic collapse boundary:


$$\mu(C_i^* - C_i) = \eta \kappa \left( S_i - C_i \right) \sigma(a(S_i - C_i))$$

---

## 5. Macroscopic Approximations & Network Metrics

### Mean-Field Approximation

Collapses the $$N$$-dimensional network to isolate global behavior:


$$\frac{d\langle S \rangle}{dt} = \langle L \rangle - \gamma \langle S \rangle$$

$$\frac{d\langle C \rangle}{dt} = \mu(\langle C^* \rangle - \langle C \rangle) - \eta \langle F(\langle S \rangle, \langle C \rangle) \rangle$$

$$\frac{d\langle C^* \rangle}{dt} = \zeta(A_0 - \langle F \rangle)$$

### Key Theoretical Control Parameters

* **Systemic Control Parameter:** $$\rho = \frac{\langle L \rangle}{\langle C \rangle}$$
* **Active Branching Ratio:** $$b = \langle k \rangle P_f$$
* **Scale-Free SOC Avalanche Distribution:** $$P(s) \sim s^{-\alpha}$$
* **Random Graph Failure (Exponential Cutoff):** $$P(s) \sim s^{-\alpha} e^{-s/s_c}$$
