lint:
	black --check .
	flake8 .

test: 
	pytest