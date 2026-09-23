#!/usr/bin/env python3
"""
Build the static site for AMSC-2026.

Converts every notebook in the repository to HTML (and optionally PDF) and
generates an index page linking to all of them, plus the folder READMEs.

    python scripts/build_docs.py            # HTML only (fast, no extra deps)
    python scripts/build_docs.py --pdf      # also PDF (needs nbconvert[webpdf] + playwright)

Output goes to docs/ , which is what GitHub Pages serves.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SKIP_DIRS = {".git", ".venv", "docs", "node_modules", ".ipynb_checkpoints", "__pycache__"}

# Section titles and blurbs, keyed by top-level folder.
SECTIONS = {
    "ODEs": (
        "Lecture Series B — ODEs",
        "Modelling &amp; Parameter Estimation for ODEs · Dr. Michael Winckler, IWR Heidelberg",
    ),
    "PDEs": (
        "Lecture Series A — PDEs",
        "Numerical Solution of PDEs · Prof. Dr. Peter Bastian, IWR Heidelberg",
    ),
    "modeling": (
        "Modelling workbench",
        "Extra notebooks: population dynamics, parameter estimation, groundwater contamination",
    ),
}


# Curated titles/summaries. Anything not listed here falls back to reading the
# first markdown heading out of the notebook, so new files need no edit to appear.
TITLES = {
    "ODEs/001-ode.ipynb": (
        "Day 1 — Euler's method for a 2-D system",
        "Forward Euler for the harmonic oscillator y'' = -y written as a first-order system; "
        "comparison with sin/cos and the growth of the amplitude.",
    ),
    "ODEs/002-ode-day2.ipynb": (
        "Day 2 — Existence, uniqueness, error and order",
        "Blow-up in finite time, Lipschitz continuity and non-uniqueness, why Euler's amplitude grows, "
        "local vs global error, Richardson extrapolation, and the SIR model.",
    ),
    "ODEs/003-ode-day3.ipynb": (
        "Day 3 — Stability and Runge–Kutta methods",
        "Consistency and stability, the decay equation and the condition |1 + h*lambda| <= 1, "
        "stability regions, and the Runge–Kutta family from Euler to RK4.",
    ),
    "PDEs/03-day3-pde.ipynb": (
        "Day 3 — The Finite Element Method",
        "Follows the lecture slide by slide: weak form to linear system, mesh generation, the reference "
        "element and the affine map, assembly, Cea's lemma, and the L-shape convergence study.",
    ),
    "modeling/00-extra.ipynb": (
        "Logistic growth and parameter estimation",
        "The logistic ODE, a fit of 100 years of world-population data with Euler inside least squares, "
        "sensitivity analysis, identifiability, and Levenberg–Marquardt from scratch.",
    ),
    "modeling/01-extra.ipynb": (
        "Groundwater contamination",
        "Darcy flow and the advection–dispersion equation: a 1-D column verified against the exact "
        "Ogata–Banks solution, then a 2-D aquifer with a clay lens, a leaking tank and a pumping well.",
    ),
}


def find_notebooks() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*.ipynb")):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        out.append(p)
    return out


def notebook_meta(nb_path: Path) -> dict:
    """Pull a title, a one-line summary and some counts out of a notebook."""
    try:
        nb = json.loads(nb_path.read_text())
    except Exception:
        return {"title": nb_path.stem, "summary": "", "cells": 0, "figures": 0}

    title, summary = None, None
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = "".join(cell.get("source", "")).strip()
        for line in text.splitlines():
            line = line.strip()
            if title is None and line.startswith("#"):
                title = re.sub(r"^#+\s*", "", line).strip()
            elif title is not None and line and not line.startswith(("#", "*", "!", "|", ">")):
                summary = re.sub(r"[*_`$\\]", "", line)[:180]
                break
        if title and summary:
            break

    figures = sum(
        1
        for c in nb.get("cells", [])
        for o in c.get("outputs", [])
        if "image/png" in o.get("data", {})
    )
    return {
        "title": title or nb_path.stem,
        "summary": summary or "",
        "cells": len(nb.get("cells", [])),
        "figures": figures,
    }


def convert(nb_path: Path, fmt: str, outdir: Path) -> bool:
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "jupyter", "nbconvert",
        "--to", fmt,
        "--output-dir", str(outdir),
        "--output", nb_path.stem,
        str(nb_path),
    ]
    if fmt == "html":
        cmd[6:6] = ["--template", "lab", "--embed-images"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  ! {fmt} failed for {nb_path.name}: {res.stderr.strip().splitlines()[-1:]}")
        return False
    return True


INDEX_CSS = """
:root {
  color-scheme: light;
  --bg: #fcfcfb; --surface: #ffffff; --border: #e5e4df;
  --ink: #0b0b0b; --ink-2: #52514e; --ink-3: #8a8984;
  --accent: #2a78d6; --accent-soft: #eef4fd;
  --radius: 12px;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #17171a; --surface: #1f1f23; --border: #303036;
    --ink: #f5f5f3; --ink-2: #b8b7b1; --ink-3: #85847f;
    --accent: #6da7ec; --accent-soft: #1c2938;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #17171a; --surface: #1f1f23; --border: #303036;
  --ink: #f5f5f3; --ink-2: #b8b7b1; --ink-3: #85847f;
  --accent: #6da7ec; --accent-soft: #1c2938;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 900px; margin: 0 auto; padding: 56px 16px 80px; }
header { margin-bottom: 40px; }
h1 { font-size: clamp(1.7rem, 4.5vw, 2.4rem); line-height: 1.2; margin: 0 0 10px; letter-spacing: -0.02em; }
.lede { color: var(--ink-2); margin: 0 0 18px; max-width: 62ch; }
.meta { color: var(--ink-3); font-size: 0.86rem; display: flex; flex-wrap: wrap; gap: 6px 16px; }
.meta a { color: var(--ink-3); }
h2 {
  font-size: 1.12rem; margin: 40px 0 4px; letter-spacing: -0.01em;
  padding-bottom: 8px; border-bottom: 1px solid var(--border);
}
h2 .sub { display: block; font-size: 0.82rem; font-weight: 400; color: var(--ink-3); margin-top: 4px; letter-spacing: 0; }
.cards { display: grid; gap: 12px; margin-top: 18px; }
.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 16px 18px; transition: border-color .15s ease, transform .15s ease;
}
.card:hover { border-color: var(--accent); transform: translateY(-1px); }
.card h3 { margin: 0 0 4px; font-size: 1rem; }
.card h3 a { color: var(--ink); text-decoration: none; }
.card h3 a:hover { color: var(--accent); }
.card p { margin: 0 0 12px; color: var(--ink-2); font-size: 0.9rem; }
.row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.pill {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.78rem; padding: 4px 10px; border-radius: 999px;
  background: var(--accent-soft); color: var(--accent); text-decoration: none;
  border: 1px solid transparent;
}
.pill:hover { border-color: var(--accent); }
.pill.ghost { background: transparent; color: var(--ink-3); border-color: var(--border); }
.path { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.78rem; color: var(--ink-3); }
footer { margin-top: 56px; padding-top: 20px; border-top: 1px solid var(--border); color: var(--ink-3); font-size: 0.84rem; }
footer a { color: var(--accent); }
@media (max-width: 480px) { .wrap { padding-top: 36px; } }
"""


def build_index(entries: dict[str, list[dict]], repo: str, with_pdf: bool) -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>AMSC 2026</title>",
        '<meta name="description" content="Notes and code from the AMSC 2026 Summer School on Applied '
        'Mathematics and Scientific Computing, Kathmandu University &amp; IWR Heidelberg.">',
        f"<style>{INDEX_CSS}</style></head><body><div class='wrap'>",
        "<header>",
        "<h1>AMSC 2026 — Applied Mathematics &amp; Scientific Computing</h1>",
        "<p class='lede'>Notes, derivations and runnable code from the summer school jointly organised by "
        "<strong>Kathmandu University</strong>, Nepal and the <strong>Interdisciplinary Center for Scientific "
        "Computing (IWR), Heidelberg University</strong>, Germany — 21–25 September 2026, Dhulikhel.</p>",
        "<div class='meta'>",
        f"<span>Updated {date.today().isoformat()}</span>",
        f"<a href='https://github.com/{repo}'>Source on GitHub</a>",
        "<span>Every notebook below runs top to bottom</span>",
        "</div></header>",
    ]

    for folder in list(SECTIONS) + sorted(set(entries) - set(SECTIONS)):
        items = entries.get(folder)
        if not items:
            continue
        title, blurb = SECTIONS.get(folder, (folder, ""))
        parts.append(f"<h2>{html.escape(title)}<span class='sub'>{blurb}</span></h2>")
        parts.append("<div class='cards'>")
        for it in items:
            parts.append("<div class='card'>")
            parts.append(f"<h3><a href='{it['html']}'>{html.escape(it['title'])}</a></h3>")
            if it["summary"]:
                parts.append(f"<p>{html.escape(it['summary'])}</p>")
            parts.append("<div class='row'>")
            parts.append(f"<a class='pill' href='{it['html']}'>Read</a>")
            if with_pdf and it.get("pdf"):
                parts.append(f"<a class='pill' href='{it['pdf']}'>PDF</a>")
            parts.append(
                f"<a class='pill ghost' href='https://github.com/{repo}/blob/main/{it['src']}'>Notebook</a>"
            )
            parts.append(
                f"<span class='pill ghost'>{it['cells']} cells · {it['figures']} figures</span>"
            )
            parts.append("</div>")
            parts.append(f"<div class='path' style='margin-top:10px'>{html.escape(it['src'])}</div>")
            parts.append("</div>")
        parts.append("</div>")

    parts.append(
        "<footer>Built automatically from the notebooks by "
        f"<a href='https://github.com/{repo}/blob/main/.github/workflows/pages.yml'>GitHub Actions</a>. "
        "Lecture slides are not redistributed here.</footer>"
    )
    parts.append("</div></body></html>")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="store_true", help="also build PDFs (needs nbconvert[webpdf])")
    ap.add_argument("--repo", default="rockerritesh/AMSC-2026")
    args = ap.parse_args()

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    notebooks = find_notebooks()
    print(f"found {len(notebooks)} notebooks")

    entries: dict[str, list[dict]] = {}
    for nb in notebooks:
        rel = nb.relative_to(ROOT)
        folder = rel.parts[0] if len(rel.parts) > 1 else "."
        outdir = DOCS / folder if folder != "." else DOCS
        print(f"  {rel}")
        if not convert(nb, "html", outdir):
            continue
        meta = notebook_meta(nb)
        if str(rel) in TITLES:                       # curated title wins over the auto-extracted one
            meta["title"], meta["summary"] = TITLES[str(rel)]
        item = {
            **meta,
            "src": str(rel),
            "html": f"{folder}/{nb.stem}.html" if folder != "." else f"{nb.stem}.html",
        }
        if args.pdf and convert(nb, "webpdf", outdir):
            item["pdf"] = item["html"].replace(".html", ".pdf")
        entries.setdefault(folder, []).append(item)

    for folder in entries:
        entries[folder].sort(key=lambda d: d["src"])

    (DOCS / "index.html").write_text(build_index(entries, args.repo, args.pdf))
    (DOCS / ".nojekyll").write_text("")          # serve files starting with _ too

    # copy the READMEs and the timetable so the site is self-contained
    for extra in ["README.md", "ODEs/README.md", "PDEs/README.md", "timeline.png"]:
        src = ROOT / extra
        if src.exists():
            dst = DOCS / extra
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    n_pdf = sum(1 for v in entries.values() for i in v if i.get("pdf"))
    print(f"\ndocs/ built: {sum(len(v) for v in entries.values())} HTML, {n_pdf} PDF, 1 index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
