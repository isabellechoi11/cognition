# Trivial Compute PyQt5 App

## Overview

This is a simple Trivial Compute game application built with PyQt5.

## Features

- GUI built with PyQt5.
- Supports Python 3.11.0 

## Prerequisites

- [Python 3.11.0](https://www.python.org/downloads/release/python-3110/) must be installed on your system.

## How to Install

1. Clone or download this repository.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   This will install PyQt5, openpyxl, and pandas.

## How to Run

Launch the game by running the following command from the project directory:
```
python client.py
```

This will open the game to the main menu.

> **Note:** The `question_creator_gui.xlsx` file must be present in the project directory for the game to function properly.

- Play Game – Click this button to begin setting up and playing a new game 
- How to Play – Click this button to open a pdf with instructions on how to play the Trivial Compute game 
- Creator Mode – This will open an excel file where questions, answers, and categories can be added 
    - Add new questions, answers, and categories in their respective categories on the excel sheet 
    - NOTE: The application must be restarted after modifying the questions, answers, and/or categories to see the updates when playing a game 
- Help – Click this button to open this pdf  