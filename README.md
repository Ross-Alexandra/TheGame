[![Build Status](https://travis-ci.org/Ross-Alexandra/TheGame.svg?branch=master)](https://travis-ci.org/Ross-Alexandra/TheGame)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![codecov](https://codecov.io/gh/Ross-Alexandra/TheGame/branch/master/graph/badge.svg)](https://codecov.io/gh/Ross-Alexandra/TheGame)
[![Maintainability](https://api.codeclimate.com/v1/badges/9650ffb60ccea8bfb4bc/maintainability)](https://codeclimate.com/github/Ross-Alexandra/TheGame/maintainability)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
# TheGame
A basic 2D game with no current ideas for story, setting, etc.

# Installation
To install the requirements for this project, please run
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

This project also uses pre-commit, this means after installing, you should run:
```
pre-commit install
```
This should cause the pre-commit hooks to run.

# Testing the game
This project uses pytest as its unit test manager. In order to run the unit tests, please run
```
pytest
```

This should manage running all of the tests.

# Running the game
Because this project is designed with modules, it must be run as
```
python -m thegame
```

Running this from the root directory will cause it to run the game.
