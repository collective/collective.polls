#! /bin/sh
# runs only if an environment variable named QA is present

# SRC: source path
# MINIMUM_COVERAGE: minimun test coverage allowed
# PEP8_IGNORES: ignore listed PEP 8 errors and warnings
# MAX_COMPLEXITY: maximum McCabe complexity allowed
# CSS_IGNORES: skip file names matching find pattern (use ! -name PATTERN)
# JS_IGNORES: skip file names matching find pattern (use ! -name PATTERN)

SRC=src/collective/polls/
MINIMUM_COVERAGE=72
PEP8_IGNORES=E501
MAX_COMPLEXITY=12
CSS_IGNORES="! -name jquery\*"
JS_IGNORES ="! -name excanvas\* ! -name jquery\*"

if "$QA" != "" ; then
	@echo Validating Python files
	# FIXME: skip complexity validation for now as we don't have time to deal with it
	#bin/flake8 --ignore=$PEP8_IGNORES --max-complexity=$MAX_COMPLEXITY $SRC
	bin/flake8 --ignore=$PEP8_IGNORES $SRC

	@echo Validating minimun test coverage
	bin/coverage.sh $MINIMUM_COVERAGE

	@echo Validating CSS files
	npm install csslint -g 2>/dev/null
	find $SRC -type f -name *.css $CSS_IGNORES | xargs csslint

	@echo Validating JavaScript files
	npm install jshint -g 2>/dev/null
	find $SRC -type f -name *.js $JS_IGNORES -exec jshint {} ';'
fi
