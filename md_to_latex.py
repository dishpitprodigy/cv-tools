#!/usr/bin/env python3
"""Convert the local CV Markdown format into a styled LaTeX document."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SECTION_NAMES = {
    "Summary",
    "Skills",
    "Work Experience",
    "Education and Certifications",
}


PREAMBLE = r"""\documentclass[10pt,a4paper]{article}

\usepackage[margin=0.55in]{geometry}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{tabularx}
\usepackage{iftex}

\ifPDFTeX
  \usepackage[T1]{fontenc}
  \usepackage[utf8]{inputenc}
  \usepackage{lmodern}
\else
  \usepackage{fontspec}
  \setmainfont{Liberation Serif}
\fi

\definecolor{resumecrimson}{HTML}{983333}
\hypersetup{colorlinks=true,urlcolor=blue,linkcolor=black}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.18em}
\setlist[itemize]{leftmargin=1.1em,itemsep=0.10em,topsep=0.15em,parsep=0pt}

\newcommand{\resumesection}[1]{%
  \vspace{0.85em}%
  {\Large\bfseries #1}\par\vspace{-0.35em}%
  {\color{resumecrimson}\rule{\textwidth}{1.2pt}}\par\vspace{0.20em}%
}

\newcommand{\resumeheader}[4]{%
  {\LARGE #1}\par
  \begin{tabular*}{\textwidth}{@{}l@{\extracolsep{\fill}}c r@{}}
    #2 & #3 & #4 \\
  \end{tabular*}\par\vspace{-0.35em}
  {\color{resumecrimson}\rule{\textwidth}{1.2pt}}\par
}

\newcommand{\jobheader}[3]{%
  \vspace{0.45em}%
  \begin{tabular*}{\textwidth}{@{}l@{\extracolsep{\fill}}c r@{}}
    \textbf{#1} & \textbf{#2} & \textbf{#3} \\
  \end{tabular*}\vspace{-0.25em}
}

\newcommand{\role}[1]{\textit{#1}\par\vspace{-0.15em}}

\begin{document}
"""


POSTAMBLE = r"\end{document}" + "\n"


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def convert_inline(text: str) -> str:
    parts: list[str] = []
    pos = 0
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*")

    for match in pattern.finditer(text):
        parts.append(latex_escape(text[pos : match.start()]))
        label, url, bold, italic = match.groups()
        if label is not None and url is not None:
            parts.append(rf"\href{{{latex_escape(url)}}}{{{latex_escape(label)}}}")
        elif bold is not None:
            parts.append(rf"\textbf{{{latex_escape(bold)}}}")
        elif italic is not None:
            parts.append(rf"\textit{{{latex_escape(italic)}}}")
        pos = match.end()

    parts.append(latex_escape(text[pos:]))
    return "".join(parts)


def split_contact(line: str) -> tuple[str, str, str]:
    if "\t" in line:
        fields = [field.strip() for field in line.split("\t") if field.strip()]
    else:
        fields = [field.strip() for field in re.split(r"\s{2,}", line) if field.strip()]

    fields = fields[:3] + [""] * (3 - len(fields))
    return fields[0], fields[1], fields[2]


def close_itemize(output: list[str], in_itemize: bool) -> bool:
    if in_itemize:
        output.append(r"\end{itemize}")
    return False


def convert_cv(markdown: str) -> str:
    lines = markdown.splitlines()
    output = [PREAMBLE]
    in_itemize = False

    nonblank_index = next((idx for idx, line in enumerate(lines) if line.strip()), None)
    if nonblank_index is None:
        return PREAMBLE + POSTAMBLE

    name = convert_inline(lines[nonblank_index].strip())
    contact_idx = next(
        (idx for idx in range(nonblank_index + 1, len(lines)) if lines[idx].strip()),
        None,
    )
    phone, email, location = ("", "", "")
    body_start = nonblank_index + 1
    if contact_idx is not None:
        phone, email, location = split_contact(lines[contact_idx].strip())
        body_start = contact_idx + 1

    output.append(
        rf"\resumeheader{{{name}}}{{{convert_inline(phone)}}}{{{convert_inline(email)}}}{{{convert_inline(location)}}}"
    )

    for raw_line in lines[body_start:]:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        is_indented = bool(line[:1].isspace())

        if stripped in SECTION_NAMES:
            in_itemize = close_itemize(output, in_itemize)
            output.append(rf"\resumesection{{{latex_escape(stripped)}}}")
            continue

        company_match = re.match(r"^\*\*(.+?)\*\*\s+\|\s+(.+?)\s+\|\s+(.+?)$", stripped)
        if company_match:
            in_itemize = close_itemize(output, in_itemize)
            company, location, dates = company_match.groups()
            output.append(
                rf"\jobheader{{{latex_escape(company)}}}{{{latex_escape(location)}}}{{{latex_escape(dates)}}}"
            )
            continue

        cert_match = re.match(r"^\*\*(.+?)\*\*\s+\|\s+(.+?)$", stripped)
        if cert_match:
            in_itemize = close_itemize(output, in_itemize)
            cert, date = cert_match.groups()
            output.append(
                r"\begin{tabular*}{\textwidth}{@{}l@{\extracolsep{\fill}}r@{}}"
            )
            output.append(rf"\textbf{{{latex_escape(cert)}}} & {latex_escape(date)} \\")
            output.append(r"\end{tabular*}")
            continue

        bold_heading_match = re.match(r"^\*\*(.+?)\*\*$", stripped)
        if bold_heading_match:
            in_itemize = close_itemize(output, in_itemize)
            output.append(rf"\vspace{{0.35em}}\textbf{{{latex_escape(bold_heading_match.group(1))}}}\par")
            continue

        if stripped.startswith("* ") and not stripped.startswith("* **"):
            if not in_itemize:
                output.append(r"\begin{itemize}")
                in_itemize = True
            output.append(rf"\item {convert_inline(stripped[2:].strip())}")
            continue

        if stripped.startswith("*") and stripped.endswith("*") and stripped.count("*") == 2:
            in_itemize = close_itemize(output, in_itemize)
            output.append(rf"\role{{{convert_inline(stripped[1:-1])}}}")
            continue

        if stripped.startswith("* **"):
            if not in_itemize:
                output.append(r"\begin{itemize}")
                in_itemize = True
            output.append(rf"\item {convert_inline(stripped[2:].strip())}")
            continue

        if in_itemize and not is_indented:
            in_itemize = close_itemize(output, in_itemize)

        output.append(convert_inline(stripped) + r"\par")

    close_itemize(output, in_itemize)
    output.append(POSTAMBLE)
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="CV Markdown source")
    parser.add_argument("target", type=Path, help="Generated LaTeX output")
    args = parser.parse_args()

    args.target.write_text(convert_cv(args.source.read_text()), encoding="utf-8")


if __name__ == "__main__":
    main()
