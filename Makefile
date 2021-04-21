lint: typecheck format

typecheck:
	pdm run mypy --exclude __pypackages__ .

format:
	pdm run isort .
	pdm run black .

release: tag build publish

tag:
ifndef V
	false : Use V=1.2.3 to specify version
endif
	git tag v$(V) -m "Version $(V)"

build:
	pdm build

publish:
	pdm run twine upload dist/*

outdated:
	pdm update --dry-run --unconstrained

.PHONY: lint typecheck format release tag build publish outdated
