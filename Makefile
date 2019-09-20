upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -U -q pip-tools
	pip-compile --upgrade -o requirements/dev.txt requirements/base.in requirements/dev.in requirements/quality.in
	pip-compile --upgrade -o requirements.txt requirements/base.in requirements/prod.in
	# Remove Django from requirements.txt
	sed '/django==/d' requirements.txt > requirements.tmp; mv requirements.tmp requirements.txt
	sed '/# via django$$/d' requirements.txt > requirements.tmp; mv requirements.tmp requirements.txt
	# Make everything =>, not ==
	sed 's/==/>=/g' requirements.txt > requirements.tmp; mv requirements.tmp requirements.txt
	pip-compile --upgrade -o requirements/doc.txt requirements/base.in requirements/doc.in
	pip-compile --upgrade -o requirements/quality.txt requirements/quality.in
	pip-compile --upgrade -o requirements/test.txt requirements/base.in requirements/test.in
	pip-compile --upgrade -o requirements/travis.txt requirements/travis.in
	# Let tox control the Django version for tests
	sed '/django==/d' requirements/test.txt > requirements/test.tmp; mv requirements/test.tmp requirements/test.txt
	sed '/# via django$$/d' requirements/test.txt > requirements/test.tmp; mv requirements/test.tmp requirements/test.txt

install_requirements: ## install development environment requirements
	pip install -qr requirements/dev.txt -qr requirements/test.txt -qr requirements/quality.txt --exists-action w
	pip-sync requirements/dev.txt requirements/doc.txt requirements/quality.txt requirements/test.txt

selfcheck: ## check that the Makefile is well-formed
	@echo "The Makefile is well-formed."