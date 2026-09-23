# Lecture Series B — Modelling & Parameter Estimation for ODEs

**Lecturer:** Dr. Michael Winckler, IWR (Interdisciplinary Center for Scientific Computing), Heidelberg University · [Google Scholar](https://scholar.google.com/citations?hl=en&user=0pg-x-EAAAAJ&view_op=list_works&sortby=pubdate)
**When:** Mon 14:00–15:30, Tue–Fri 11:15–12:45 (21–25 Sep 2026)

Notes below are transcribed from the handwritten pages in this folder (`20260921_*.jpg`). One section per day; later days get appended. Code lives in the notebooks next to this file.

---

## Day 1 — Monday, 21 September 2026

**Topics:** modelling with a single variable → a growth model → the sin–cos model → Euler's method and its error → formal definition of ODE and initial value problem.

### 1.1 Modelling with ODEs (single variable)

#### 1.1.1 Growth model

Measured data (e.g. size of a cell colony):

| $t$ | 0 | 5 | 10 |
|---|---|---|---|
| $A$ | 1 | 2.3 | 5.5 |

Ratio between consecutive values ≈ 2.3, ≈ 2.4 → **multiplicative** growth. Discretely:
$$u_0 = 1,\quad u_1 = 2.3,\quad u_2 = 5.5,\quad u_N \approx (2.3)^N \cdot 1$$

Sketch: a **vector field** (direction field) in the $(t, A)$ plane — the slope gets steeper the larger $A$ is.

Continuous model — rate of change proportional to the current amount:
$$\boxed{\;u'(t) = \alpha\, u(t)\;}$$

Check $u(t) = u_0 e^{\alpha t}$: $\;u'(t) = \alpha u_0 e^{\alpha t} = \alpha\, u(t)$ ✓ — so $u(t) = u_0 e^{\alpha t}$ is **one** solution (the initial value $u_0$ picks it out).

#### 1.1.2 The sin–cos model

We know $\sin'(t) = \cos(t)$ and $\cos'(t) = -\sin(t)$. Set $u_1 = \sin$, $u_2 = \cos$:

$$\begin{pmatrix} u_1 \\ u_2 \end{pmatrix}' = \begin{pmatrix} u_2 \\ -u_1 \end{pmatrix} = f(t, u_1, u_2), \qquad u_1(0) = \sin 0 = 0,\quad u_2(0) = \cos 0 = 1$$

Motivation: compute $\sin(0.6)$ (or any value) **without** knowing the sine function — by solving this ODE numerically. This is a first-order **system** of two equations; the notebook below does exactly this.

### 1.2 Euler's method

Notation: $u$ = exact (analytic) solution of the ODE, $y$ = approximate (numerical) solution.

Problem: $u'(t) = f(t, u)$, $u(t_0) = u_0$. Choose a step size $h$.

$$y_1 = u_0 + h\, f(t_0, u_0) \;\approx\; u(t_0 + h)$$
$$y_2 = y_1 + h\, f(t_0 + h,\ y_1), \qquad \dots, \qquad \boxed{\;y_{k+1} = y_k + h\, f(t_k, y_k)\;}$$

**Why it works (Exp. 1).** Taylor expansion around $t_0$:
$$u(t) = u_0 + u'(t_0)(t-t_0) + \frac{(t-t_0)^2}{2}\,u''(\xi) = u_0 + f(t_0,u_0)(t-t_0) + \frac{(t-t_0)^2}{2}\,u''(\xi)$$
Euler keeps the linear term and drops the rest. Equivalently, in integral form
$$u(t) = u_0 + \int_{t_0}^{t} f(\tau, u(\tau))\,d\tau$$
Euler replaces the integral by a rectangle of width $h$ and height $f(t_0,u_0)$ (the hatched area in the sketch).

**How good is Euler?**
- One step: $u(t_{n+1}) = u(t_n) + h\,f(t_n,u_n) + \dfrac{h^2}{2}\,u''(\xi)$, $\ t_n \le \xi \le t_{n+1}$ → local error $O(h^2)$.
- After $N = (t_E - t_0)/h$ steps the errors accumulate: $\boxed{\;y(t_E) = u(t_E) + O(h)\;}$ → **first order**: halving $h$ halves the error.

### 1.3 Definitions

**DEF (ODE).** Let $u:\mathbb{R} \to \mathbb{R}^d$ be a function defined on an interval $I \subset \mathbb{R}$. An *ordinary differential equation* is an equation on $u(t)$ and its derivatives:
$$F\big(t,\ u(t),\ u'(t),\ u''(t),\ \dots,\ u^{(n)}(t)\big) = 0$$
Usually the equation is **explicit** in the highest derivative: $u^{(n)}(t) = f(t, u, u', \dots, u^{(n-1)})$.

**Higher order → first-order system.** Any $n$-th order equation can be rewritten as a system of $n$ first-order equations:
$$u_1 = u,\quad u_1' = u_2,\quad u_2' = u_3,\quad \dots,\quad u_{n-1}' = u_n,\quad u_n' = f(t, u_1, u_2, \dots, u_n)$$
(This is exactly how $y'' = -y$ became the sin–cos system: $u_1 = y$, $u_2 = y'$.)

**DEF (Initial value problem, IVP).** Given a point $(t_0, u_0) \in \mathbb{R}\times\mathbb{R}^d$ and a function $f:\mathbb{R}\times\mathbb{R}^d \to \mathbb{R}^d$, the IVP is: find $u:\mathbb{R} \to \mathbb{R}^d$ such that
$$u'(t) = f(t, u(t)) \quad\text{and}\quad u(t_0) = u_0.$$
Sketch: the direction field with the one solution curve that passes through $(t_0, u_0)$.

### Hands-on — [`001-ode.ipynb`](001-ode.ipynb)

Forward Euler for the sin–cos system on $[0, 10]$ with $N = 500$ steps ($h = 0.02$), starting from $(y_1, y_2) = (0, 1)$.

- Loop: `y1 += h*y2; y2 += -h*y1` (Euler on the 2-D system), storing `y_values`, `t_values`.
- Plot of $y_1, y_2$ against $\sin t, \cos t$.
- Reading off $\sin(0.5)$: index $0.5/h = 25$ → $y_1 = 0.4818$ vs $\sin(0.5) = 0.4794$, error $2.3\times10^{-3}$.
- Observation: the Euler amplitude slowly **grows** (forward Euler adds energy to an oscillator each step); the error at $t = 10$ is ≈ 0.08 and shrinks linearly with $h$, matching the $O(h)$ result above.

---

## Day 2 — Tuesday, 22 September 2026

_to be added_

## Day 3 — Wednesday, 23 September 2026

_to be added_

## Day 4 — Thursday, 24 September 2026

_to be added_

## Day 5 — Friday, 25 September 2026

_to be added_
