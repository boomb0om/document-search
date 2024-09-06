codestyle:
	mypy document_search/
	ruff check document_search/ --config pyproject.toml
	isort --check document_search/

autofix:
	ruff check document_search/ --config pyproject.toml --fix
	isort document_search/