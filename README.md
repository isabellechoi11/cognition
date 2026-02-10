# Trivial Compute PyQt5 App

## Overview

This is a simple Trivial Compute game application built with PyQt5.

## Features

- GUI built with PyQt5.
- Supports Python 3.11.0

## Prerequisites

- Python 3.11.0 (or a compatible version)
- `question_creator_gui.xlsx` must be present in the project root directory for the game to load questions

## How to Install

1. Clone the repository:
   ```bash
   git clone https://github.com/isabellechoi11/cognition.git
   cd cognition
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate           # Windows
   ```

3. Install the required dependencies (PyQt5, openpyxl, pandas):
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

From the project root directory, run:
```bash
python client.py
```

This will launch the game and open the main menu, where you can:

- **Play Game** – Click this button to begin setting up and playing a new game
- **How to Play** – Click this button to open a PDF with instructions on how to play the Trivial Compute game
- **Creator Mode** – This will open an Excel file where questions, answers, and categories can be added
    - Add new questions, answers, and categories in their respective columns on the Excel sheet
    - NOTE: The application must be restarted after modifying the questions, answers, and/or categories to see the updates when playing a game
- **Help** – Click this button to open the help PDF 