---
layout: page
title: Thermodynamics
nav: true
nav_order: 4
math: true
permalink: /04_Thermodynamics.html
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

# Thermodynamic Interpretation

NSD maps structural and stress distributions to statistical mechanical concepts to mathematically evaluate global stability.

## 1. Systemic Entropy ($$H$$)
Entropy quantifies the disorder and diffusion of stress across the network. Let the instantaneous stress probability mass of node $$i$$ be $$p_i(t) = \frac{S_i(t)}{\sum S_j(t)}$$. 
$$H(t) = - \sum_{i=1}^{N} p_i(t) \ln(p_i(t))$$
A sharp acceleration in entropy ($$\frac{dH}{dt} \gg 0$$) serves as a computable early-warning indicator of impending topological phase transitions.

## 2. Normative Free Energy ($$\mathcal{F}_{NSD}$$)
We introduce $$\mathcal{F}_{NSD}$$ as a **Lyapunov candidate function** representing the total usable structural resilience of the system. Let systemic "Temperature" ($$\tau$$) be the variance of the exogenous load ($$\text{Var}(L)$$).
$$\mathcal{F}_{NSD}(t) = \sum_{i=1}^{N} C_i(t) - \tau H(t)$$
Under bounded load injection and strictly positive dissipation, the system is subcritical and globally stable if and only if:
$$\frac{d\mathcal{F}_{NSD}}{dt} \le 0$$
Collapse is triggered when $$\mathcal{F}_{NSD}(t) < \sum S_i(t)$$.

## 3. The Burnout Bifurcation (Saddle-Node Transition)
Setting $$\frac{dC_i}{dt} = 0$$ reveals the steady-state equilibrium:
$$\mu(C_i^* - C_i) = \eta \kappa \left( S_i - C_i \right) \sigma(a(S_i - C_i))$$
As $$S_i$$ increases, a **saddle-node bifurcation** occurs. The stable high-capacity ("Healthy") equilibrium collides with an unstable intermediate equilibrium and vanishes. The node is deterministically pulled into a degraded, low-capacity attractor ("Burnout", $$C_i \to 0$$).
