# Trivial Compute PyQt5 App

## Overview

This is a simple Trivial Compute game application built with PyQt5.

## Features

- GUI built with PyQt5.
- Supports Python 3.11.0 

## How to Install

1. Clone the repository:
   ```bash
   git clone https://github.com/isabellechoi11/cognition.git
   cd cognition
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   ```
   - **macOS / Linux:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

> **Note:** This project requires **Python 3.11.0**. On Linux you may also need to install PyQt5 system dependencies (e.g., `sudo apt-get install python3-pyqt5`).

## How to Run

From the repository root, start the game with:
```bash
python client.py
```

This will open the game to the main menu where you can:

- Play Game – Click this button to begin setting up and playing a new game 
- How to Play – Click this button to open a pdf with instructions on how to play the Trivial Compute game 
- Creator Mode – This will open an excel file where questions, answers, and categories can be added 
    - Add new questions, answers, and categories in their respective categories on the excel sheet 
    - NOTE: The application must be restarted after modifying the questions, answers, and/or categories to see the updates when playing a game 
- Help – Click this button to open this pdf  