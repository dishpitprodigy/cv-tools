# CV PDF Build

This keeps CV or resume content in Markdown and generates LaTeX for the visual layer.
The generated PDF is intended to mimic the existing Google Docs style: A4 page,
compact typography, aligned employer/location/date rows, and crimson section rules.

## Files

* `md_to_latex.py` converts the local CV Markdown format into `.tex`.
* `Makefile` provides repeatable `tex` and `pdf` targets.
* The default source is `../cv.md`.
* The default generated LaTeX file is `../cv.tex`.

## Usage

Generate LaTeX only:

```bash
make tex
```

Generate a PDF:

```bash
make pdf
```

Override source or output:

```bash
make tex SRC=../targeted-cv.md OUT=../targeted-cv
```

## Dependencies

PDF generation expects a TeX engine, preferably `xelatex`.

On Fedora/RHEL-like systems, install a XeLaTeX-capable TeX Live set:

```bash
sudo dnf install texlive-xetex texlive-iftex texlive-fontspec texlive-geometry texlive-enumitem texlive-hyperref texlive-tools texlive-xcolor
```

On Debian/Ubuntu-like systems:

```bash
sudo apt install texlive-xetex texlive-latex-recommended texlive-latex-extra
```
