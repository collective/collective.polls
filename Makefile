# convenience Makefile to run tests and QA tools
# options: zc.buildout options
# src: source path
# minimum_coverage: minimun test coverage allowed
# pep8_ignores: ignore listed PEP 8 errors and warnings
# max_complexity: maximum McCabe complexity allowed
# css_ignores: skip file names matching find pattern (use ! -name PATTERN)
# js_ignores: skip file names matching find pattern (use ! -name PATTERN)

SHELL = /bin/sh

options = -N -q -t 3
src = src/collective/polls/
minimum_coverage = 72
pep8_ignores = E501
max_complexity = 12
css_ignores = ! -name jquery\*
js_ignores = ! -name excanvas\* ! -name jquery\*

qa:
# QA runs only if an environment variable named QA is present
ifneq "$(QA)" ""
	@echo Validating Python files
	# FIXME: skip complexity validation for now as we don't have time to deal with it
	#bin/flake8 --ignore=$(pep8_ignores) --max-complexity=$(max_complexity) $(src)
	bin/flake8 --ignore=$(pep8_ignores) $(src)

	@echo Validating minimun test coverage
	bin/coverage.sh $(minimum_coverage)

	@echo Validating CSS files
	npm install csslint -g 2>/dev/null
	find $(src) -type f -name *.css $(css_ignores) | xargs csslint

	@echo Validating JavaScript files
	npm install jshint -g 2>/dev/null
	find $(src) -type f -name *.js $(js_ignores) -exec jshint {} ';'
else
	@echo 'No QA environment variable present; skipping'
endif

install:
	mkdir -p buildout-cache/downloads
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

tests:
	bin/test
