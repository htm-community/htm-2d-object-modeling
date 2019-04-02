# Python

## Installation

Pipenv seems to be the best environment manager.  https://pipenv.readthedocs.io/en/latest/

Inside the `python` directory, run:

```bash
brew install pipenv
pipenv install
```

## Run the tests

```
pipenv run python -m unittest tests/*.py
```

## Add a package

```
pipenv install pyyaml
```

Or a dev package

```
pipenv install flake8 --dev
```

# Code style / formatting

Project uses flake8 and black.

Install them globally so your IDE can find them or point your IDE at your pipenv environment.

```
pip3 install flake8
pip3 install black
```