# Python

## Installation

You can use variety of python environment managers, but we recommend Anaconda with Python 3.6+
or using pure system python.

**Use Python3.6+ and be careful, that you are actually using it**

Inside the `python` directory, run:

```bash
python -m pip install -r requirements.txt
```

## Run the tests

```
python -m unittest tests/*.py
```
# Run

Just run in the python folder
```
python main.py
```

# Using visualization tool

You can use [visualisation tool for HTM systems](https://github.com/htm-community/HTMpandaVis).
Install what is neccessary according to project readme & enable using pandaVis in the main.py by setting appropriate flag at the beginning of the script.
Firstly run the vis tool in terminal, then run this script in terminal. It will get connected through TCP and show state of HTM system.

# Code style / formatting

Project uses flake8(quality code check) and black(code formatter).
Install them globally so your IDE can find them or point your IDE at your py environment.

```
python -m pip install flake8
python -m pip install black
```

Setup your IDE to 4 spaces indentation.

## Manually apply formatting
Other option is just to apply formatting to file manually.
```
black path/to/file.py
```

