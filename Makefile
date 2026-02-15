.PHONY: install test clean build

install:
	pip install -e .

test:
	python3 -m unittest discover tests

clean:
	rm -rf dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python3 -m build
