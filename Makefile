#!/usr/bin/env make

all: photons.py Makefile
	mkdir -p gif
	./photons.py --tanh=2e-1 --wiki

.PHONY: clean
clean:
	rm -f `find . -name "*.pyc"` `find . -name "*.gif"` 

