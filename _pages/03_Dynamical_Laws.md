---
layout: page
title: The Dynamical Laws of NSD
nav: true
nav_order: 3
math: true
permalink: /03_Dynamical_Laws.html
toc:
  sidebar: left
---

The core of the theory is a three-equation slow-fast dynamical system governing continuous accumulation, non-linear activation, and structural degradation.

## Law 1: Stress Evolution (The Slow Drive)
Stress accumulates via exogenous load, dissipates naturally over time, and redistributes rapidly during network cascades:
$$\\frac{dS_i}{dt} = L_i(t) - \gamma S_i(t) + \sum_{k} \sum_{j} W_{ji}^{(k)} F_j^{(k)}(t) - \sum_{k} F_i^{(k)}(t)$$
Where $$\gamma$$ is the natural localized dissipation rate.

## Law 2: Differentiable Cascade Activation (The SOC Trigger)
Nodes become highly contagious sources of stress only when $$S_i(t) \gg C_i(t)$$. We define a smooth, differentiable activation function to permit Lyapunov stability analysis:
$$F_i^{(k)}(t) = \kappa^{(k)} (S_i(t) - C_i(t)) \sigma(a(S_i(t) - C_i(t)))$$
Where $$\sigma(x) = \\frac{1}{1+e^{-x}}$$, $$\kappa^{(k)}$$ is the propagation speed in layer $$k$$, and $$a$$ dictates the threshold sharpness. As $$a \to \infty$$, this recovers the hard boundary of classical sandpile models.

## Law 3: Dynamic Capacity Degradation (Structural Fatigue)
Capacity is not static. It naturally recovers toward a healthy baseline $$C_i^*$$ but suffers immediate, permanent degradation when forced to cascade stress:
$$\\frac{dC_i}{dt} = \mu(C_i^* - C_i(t)) - \eta \sum_{k} F_i^{(k)}(t)$$
Where $$\mu$$ is the institutional recovery rate and $$\eta$$ is the burnout penalty.

## Law 4: Global Leaky Conservation
By summing Law 1 over all $$N$$ nodes and applying the topological normalization condition, the internal propagation terms strictly cancel out:
$$\sum_{i=1}^{N} \\frac{dS_i}{dt} = \sum_{i=1}^{N} L_i(t) - \gamma \sum_{i=1}^{N} S_i(t)$$
This mathematically proves the system is globally conserved with localized dissipation.
