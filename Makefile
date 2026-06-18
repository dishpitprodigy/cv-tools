SRC ?= ../cv.md
OUT ?= ../cv
ENGINE ?= xelatex

.PHONY: tex pdf clean

tex:
	./md_to_latex.py "$(SRC)" "$(OUT).tex"

pdf: tex
	$(ENGINE) -interaction=nonstopmode -halt-on-error -output-directory "$$(dirname "$(OUT)")" "$(OUT).tex"

clean:
	rm -f "$(OUT).aux" "$(OUT).log" "$(OUT).out"
