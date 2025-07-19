# Nighthawks Event Statistics Tool (NEST)
Python-powered statistics tool for viewing FIRST Tech Challenge team statistics.

View and compare teams' Offensive Power Rating (OPR) and Expected Points Added (EPA) from specified events.

`Powered by tkinter and Python 3.13`

## Usage

1) Create a `.env` file in the main directory of this project.
2) Inside your `.env` file add your FIRST API username and password in the following format:
```
API_USER=[username]
API_TOKEN=[password]
```
3) From a command line interface in the project directory run `pip install -r requirements.txt` to install
the required python dependencies.
4) Run `main.py` to start the app.

## Updating for Future Seasons
See [stats-calculator](https://github.com/team24124/stats-calculator/blob/main/README.md) for information on updating the stats calculator for new seasons.