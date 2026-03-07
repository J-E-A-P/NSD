---
layout: default
title: 07_Quick_Review
nav: true
nav_order: 6
math: true
---
## 1. Core State Variables

Every node $i$ at time $t$ is governed by four interacting state variables:

| Variable | Notation | Definition | Biological Analog |
| --- | --- | --- | --- |
| **Continuous Stress** | $S_i(t)$ | Instantaneous operational load on node $i$. | Membrane Potential |
| **Cascade Activation** | $F_i(t)$ | Rate of externalizing overflow stress. | Action Potential |
| **Dynamic Capacity** | $C_i(t)$ | Immediate structural resilience. | Synaptic Depression |
| **Baseline Target** | $C_i^*(t)$ | Long-term homeostatic capacity goal. | Homeostatic Plasticity |

---

## 2. The Four Continuous Dynamical Laws

These coupled, non-linear differential equations govern the microscopic behavior of the socio-technical system.

### Law I: Stress Evolution

Governs the accumulation, dissipation, and externalization of operational stress:


$$rac{dS_i}{dt} = L_i(t) - \gamma S_i(t) + \sum_{k} \sum_{j} W_{ji}^{(k)} F_j^{(k)}(t) - \sum_{k} F_i^{(k)}(t)$$

### Law II: Differentiable Cascade Activation

Replaces the rigid step-function of classical SOC with a bounded, differentiable sigmoid threshold:


$$F_i^{(k)}(t) = \kappa^{(k)} (S_i(t) - C_i(t)) \sigma(a(S_i(t) - C_i(t)))$$


*(Where the logistic sigmoid function is $\sigma(x) = rac{1}{1+e^{-x}}$)*

### Law III: Dynamic Capacity Degradation

Calculates the immediate mathematical degradation of capacity (the burnout penalty) during an active stress cascade:


$$rac{dC_i}{dt} = \mu(C_i^*(t) - C_i(t)) - eta \sum_{k} F_i^{(k)}(t)$$

### Law IV: Homeostatic Adaptation

The algorithmic governor that drives the system toward self-organized criticality by tuning the baseline capacity against global activity $A(t) = rac{1}{N}\sum_i F_i(t)$:


$$rac{dC_i^*}{dt} = ta(A_0 - A(t))$$

---

## 3. Network Topology and Conservation

### Multiplex Directed Graph

The organization is modeled across $k$ interaction layers (e.g., formal hierarchy vs. informal email networks):


$$G = (V, E^{(k)})$$

### Strict Normalization Condition

Ensures stress is not artificially lost during a cascade transfer:


$$\sum_i W_{ji}^{(k)} = 1$$

### Global Leaky Conservation

Summing Law I over all $N$ nodes cancels out internal propagation, proving the system is bounded exclusively by exogenous input and natural leak:


$$\sum_{i=1}^{N} rac{dS_i}{dt} = \sum_{i=1}^{N} L_i(t) - \gamma \sum_{i=1}^{N} S_i(t)$$

---

## 4. Macroscopic Thermodynamics and Stability

### Systemic Entropy ($H$)

Quantifies the macroscopic disorder and spatial diffusion of stress. A violent spike ($rac{dH}{dt} \gg 0$) serves as an early warning for network percolation:


$$H(t) = - \sum_{i=1}^{N} p_i(t) \ln(p_i(t))$$


*(Where stress probability mass is $p_i(t) = rac{S_i(t)}{\sum S_j(t)}$)*

### Normative Free Energy ($\mathcal{F}_{NSD}$)

A pseudo-Lyapunov function measuring distance from critical energy depletion. Temperature $	au$ is strictly proportional to the variance of the exogenous load ($	au \propto 	ext{Var}(L)$):


$$\mathcal{F}_{NSD}(t) = \sum_{i=1}^{N} C_i(t) - 	au H(t)$$

### Stability Boundary Equation

The time derivative of Free Energy defines absolute Lyapunov bounds:


$$rac{d\mathcal{F}_{NSD}}{dt} = \sum_{i=1}^{N} \left[ \mu(C_i^* - C_i(t)) - eta \sum_{k} F_i^{(k)}(t) 
ight] - 	au rac{dH}{dt}$$

### Saddle-Node Burnout Bifurcation

Setting capacity degradation to equilibrium ($rac{dC_i}{dt} = 0$) reveals the deterministic collapse boundary:


$$\mu(C_i^* - C_i) = eta \kappa \left( S_i - C_i 
ight) \sigma(a(S_i - C_i))$$

---

## 5. Macroscopic Approximations & Network Metrics

### Mean-Field Approximation

Collapses the $N$-dimensional network to isolate global behavior:


$$rac{d\langle S 
angle}{dt} = \langle L 
angle - \gamma \langle S 
angle$$

$$rac{d\langle C 
angle}{dt} = \mu(\langle C^* 
angle - \langle C 
angle) - eta \langle F(\langle S 
angle, \langle C 
angle) 
angle$$

$$rac{d\langle C^* 
angle}{dt} = ta(A_0 - \langle F 
angle)$$

### Key Theoretical Control Parameters

* **Systemic Control Parameter:** $
ho = rac{\langle L 
angle}{\langle C 
angle}$
* **Active Branching Ratio:** $b = \langle k 
angle P_f$
* **Scale-Free SOC Avalanche Distribution:** $P(s) \sim s^{-lpha}$
* **Random Graph Failure (Exponential Cutoff):** $P(s) \sim s^{-lpha} e^{-s/s_c}$
