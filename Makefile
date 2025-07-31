all: test

uninstall:
	pip freeze | grep -v "^-e" | sed "s/@.*//" | xargs pip uninstall -y

clean:
	rm -rf build dist
	find . -name '*.pyc' -exec rm \{\} \;
	find . -type d -name '__pycache__' -exec rm -r {} +

deps:
	pip install --upgrade pip build twine

install: deps
	@# Install OpenFisca-Nouvelle-Caledonie for development.
	@# `make install` installs the editable version of openfisca-nouvelle-caledonie.
	@# This allows contributors to test as they code.
	pip install --editable .[dev] --upgrade

build: clean deps
	@# Install OpenFisca-Nouvelle-Caledonie for deployment and publishing.
	@# `make build` allows us to be be sure tests are run against the packaged version
	@# of OpenFisca-Extension-Template, the same we put in the hands of users and reusers.
	python -m build
	pip uninstall --yes openfisca-nouvelle-caledonie
	find dist -name "*.whl" -exec pip install --force-reinstall {}[dev] \;

format:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	ruff format `git ls-files | grep "\.py$$"`
	isort `git ls-files | grep "\.py$$"`

lint:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	isort --check `git ls-files | grep "\.py$$"`
	ruff check `git ls-files | grep "\.py$$"`
	yamllint `git ls-files | grep "\.yaml$$"`

test: clean
	openfisca test --country-package openfisca_nouvelle_caledonie openfisca_nouvelle_caledonie/tests

serve-local: build
	openfisca serve --country-package openfisca_nouvelle_caledonie
