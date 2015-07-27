#!/usr/bin/env make

all: photons.py Makefile
	./photons.py

.PHONY: clean
clean:
	rm -f `find . -name "*.pyc"` `find . -name "*.gif"` 

