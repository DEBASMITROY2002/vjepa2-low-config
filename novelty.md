# Symmetry-Constrained V-JEPA (SC-JEPA)  
### Geometric Regularization for Zero-Shot Robot Planning

---

## Abstract

I propose **Symmetry-Constrained V-JEPA (SC-JEPA)**, a novel self-supervised framework designed to enhance the physical plausibility of Video Joint Embedding Predictive Architectures (V-JEPA). My core hypothesis is that standard autoregressive models fail to capture the underlying **Lie Group symmetries** of robot motion, leading to accumulated drift. I propose enforcing **Transitivity (Composition)** and **Invertibility (Cycle Consistency)** constraints directly onto the latent predictor. This approach aims to regularize the latent space, enabling robust **zero-shot Model Predictive Control (MPC)** without requiring additional training data.

---

## 1. Motivation: Solving the Drift Problem

In my analysis of standard autoregressive world models like **V-JEPA 2**, I identified a critical limitation: they learn temporal dynamics purely through forward prediction,

\[
z_{t+1} = P(z_t, a_t)
\]

While effective for short horizons, this approach treats physics as a sequence of arbitrary transitions rather than a structured system governed by geometric algebra.

When I apply zero-shot planning (e.g., via the Cross-Entropy Method) to these models, I observe two major failure modes:

- **Drift**: Small prediction errors accumulate rapidly, causing the imagined state to diverge from physical reality.
- **Non-Reversibility**: The model frequently imagines trajectories that violate kinematic constraints, such as *teleporting* through obstacles.

### My Solution

I propose to solve this by enforcing two rigid-body constraints directly in the latent space:

- **Compositionality**  
  \[
  P(P(z, a_1), a_2) \equiv P(z, a_1 \oplus a_2)
  \]

- **Invertibility**  
  \[
  P(P(z, a), a^{-1}) \equiv z
  \]

---

## 2. Framework Overview

### Baseline Architecture

I build upon the **V-JEPA 2-AC architecture**. This model predicts latent video embeddings (\(z\)) from a frozen context encoder (\(h\)) conditioned on action vectors (\(A\)). The predictor \(P_\phi\) acts as my differentiable physics simulator.

> **[INSERT FIGURE 1 HERE: The Original V-JEPA 2 Framework]**  
> *Caption:* The baseline V-JEPA 2 inference flow. The predictor \(P_\phi\) autoregressively predicts future latent states given a context and action history.

---

## 3. Proposed Methodology

I introduce two auxiliary loss functions that operate on arbitrary time horizons \(t_a, t_b, t_c\). I employ a **hybrid loss strategy**, ensuring that auto-regressive rollouts are grounded in reality while enforcing that single-step *jumps* remain consistent with those rollouts.

---

### Novelty I: The Transitivity Constraint (Hybrid Consistency)

**My Assumption:**  
I posit that the latent predictor must be **resolution-independent**. Whether I predict the future state \(h_c\) via a sequence of small steps (\(t_a \to t_b \to t_c\)) or one large jump (\(t_a \to t_c\)), the resulting physics must be consistent.

> **[INSERT FIGURE 2 HERE: The Transitivity / Composition Constraint]**  
> *Caption:* I enforce that the sequential prediction path (Top) aligns with the direct composite *jump* path (Bottom). The loss minimizes the divergence between these two latent representations.

#### Mathematical Formulation

I sample timestamps \(t_a < t_b < t_c\).

**Path 1 (Sequential):**  
I roll out the predictor auto-regressively using accumulated actions \(A_{ab}\) and \(A_{bc}\):

\[
z_{c\_seq} = P_\phi(P_\phi(h_a, A_{ab}), A_{bc})
\]

**Path 2 (Direct):**  
I predict the target directly using the composite action \(A_{ac}\):

\[
z_{c\_jump} = P_\phi(h_a, A_{ac})
\]

**The Loss:**

\[
L_{comp} =
\underbrace{\| z_{c\_seq} - h_c \|^2}_{\text{Grounding Loss}} +
\underbrace{\| z_{c\_seq} - z_{c\_jump} \|^2}_{\text{Internal Consistency}}
\]

---

### Novelty II: Bi-Directional Cycle Consistency (Dual-Source Inversion)

**My Assumption:**  
Kinematic physics is **locally reversible**. If my model imagines a transition forward, applying the inverse action must recover the original state. This acts as a powerful regularizer against *hallucinating* physically impossible moves.

> **[INSERT FIGURE 3 HERE: The Bi-Directional Cycle Constraint]**  
> *Caption:* I enforce reversibility on both the imagined future (Path 1) and the ground-truth future (Path 2). Both inverse predictions must recover the start state \(h_a\).

#### Mathematical Formulation

Let \(A_{fwd}\) be the action from \(t_a \to t_b\).

**Path 1 (The Yo-Yo):**  
I predict forward to generate an imagined future \(\hat{z}_b\), then predict backward using \(A_{inv}\):

\[
\hat{h}_{cycle} = P_\phi(\hat{z}_b, A_{inv})
\]

**Path 2 (Ground Truth Inversion):**  
I take the real future encoding \(h_b\) and predict backward:

\[
\hat{h}_{inverse} = P_\phi(h_b, A_{inv})
\]

**The Loss:**

\[
L_{cycle} =
\underbrace{\| \hat{h}_{cycle} - h_a \|^2}_{\text{Internal Reversibility}} +
\underbrace{\| \hat{h}_{inverse} - h_a \|^2}_{\text{Ground Truth Reversibility}}
\]

---

## 4. Technical Implementation: Action Algebra

To implement these constraints effectively while maintaining the gradient graph (via shallow copying), I define the action composition and inversion operations specifically for the **DROID dataset’s delta-action space**.

### A. Computing Composite Actions (\(A_{ac}\))

I calculate the *jump* action by summing the slices of the original tensor. This ensures gradients propagate back through the original atomic actions:

\[
A_{ac} = A_{ab} + A_{bc}
\]

### B. Computing Inverse Actions (\(A_{inv}\))

Since the action \(A\) describes a vector displacement (\(\vec{v}\)), the inverse is the negation:

\[
A_{inv} = -A
\]

---

## 5. Final Objective Function

To train the model, I integrate the standard JEPA prediction loss with my geometric regularizers. This unified objective forces the model to balance visual reconstruction with structural geometric integrity:

\[
L_{total} = L_{JEPA} + \lambda_1 L_{comp} + \lambda_2 L_{cycle}
\]

where \(\lambda_1\) and \(\lambda_2\) are hyperparameters controlling the strength of the geometric regularization.

---

## 6. Expected Impact

By integrating **SC-JEPA**, I expect to see a significant reduction in drift for long-horizon planning tasks compared to the vanilla V-JEPA baseline. This proposal shifts the paradigm from simply *learning from video* to **learning the geometry of motion**, providing a mathematical guarantee of consistency that is critical for zero-shot deployment in unstructured environments.

---
