# AMSC 2026 — Summer School on Applied Mathematics and Scientific Computing

Jointly organised by **Kathmandu University**, Nepal and the **Interdisciplinary Center for Scientific
Computing (IWR), Heidelberg University**, Germany.

📍 Kathmandu University, Dhulikhel · 📅 Monday 21 – Friday 25 September 2026

**📖 Browsable notebooks: [rockerritesh.github.io/AMSC-2026](https://rockerritesh.github.io/AMSC-2026/)**

This repository holds my notes, transcribed lecture content and runnable code from the school. Every
notebook executes top to bottom; every numerical claim in the text is produced by the code next to it.

---

## Lecture series

| Series | Title | Lecturer | Folder |
|---|---|---|---|
| **A** | Numerical Solution of PDEs | Prof. Dr. Peter Bastian, IWR Heidelberg · [Scholar](https://scholar.google.com/citations?hl=en&user=pVZJ_NcAAAAJ&view_op=list_works&sortby=pubdate) | [`PDEs/`](PDEs/) |
| **B** | Modelling & Parameter Estimation for ODEs | Dr. Michael Winckler, IWR Heidelberg · [Scholar](https://scholar.google.com/citations?hl=en&user=0pg-x-EAAAAJ&view_op=list_works&sortby=pubdate) | [`ODEs/`](ODEs/) |

**Guest lectures**
- Tue 22 Sep — *An Introductory Guide to Mathematical Modeling: Five-Step Modeling Approach* — Prof. Gurung
- Tue 22 Sep — *From Physical Laws to Computation: A Computational Journey Through PDE Models* — Mr. Narayan Sapkota
- Thu 24 Sep — *From ODEs to Epidemics: Modeling Infectious Disease Dynamics with Compartmental Models* — Dr. Phaijoo

## Contents

### ODEs — [`ODEs/`](ODEs/README.md)

| Notebook | Topics |
|---|---|
| [`001-ode.ipynb`](ODEs/001-ode.ipynb) | Forward Euler for $y''=-y$ as a first-order system; comparison with $\sin$/$\cos$ |
| [`002-ode-day2.ipynb`](ODEs/002-ode-day2.ipynb) | Blow-up in finite time · Lipschitz continuity and non-uniqueness · why Euler's amplitude grows · local vs global error and order · Richardson extrapolation · SIR model |
| [`003-ode-day3.ipynb`](ODEs/003-ode-day3.ipynb) | Consistency and stability · the decay equation and $\lvert 1+h\lambda\rvert \le 1$ · stability regions · Runge–Kutta methods from Euler to RK4 |

### PDEs — [`PDEs/`](PDEs/README.md)

| Notebook / script | Topics |
|---|---|
| [`03-day3-pde.ipynb`](PDEs/03-day3-pde.ipynb) | The Finite Element Method, following the lecture slide by slide: weak form → linear system, mesh generation, reference element and the affine map, assembly, Céa's lemma and a priori estimates, matrix properties, the L-shape convergence study |
| [`steel_in_rubber.py`](PDEs/steel_in_rubber.py) | Plane-stress FEM: a steel square embedded in a rubber sheet under tension — discontinuous coefficients and interface-corner stress concentration |

### Modelling workbench — [`modeling/`](modeling/)

| Notebook | Topics |
|---|---|
| [`00-extra.ipynb`](modeling/00-extra.ipynb) | Logistic growth · fitting 100 years of world-population data with Euler inside least squares · sensitivity analysis and identifiability · Levenberg–Marquardt from scratch |
| [`01-extra.ipynb`](modeling/01-extra.ipynb) | Groundwater contamination: Darcy flow + advection–dispersion, verified against the exact Ogata–Banks solution, then a 2-D aquifer with a clay lens and a pumping well |

## Schedule

Full timetable: [`timeline.png`](timeline.png).

| Day | Morning | Late morning | Afternoon |
|---|---|---|---|
| **Mon 21 Sep** | 09:30 Opening ceremony & MoU | 10:45–12:15 **A: PDEs** | 14:00–15:30 **B: ODEs** |
| **Tue 22 Sep** | 09:30–11:00 **A: PDEs** | 11:15–12:45 **B: ODEs** | Guest lectures |
| **Wed 23 Sep** | 09:30–11:00 **A: PDEs** | 11:15–12:45 **B: ODEs** | Social event: hiking around Dhulikhel |
| **Thu 24 Sep** | 09:30–11:00 **A: PDEs** | 11:15–12:45 **B: ODEs** | Guest lecture |
| **Fri 25 Sep** | 09:30–11:00 **A: PDEs** | 11:15–12:45 **B: ODEs** | Closing lunch & feedback |

## Running the code

Managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync                 # create .venv and install jupyter, numpy, scipy, matplotlib
uv run jupyter lab      # or open the .ipynb files in VS Code with the .venv kernel
```

## Building the site locally

```bash
python scripts/build_docs.py          # HTML only — fast, no extra dependencies
python scripts/build_docs.py --pdf    # also PDF (needs `pip install "nbconvert[webpdf]"`)
```

Output lands in [`docs/`](docs/), which is what GitHub Pages serves.

## Adding new content

1. Drop a new `.ipynb` anywhere in the repository (or add to an existing one).
2. Commit and push to `main`.
3. [`.github/workflows/pages.yml`](.github/workflows/pages.yml) rebuilds every notebook to HTML + PDF,
   regenerates the index, and redeploys the site. No workflow edits needed.

To give a notebook a nicer title and summary on the index page, add an entry to `TITLES` in
[`scripts/build_docs.py`](scripts/build_docs.py). Anything not listed falls back to the first markdown
heading in the notebook.

## A note on the lecture slides

The lecturers' own slide decks are **not** included in this repository — they are the lecturers'
material to distribute. `.gitignore` excludes them. Everything here is my own notes, transcription and code.
