test:
	python -m unittest discover tests ${ARGS}

coverage:
	coverage run --source=goldencheetahlib -m unittest discover tests
	coverage report
	coverage html

isort:
	isort --skip=venv
