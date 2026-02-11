# Trivial Compute PyQt5 App

## Overview

This is a simple Trivial Compute game application built with PyQt5.

## Features

- GUI built with PyQt5.
- Supports Python 3.11.0 

## How to Install:

### Prerequisites
- Python 3.11.0

### Steps
1. Clone or download this repository.
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run:
Launch the game by running the following command from the project directory:
```bash
python client.py
```

Once the application has started, the game will open to the main menu.

- Play Game – Click this button to begin setting up and playing a new game 
- How to Play – Click this button to open a pdf with instructions on how to play the Trivial Compute game 
- Creator Mode – This will open an excel file where questions, answers, and categories can be added 
    - Add new questions, answers, and categories in their respective categories on the excel sheet 
    - NOTE: The application must be restarted after modifying the questions, answers, and/or categories to see the updates when playing a game 
- Help – Click this button to open this pdf  