# Lecture Series A — Numerical Solution of PDEs

**Lecturer:** Prof. Dr. Peter Bastian, IWR (Interdisciplinary Center for Scientific Computing), Heidelberg University · [Google Scholar](https://scholar.google.com/citations?hl=en&user=pVZJ_NcAAAAJ&view_op=list_works&sortby=pubdate)
**When:** Mon 10:45–12:15, Tue–Fri 09:30–11:00 (21–25 Sep 2026)
**Overall theme:** *Modelling and Simulation with Partial Differential Equations*

Notes below are transcribed from the handwritten pages in this folder (`20260921_*.jpg`). One section per day; later days get appended.

---

## Day 1 — Monday, 21 September 2026

**Topics:** calculus in several variables → what a PDE is → history → gravity & the Poisson equation → the modelling cycle → conservation laws → conservation of mass → conservation of heat energy (heat equation).

### 1. Calculus recap in $\mathbb{R}^d$

Functions of $d$ variables, $x = (x_1, \dots, x_d) \in \mathbb{R}^d$.

- **Derivative (1-D):** $\displaystyle \frac{df}{dx}(x) = \lim_{\Delta x \to 0} \frac{f(x+\Delta x) - f(x)}{\Delta x}$
- **Partial derivative:** $\partial_{x_i} f$ — derivative in direction $x_i$; evaluated at a point it is a number, as a whole it is again a function.
- **Second partials:** $\partial_{x_i}\partial_{x_j} f$, in particular $\partial^2_{x_i} f = \dfrac{\partial^2 f}{\partial x_i^2}$.
- **Gradient** ($f:\mathbb{R}^d \to \mathbb{R}$): $\nabla f = \big(\partial_{x_1} f, \dots, \partial_{x_d} f\big)^{T}$ — a **vector**, so $\nabla f : \mathbb{R}^d \to \mathbb{R}^d$.
- **Divergence** ($f:\mathbb{R}^d \to \mathbb{R}^d$): $\nabla\cdot f = \partial_{x_1} f_1 + \dots + \partial_{x_d} f_d$ — a **scalar**, so $\nabla\cdot f : \mathbb{R}^d \to \mathbb{R}$.
- **Jacobian** ($f:\mathbb{R}^n \to \mathbb{R}^m$): the $m \times n$ matrix

  $$\nabla f = \begin{pmatrix} \partial_{x_1} f_1 & \cdots & \partial_{x_n} f_1 \\ \vdots & & \vdots \\ \partial_{x_1} f_m & \cdots & \partial_{x_n} f_m \end{pmatrix}$$

- **Laplacian** ($f:\mathbb{R}^d \to \mathbb{R}$): $\displaystyle \Delta f = \partial^2_{x_1} f + \dots + \partial^2_{x_d} f = \sum_{i=1}^{d} \partial^2_{x_i} f = \nabla\cdot(\nabla f)$

Summary line from the board: **divergence $\nabla\cdot f$ / gradient $\nabla f$ / Jacobian / Laplacian $\Delta f$** — these four are the building blocks of every PDE this week.

### 2. What is a PDE?

> Seek a function $f$ of several variables that has to satisfy conditions on its partial derivatives.

Example: find $f:\mathbb{R}^2 \to \mathbb{R}$ such that
$$\partial_{x_1} f + \partial_{x_2} f = g, \qquad\text{i.e.}\qquad \frac{\partial f}{\partial x_1}(x) + \frac{\partial f}{\partial x_2}(x) = g(x),$$
for a given $g:\mathbb{R}^2 \to \mathbb{R}$, posed on a **bounded domain** $\Omega \subset \mathbb{R}^2$.

Where PDEs appear: flow, heat, climate, waves, general relativity — whenever a quantity depends on **two or more** variables (space + time, or several space directions).

### 3. A little history

| Year | Who | What |
|---|---|---|
| 1757 | Euler | Euler equations (inviscid flow) |
| ≈1800 | Poisson | Poisson equation |
| 1822 | Navier | viscous flow |
| 1845 | Stokes | Navier–Stokes equations |
| 1864 | Maxwell | electromagnetism |
| 1915 | Einstein | general relativity |

- Navier–Stokes are **non-linear** equations; existence/regularity of solutions is still an open problem (the "?!" on the board).
- Computing milestone: **ASCI Red (1997)** — the ≈ $30 M supercomputer that first broke 1 TFLOP on the Linpack benchmark. Simulation at scale is what makes PDE modelling useful in practice.

### 4. From Newton's gravity to the Poisson equation

Point mass $M$ fixed at $y \in \mathbb{R}^3$, test mass $m$ at $x$:

$$F_y(x) = \frac{\gamma\, m\, M}{\|y-x\|^2}\cdot\frac{y-x}{\|y-x\|}$$

Everything is fixed except $x$, so $F_y$ is a **vector field** in $x$.

**Gravitational potential** of the point mass:
$$\psi_y(x) = -\frac{\gamma M}{\|x-y\|}, \qquad -\nabla\psi_y(x) = \frac{\gamma M\,(y-x)}{\|y-x\|^3} \quad\Rightarrow\quad F_y(x) = -m\,\nabla\psi_y(x)$$

Acceleration: $a(x) = F_y(x)/m = -\nabla\psi_y(x)$ — the force is the gradient of a scalar.

**Continuum assumption:** replace point masses by a **mass density** $\rho:\mathbb{R}^3 \to \mathbb{R}$; the mass in a region $\omega$ is $M_\omega = \int_\omega \rho(x)\,dx$.

The potential $\psi:\mathbb{R}^3 \to \mathbb{R}$ of a mass distribution satisfies

$$\boxed{\;\Delta\psi(x) = 4\pi\gamma\,\rho(x), \quad x \in \mathbb{R}^3\;}$$

— the **Poisson equation**.

**Example (boundary value problem):** two spherical bodies at $p$ and $q$,
$$\Delta\psi = 4\pi\gamma\rho \ \text{ in } \Omega, \qquad \psi = 0 \ \text{ on } \partial\Omega, \qquad
\rho(x) = \begin{cases} \rho_p & \|x-p\| \le R_p \\ \rho_q & \|x-q\| \le R_q \\ 0 & \text{else} \end{cases}$$

### 5. The modelling cycle

```
Reality ──► conceptual model ──► mathematical model ──► numerical method ──► Prediction
   ▲                                                        ▲                    │
   │                                                    data / test data         │
   └──────────────────── compare / validate ────────────────────────────────────┘
```

- Keywords: **modelling, simulation, optimisation, learning**.
- ML/AI is an alternative path from data to prediction — but needs (much) more data than a physics-based model.

### 6. PDEs from conservation laws

Setting:
- **Domain** $\Omega \subset \mathbb{R}^d$: a connected open set, $d = 1, 2, 3$.
- **Control volume** $\omega \subset \Omega$, fixed in time, with boundary $\partial\omega$ and unit outer normal $n$.
- **Mass density** $\rho(x,t):\mathbb{R}^3\times\mathbb{R} \to \mathbb{R}$, units kg/m³. Mass inside $\omega$: $M_\omega(t) = \int_\omega \rho(x,t)\,dx$.
- **Velocity** $v(x,t)$ of the material; **source/sink density** $f(x,t)$.

**Balance over $[t, t+\Delta t]$** — change of mass = mass added/removed by sources − mass that flowed out through the boundary:

$$M_\omega(t+\Delta t) - M_\omega(t) = \int_t^{t+\Delta t} \left( \int_\omega f(x,\tau)\,dx - \int_{\partial\omega} \rho(x,\tau)\, v(x,\tau)\cdot n(x)\,ds \right) d\tau$$

**Gauss's theorem** turns the surface integral into a volume integral: $\int_{\partial\omega} \rho v\cdot n\,ds = \int_\omega \nabla\cdot(\rho v)\,dx$. Differentiating in $t$:

$$\frac{d}{dt}\int_\omega \rho(x,t)\,dx + \int_\omega \nabla\cdot\big(\rho(x,t)v(x,t)\big)\,dx = \int_\omega f(x,t)\,dx$$

Since $\omega$ is arbitrary, the integrands must agree pointwise:

$$\boxed{\;\partial_t\rho + \nabla\cdot(\rho v) = f\;} \qquad\text{(conservation of mass / continuity equation)}$$

- Three unknown functions $\rho,\ v,\ f$ but only one equation → a **closure** (constitutive law) is needed; the same recipe yields momentum and energy equations.
- $f$ = source (+) / sink (−).
- **Incompressible** case: $\partial_t\rho = 0$.

### 7. Conservation of heat energy → the heat equation

Heat energy stored in $\omega$:
$$Q_\omega(t) = \int_\omega \underbrace{\rho(x,t)}_{\text{mass density}}\; c\; \underbrace{T(x,t)}_{\text{temperature}}\,dx, \qquad c = \text{specific heat}$$

Same bookkeeping as for mass, now with **two** fluxes:

$$\boxed{\;\partial_t(\rho c T) + \nabla\cdot\big(\underbrace{\rho c T\, v}_{\text{convective flux}} - \underbrace{\lambda\nabla T}_{\text{diffusive flux}}\big) + \underbrace{r\,\rho c T}_{\text{sink}} = \underbrace{f}_{\text{source}}\;}$$

- $\rho c T v$ — heat carried along with the flow (convection / advection).
- $-\lambda\nabla T$ — Fourier's law: heat flows from hot to cold, $\lambda$ = heat conductivity.
- The **same structure** describes conservation of the concentration of a substance (advection–diffusion equation).

Special cases:
- **Stationary, no sinks:** $\nabla\cdot(\rho c T v - \lambda\nabla T) = f$
- **Stationary solid body** ($v = 0$): $-\nabla\cdot(\lambda\nabla T) = f$; with constant $\lambda$:

  $$\nabla\cdot\nabla T = \Delta T = -\frac{f}{\lambda}$$

  → **Poisson's equation again.** The same PDE governs gravity and steady heat conduction.

### 8. Mentioned, to be continued

Inviscid fluid flow, groundwater flow, mass **and momentum** conservation (→ Euler / Navier–Stokes).

---

## Day 2 — Tuesday, 22 September 2026

_to be added_

## Day 3 — Wednesday, 23 September 2026

_to be added_

## Day 4 — Thursday, 24 September 2026

_to be added_

## Day 5 — Friday, 25 September 2026

_to be added_
