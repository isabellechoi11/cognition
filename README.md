# Trivial Compute PyQt5 App

## Overview

This is a simple Trivial Compute game application built with PyQt5.

## Features

- GUI built with PyQt5.
- Supports Python 3.11.0 

## Prerequisites

- Python 3.11.0
- pip (Python package manager)
- The following Python packages (listed in `requirements.txt`):
  - PyQt5
  - openpyxl
  - pandas

## How to Install

1. Clone the repository:
   ```bash
   git clone https://github.com/isabellechoi11/cognition.git
   cd cognition
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

1. Make sure `question_creator_gui.xlsx` is present in the working directory — this file contains the trivia questions loaded by the game at startup.

2. Launch the game:
   ```bash
   python client.py
   ```

3. The game will open to the main menu with the following options:

- **Play Game** – Click this button to begin setting up and playing a new game
- **How to Play** – Click this button to open a PDF with instructions on how to play the Trivial Compute game
- **Creator Mode** – This will open an Excel file where questions, answers, and categories can be added
    - Add new questions, answers, and categories in their respective columns on the Excel sheet
    - NOTE: The application must be restarted after modifying the questions, answers, and/or categories to see the updates when playing a game
- **Help** – Click this button to open the help PDF 