import random
import subprocess
import sys
import platform
import os
import time
import pandas as pd
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QStackedWidget, 
    QSizePolicy, QScrollArea, QDialog
)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPixmap, QIcon, QFont

from server import Direction, Game, Question, State, TrivialComputeServer, Kind

class DiceRollDialog(QDialog):
    def __init__(self, names):
        super().__init__()

        self.setWindowTitle("Player Dice Rolls")
        self.setFixedSize(400, 300)  # Set the window size

        self.layout = QVBoxLayout()
        self.rolls = self.roll_dice(names)
        self.shift_first_player()
        self.display_rolls()

        first_player = self.rolls[0][0]
        explanation_label = QLabel(f"{first_player} goes first!")
        explanation_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(explanation_label)

        self.ok_button = QPushButton("OK")
        self.ok_button.setFont(QFont(None, 12))
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

    def roll_dice(self, names):
        """Roll a dice for each player, ensure no ties, and return a sorted list of tuples (name, roll)."""
        rolls = {}
        while len(rolls) < len(names):
            roll = random.randint(1, 6)
            if roll not in rolls.values():
                rolls[names[len(rolls)]] = roll
        return sorted(rolls.items(), key=lambda x: 0, reverse=False)

    def display_rolls(self):
        """Display the player rolls in the dialog."""
        grid_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        num_players = len(self.rolls)

        for i in range(4):
            if i < num_players:
                # Create and display player widget for each existing player
                name, roll = self.rolls[i]
                player_widget = self.create_player_widget(name, roll)
            else:
                # Create and display an empty placeholder for missing players
                player_widget = QWidget()
                player_layout = QVBoxLayout()
                name_label = QLabel("Empty")
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setFont(QFont(None, 14, QFont.Bold))
                player_layout.addWidget(name_label)
                player_widget.setLayout(player_layout)

            if i % 2 == 0:
                left_layout.addWidget(player_widget)
            else:
                right_layout.addWidget(player_widget)

        grid_layout.addLayout(left_layout)
        grid_layout.addLayout(right_layout)

        self.layout.addLayout(grid_layout)

    def create_player_widget(self, name, roll):
        """Create a widget to display a player's name and roll in a quadrant."""
        player_widget = QWidget()
        player_layout = QVBoxLayout()

        name_label = QLabel(name)
        name_label.setFont(QFont(None, 14, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("text-decoration: underline;")
        
        roll_label = QLabel(str(roll))
        roll_label.setFont(QFont(None, 20))
        roll_label.setAlignment(Qt.AlignCenter)

        player_layout.addWidget(name_label)
        player_layout.addWidget(roll_label)

        player_widget.setLayout(player_layout)

        return player_widget

    def shift_first_player(self):
        """Shift self.rolls so that the player with the highest roll goes first."""
        max_roll_index = 0
        
        # Find the index of the player with the highest roll
        for i in range(1, len(self.rolls)):
            if self.rolls[i][1] > self.rolls[max_roll_index][1]:
                max_roll_index = i
        
        # Shift the list so that the highest roll is first
        self.rolls = self.rolls[max_roll_index:] + self.rolls[:max_roll_index]
    
    def get_player_order(self):
        """Return the player order based on their dice rolls."""
        return [name for name, roll in self.rolls]


class DirectionDialog(QDialog):
    def __init__(self, directions, name, roll, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Direction")
        self.layout = QVBoxLayout()
        self.setFixedWidth(300)
        
        self.placeholder_label = QLabel(f"{name} has {roll} moves left!", self)
        self.layout.addWidget(self.placeholder_label)
        
        # Create buttons for each enum value
        for direction in directions :
            button = QPushButton(direction.name, self)
            button.clicked.connect(lambda _, d=direction: self.select_direction(d))
            self.layout.addWidget(button)
        
        
        self.setLayout(self.layout)
        self.selected_direction = None
    
    def select_direction(self, direction):
        self.selected_direction = direction
        self.accept()
class BoardWidget(QWidget):
    def __init__(self, server: TrivialComputeServer, game: Game, player_names, selected_categories):
        super().__init__()
        self.server = server
        self.game = game
        self.player_names = player_names
        self.selected_categories = selected_categories
        self.squares = {}
        self.grid_square_size = 73
        self.outer_margin = 75
        self.initUI()
        self.update_player_positions()

        self.timer = QTimer()
        self.time_elapsed = QTime(0,0)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.bg_label = QLabel(self)
        bg_pixmap = QPixmap('images/gameplay_blank.png')
        self.bg_label.setPixmap(bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(self.rect())
        self.layout.addWidget(self.bg_label)

        self.draw_board()
        self.setup_buttons()
        self.category_legend()
        
        dialog = DiceRollDialog(self.player_names)

        if dialog.exec_() == QDialog.Accepted:
            player_order = dialog.get_player_order()
            self.player_names = [x for x in player_order]
            self.game = self.server.set_order(player_order)
            
            
            print([x.name for x in self.game.players])
            
            self.display_timer()
            self.display_current_player()
            self.display_roll_outcome()
            self.draw_players()
            self.draw_player_icons()



            self.question_overlay = None

    def draw_board(self):
        for k, square in self.game.board.index_map.items():
            if k == -1:
                continue
            x, y = self.calculate_position_on_background(square.y_x)
            label = QLabel(self.bg_label)
            label.setAlignment(Qt.AlignCenter)
            label.setGeometry(int(x), int(y), int(self.grid_square_size), int(self.grid_square_size))
            label.setStyleSheet(f"background: transparent; color: pink; font-weight: bold;")
            self.squares[k] = label

    def draw_players(self):
        self.player_widgets = []
        player_icons = ['elephant.png', 'chicken.png', 'octopus.png', 'snail.png']
        self.player_info_labels = []
        
        player_positions = [
            (150, 210),  # Position for Player 1
            (450, 210),  # Position for Player 2
            (150, 510),  # Position for Player 3
            (450, 510)   # Position for Player 4
        ]

        for i, player in enumerate(self.game.players):
            # Player Name and Categories (existing code)
            info_label = QLabel(self.bg_label)
            info_label.setText(f"{self.player_names[i]}\nCategories Acquired:\n")
            info_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
            info_label.setAlignment(Qt.AlignCenter)
            
            # Set a fixed size to prevent it from moving upwards
            info_label.setGeometry(player_positions[i][0], player_positions[i][1], 200, 80)
            
            info_label.show()
            self.player_info_labels.append(info_label)

            # Player Icon - Set the icon size to be smaller to fit the board tiles
            icon_label = QLabel(self.bg_label)
            icon_path = f'player_icons/{player_icons[i]}'
            player_pixmap = QPixmap(icon_path).scaled(30, 30, Qt.KeepAspectRatio)  # Icon Size
            icon_label.setPixmap(player_pixmap)
            icon_label.setScaledContents(True)
            
            # Adjust icon position relative to the text
            icon_label.setGeometry(player_positions[i][0] + 85, player_positions[i][1] + 85, 30, 30)
            
            icon_label.show()
            
            # Store the icon label
            self.player_widgets.append(icon_label)

    def draw_player_icons(self):
        # Legend for identifying player's pre-selected game icons
        player_icons = ['elephant.png', 'chicken.png', 'octopus.png', 'snail.png']
        player_icon_positions = [
            (230, 160),  # Player 1
            (535, 160),  # Player 2
            (230, 460),  # Player 3
            (535, 460)   # Player 4
        ]
        
        # Draw icons only for the selected players
        for i, player in enumerate(self.game.players):
            icon_label = QLabel(self.bg_label)
            icon_path = f'player_icons/{player_icons[i]}'
            player_pixmap = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio)
            icon_label.setPixmap(player_pixmap)
            icon_label.setScaledContents(True)
            
            # Set the estimated position for each icon
            icon_label.setGeometry(player_icon_positions[i][0], player_icon_positions[i][1], 40, 40)
            icon_label.show()
            
            # Store the icon label in case we need to reference it later
            self.player_widgets.append(icon_label)

    def setup_buttons(self):
        button_layout = QVBoxLayout()
        self.layout.addLayout(button_layout)

        # Define a fixed size for all buttons
        button_width = 800
        button_height = 50

        # Roll button
        self.roll_button = QPushButton("Roll")
        self.roll_button.setFixedSize(button_width, button_height)
        button_layout.addWidget(self.roll_button)
        self.roll_button.clicked.connect(self.roll)

        # Question button
        self.question_button = QPushButton("Question")
        self.question_button.setFixedSize(button_width, button_height)
        button_layout.addWidget(self.question_button)
        self.question_button.clicked.connect(self.get_question)

        # Placeholder button (when no action is required)
        self.placeholder_button = QPushButton("")
        self.placeholder_button.setFixedSize(button_width, button_height)
        self.placeholder_button.setVisible(False)  # Initially hidden
        button_layout.addWidget(self.placeholder_button)

        # Initially, only the roll button should be visible
        self.update_buttons()

    def update_buttons(self):
        # Hide all buttons initially
        self.roll_button.setVisible(False)
        self.question_button.setVisible(False)
        self.placeholder_button.setVisible(False)

        # Show the appropriate button based on the game state
        if self.game.state == State.ROLL:
            self.roll_button.setVisible(True)
            self.roll_button.setEnabled(True)
        elif self.game.state == State.QUESTION:
            self.question_button.setVisible(True)
            self.question_button.setEnabled(True)
        else:
            self.placeholder_button.setVisible(True)

    def display_timer(self):
        self.timer_label = QLabel("Time: 00:00", self)
        self.timer_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setGeometry(10, 10, 100, 30)
        self.timer_label.show()

    def update_timer(self):
        self.time_elapsed = self.time_elapsed.addSecs(1)
        self.timer_label.setText(f'Time: {self.time_elapsed.toString("mm:ss")}')

    def display_current_player(self):
        index, first_player = next(enumerate(self.game.players))
        self.current_player_label = QLabel(f"Current Player: {self.player_names[index]}", self)
        self.current_player_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.current_player_label.setAlignment(Qt.AlignCenter)
        self.current_player_label.setGeometry(
            (self.width() - 30) // 2, 16, 200, 30
        )
        self.current_player_label.show()
        
    def display_roll_outcome(self):
        self.roll_label = QLabel('', self)
        self.roll_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.roll_label.setAlignment(Qt.AlignCenter)
        self.roll_label.setGeometry(
            (self.width() - 30) // 2, 38, 200, 30
        )
        self.roll_label.show()

    def category_legend(self):
        category_icons = ['yellow_category_icon.png', 'blue_category_icon.png', 'green_category_icon.png', 'red_category_icon.png']
        for i in range(len(category_icons)):
            category_label = QLabel(self.bg_label)
            category_path = f'images/{category_icons[i]}'
            category_pixmap = QPixmap(category_path).scaled(30, 30, Qt.KeepAspectRatio)
            category_label.setPixmap(category_pixmap)
            category_label.setScaledContents(True)
            if i == 0 or i == 1:
                x_position = 10
                y_position = 735 + 30*i
            else:
                x_position = 200
                y_position = 735 + 30*(i-2)
            category_label.move(x_position, y_position)
            category_label.show()

            category_name = QLabel(self.bg_label)
            category_name.setText(f"{self.selected_categories[i]}")
            category_name.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
            category_name.move(x_position+34, y_position+6)
            category_name.show()

    def roll(self):
        if self.game.state != State.ROLL:
            return
        
        roll_result = self.server.roll()
        if roll_result == -1:
            return

        print(f"Rolled: {roll_result}")
        self.roll_label.setText(f'Rolled: {roll_result}')
        
        self.update_buttons()
        self.move()
    
    def move(self):
        dirs = self.server.get_available_directions()
        selected_direction = None
        
        # If the player can still choose a direction, display the direction selection dialog
        if dirs:
            dialog = DirectionDialog(dirs, self.game.active_player().name, self.game.roll)
            if dialog.exec_() == QDialog.Accepted:
                selected_direction = dialog.selected_direction
                print(f"Selected Direction: {selected_direction}")
        
        # Move the player based on the selected direction or predefined direction
        self.game = self.server.move(selected_direction)
        print(f"Player moved to location {self.game.active_player().location}")
        self.update_player_positions()

        self.update_buttons()

        # Check if the player has 4 categories and is at the center square
        player = self.game.active_player()
        player_score = self.server.get_score(player)
        
        # Trigger the category selection dialog only when the player reaches the center with 4 categories
        if player.location == 99 and len(player_score) == 4:
            print("Player landed on the center square with all categories. Showing category selection dialog.")
            self.show_category_selection_dialog()
            
        if self.game.active_square().kind == Kind.ROLL_AGAIN:
            self.show_roll_again_prompt()
        
        # Continue moving if there are remaining moves
        if self.game.roll > 0:
            self.move()
            
    def show_roll_again_prompt(self):
        roll_again_dialog = QDialog(self)
        roll_again_dialog.setWindowTitle("Roll Again!")
        
        layout = QVBoxLayout()
        prompt_label = QLabel("You landed on a Roll Again spot! Please roll again.")
        layout.addWidget(prompt_label)
        
        ok_button = QPushButton("OK")
        layout.addWidget(ok_button)
        ok_button.clicked.connect(roll_again_dialog.accept)  # Close the dialog when OK is clicked
        
        roll_again_dialog.setLayout(layout)
        roll_again_dialog.exec_()

    def get_question(self):
        if not self.question_button.isEnabled():
            return  # If the button is already disabled, do nothing

        self.question_button.setEnabled(False)  # Disable the button immediately after it's clicked

        question_obj: Question = self.server.get_question()
        if question_obj == -1:
            self.question_button.setEnabled(True)  # Re-enable the button if no question is retrieved
            return

        question = question_obj.question
        answer = question_obj.answer
        category = question_obj.category

        if self.question_overlay:
            self.question_overlay.setParent(None)
        
        self.question_overlay = QuestionOverlay(self, category, question, answer)
        self.question_overlay.setGeometry(62, 170, 700, 450)
        self.question_overlay.correct_button.clicked.connect(lambda: self.handle_question_answer(True))
        self.question_overlay.incorrect_button.clicked.connect(lambda: self.handle_question_answer(False))
        self.question_overlay.show()
        self.roll_label.setText('')

    def show_category_selection_dialog(self):
        category_dialog = QDialog(self)
        category_dialog.setWindowTitle("Select a Category")
        
        layout = QVBoxLayout()
        instruction_label = QLabel("Please select a category for the final question:")
        layout.addWidget(instruction_label)
        category_combo = QComboBox(category_dialog)
        category_combo.addItems(self.selected_categories)
        layout.addWidget(category_combo)
        ok_button = QPushButton("OK")
        layout.addWidget(ok_button)
        category_dialog.setLayout(layout)
        ok_button.clicked.connect(lambda: self.category_selected(category_combo.currentText(), category_dialog))
        category_dialog.exec_()


    def category_selected(self, selected_category, dialog):
        print(f"Selected category: {selected_category}")
        dialog.accept()  # Close the dialog
        
        # Retrieve a question from the selected category
        question = self.server.get_question(selected_category)
        
        if question:
            # Create the QuestionOverlay and display it
            self.question_overlay = QuestionOverlay(self, question.category, question.question, question.answer)
            self.question_overlay.setGeometry(62, 170, 700, 450)  # Adjust size and position as needed

            # Connect the correct and incorrect buttons to the appropriate handlers
            self.question_overlay.correct_button.clicked.connect(lambda: self.handle_question_answer(True))
            self.question_overlay.incorrect_button.clicked.connect(lambda: self.handle_question_answer(False))

            # Show the overlay
            self.question_overlay.show()
        else:
            print("No question found for the selected category")
    
    def handle_question_answer(self, correct):
        self.question_overlay.hide()
        verify = self.server.verify_question(correct)
        self.game = verify
        self.current_player_label.setText(f'Current Player: {self.game.active_player().name}')
        self.update_player_positions()

        # Re-enable the question button
        self.question_button.setEnabled(True)

        # Updated logic to consider final question
        player = self.game.active_player()
        player_score = self.server.get_score(player)

        # Check if the player is at the center square with all categories and answered correctly
        if correct and player.location == 99 and len(player_score) == 4:
            self.show_winner_screen(player.name)  # Show the winner screen
        else:
            if correct:
                self.update_player_score()

        # Check if it's time to roll again or move on
        if self.game.state == State.ROLL:
            self.show_roll_button()
        else:
            self.show_question_button()

    def show_roll_button(self):
        self.question_button.hide()
        self.roll_button.setEnabled(True)
        self.roll_button.show()

    def show_question_button(self):
        self.roll_button.hide()
        self.question_button.setEnabled(True)
        self.question_button.show()


    def show_winner_screen(self, winner_name):
        # Hide player names, scores, and icons from the background screen
        for label in self.player_info_labels + self.player_widgets:
            label.hide()

        # Stop the game timer
        self.timer.stop()

        # Calculate final gameplay time
        final_time = self.time_elapsed.toString("mm:ss")

        # Create the winner screen background
        winner_bg_label = QLabel(self)
        winner_bg_pixmap = QPixmap('images/winner_screen.png')
        winner_bg_label.setPixmap(winner_bg_pixmap)
        winner_bg_label.setScaledContents(True)
        winner_bg_label.setGeometry(self.rect())
        winner_bg_label.show()

        # Calculate rankings based on score
        rankings = sorted(self.game.players, key=lambda p: len(p.score), reverse=True)
        
        # Create the winner message and ranking details
        winner_message = f"{winner_name} has won the game with a time of {final_time}!"
        ranking_details = "\n\nFinal Rankings:\n"
        for idx, player in enumerate(rankings):
            ranking_details += f"{idx + 1}. {player.name} with {len(player.score)} categories collected\n"

        # Create the pop-up dialog with winner message and rankings
        winner_dialog = QDialog(self)
        winner_dialog.setWindowTitle("Game Over")
        winner_dialog_layout = QVBoxLayout()
        
        winner_label = QLabel(winner_message)
        winner_label.setAlignment(Qt.AlignCenter)
        winner_dialog_layout.addWidget(winner_label)
        
        ranking_label = QLabel(ranking_details)
        ranking_label.setAlignment(Qt.AlignCenter)
        winner_dialog_layout.addWidget(ranking_label)

        # Create buttons for returning to the main menu and exiting the game
        button_layout = QHBoxLayout()
        return_to_menu_button = QPushButton("Return to Main Menu")
        return_to_menu_button.clicked.connect(lambda: self.return_to_menu(winner_dialog))
        exit_game_button = QPushButton("Exit Game")
        exit_game_button.clicked.connect(self.exit_game)
        
        button_layout.addWidget(return_to_menu_button)
        button_layout.addWidget(exit_game_button)
        
        winner_dialog_layout.addLayout(button_layout)
        winner_dialog.setLayout(winner_dialog_layout)
        
        winner_dialog.exec_()

    def return_to_menu(self, winner_dialog):
        winner_dialog.accept()
        self.parent().parent().show_main_menu()

    def exit_game(self):
        QApplication.quit()

    def update_player_score(self):
        for i,player in enumerate(self.game.players):
            scores = self.server.get_score(player)
            scoreLabel = f"{player.name}\n\nCategories Acquired:\n"
            for cat in scores:
                scoreLabel += '\n' + cat
            self.player_info_labels[i].setText(scoreLabel)
            self.player_info_labels[i].setAlignment(Qt.AlignCenter)
            self.player_info_labels[i].setFixedSize(200, 110)

    def update_player_positions(self):
        for i, player in enumerate(self.game.players):
            x, y = self.calculate_position_on_background(self.game.board.index_map[player.location].y_x)
            offsets = [
                (0, 0),
                (self.grid_square_size - 30, 0),
                (0, self.grid_square_size - 30),
                (self.grid_square_size - 30, self.grid_square_size - 30)
            ]
            offset_x, offset_y = offsets[i]
            self.player_widgets[i].move(int(x + offset_x), int(y + offset_y))

    def calculate_position_on_background(self, y_x):
        x = self.outer_margin + y_x[1] * self.grid_square_size
        y = self.outer_margin + y_x[0] * self.grid_square_size
        return x, y

class QuestionOverlay(QWidget):
    def __init__(self, parent, category_name, question, answer):
        super().__init__(parent)
        # Set a modern style with padding and borders
        self.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.95); 
            border-radius: 15px; 
            border: 2px solid #cccccc;
            padding: 20px;
            font-family: Arial, sans-serif;
        """)
        self.setFixedSize(700, 450)

        layout = QVBoxLayout(self)
        
        # Category and Question styling
        category_label = QLabel(f"<b style='font-size:18px;'>Category:</b> {category_name}")
        category_label.setAlignment(Qt.AlignCenter)
        question_label = QLabel(f"<b style='font-size:18px;'>Question:</b> {question}")
        question_label.setWordWrap(True)
        question_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(category_label)
        layout.addSpacing(2)
        layout.addWidget(question_label)
        
        # Answer display
        self.answer_label = QLabel(f"<b style='font-size:18px;'>Answer:</b> {answer}")
        self.answer_label.setVisible(False)
        self.answer_label.setWordWrap(True)
        self.answer_label.setAlignment(Qt.AlignCenter)
        layout.addSpacing(2)
        layout.addWidget(self.answer_label)

        # Button Layout with modern style
        button_layout = QHBoxLayout()
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                color: black;
                font-size: 20px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #00F059;  /* Green hover color */
            }
        """

        # Correct Button
        self.correct_button = QPushButton('Correct')
        self.correct_button.setStyleSheet(button_style)
        button_layout.addWidget(self.correct_button)

        # Incorrect Button with specific style
        self.incorrect_button = QPushButton('Incorrect')
        self.incorrect_button.setObjectName("IncorrectButton")  # Assign object name
        self.incorrect_button.setStyleSheet("""
            QPushButton#IncorrectButton {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                color: black;
                font-size: 20px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton#IncorrectButton:hover {
                background-color: #FF6347;  /* Tomato hover color for Incorrect button */
            }
        """)
        button_layout.addWidget(self.incorrect_button)

        # Show Answer Button
        self.show_answer_button = QPushButton('Show Answer')
        self.show_answer_button.setStyleSheet(button_style)
        button_layout.addWidget(self.show_answer_button)

        layout.addSpacing(2)
        layout.addLayout(button_layout)

        self.show_answer_button.clicked.connect(self.toggle_answer)

    def toggle_answer(self):
        if self.answer_label.isVisible():
            self.answer_label.setVisible(False)
            self.show_answer_button.setText('Show Answer')
        else:
            self.answer_label.setVisible(True)
            self.show_answer_button.setText('Hide Answer')

class TrivialComputeClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server = TrivialComputeServer()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Trivial Compute')

        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_menu = MainMenu(self)
        self.player_selection = PlayerSelection(self)
        self.player_customization = PlayerCustomization(self)
        self.category_selection = CategorySelection(self)

        self.central_widget.addWidget(self.main_menu)
        self.central_widget.addWidget(self.player_selection)
        self.central_widget.addWidget(self.player_customization)
        self.central_widget.addWidget(self.category_selection)

        self.show_main_menu()

    def show_main_menu(self):
        self.central_widget.setCurrentWidget(self.main_menu)

    def show_player_selection(self):
        self.central_widget.setCurrentWidget(self.player_selection)

    def show_player_customization(self, player_count=None):
        if player_count:
            self.num_players = player_count
        self.player_customization = PlayerCustomization(self, self.num_players)
        self.central_widget.addWidget(self.player_customization)
        self.central_widget.setCurrentWidget(self.player_customization)

    def show_category_selection(self):
        self.category_selection = CategorySelection(self, self.num_players)
        self.central_widget.addWidget(self.category_selection)
        self.central_widget.setCurrentWidget(self.category_selection)

    def start_board_game(self, categories):
        player_names = self.player_customization.get_player_names()
        print(f"Starting board game with categories: {categories}")
        self.game = self.server.start_game(player_names, categories)
        self.board_widget = BoardWidget(self.server, self.game, player_names, categories)
        self.central_widget.addWidget(self.board_widget)
        self.central_widget.setCurrentWidget(self.board_widget)


class MainMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.central_widget = self.parent().central_widget

        self.bg_label = QLabel(self)
        self.bg_pixmap = QPixmap('images/Main Menu.png')
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(self.rect())

        self.button_layout = QVBoxLayout(self)
        self.button_layout.setContentsMargins(0, 350, 0, 0)
        self.button_layout.setAlignment(Qt.AlignCenter)

        self.add_image_button(self.button_layout, 'images/play_button.png', 'images/play_button_hover.png', self.parent().show_player_selection)
        self.add_image_button(self.button_layout, 'images/how_to_play_button.png', 'images/how_to_play_button_hover.png', self.how_to_play)
        self.add_image_button(self.button_layout, 'images/creator_mode_button.png', 'images/creator_mode_button_hover.png', self.creator_mode)
        self.add_image_button(self.button_layout, 'images/help_button.png', 'images/help_button_hover.png', self.help)

        overlay_layout = QVBoxLayout(self)
        overlay_layout.addWidget(self.bg_label)
        overlay_layout.addLayout(self.button_layout)

        if not self.layout():
            self.setLayout(overlay_layout)

        self.resizeEvent = self.resize_background

    def resize_background(self, event):
        self.bg_label.setGeometry(self.rect())

    def add_image_button(self, layout, normal_image_path, hover_image_path, func):
        button = ImageButton(self, normal_image_path, hover_image_path, func)
        layout.addWidget(button)

    def how_to_play(self):
        print("How To Play")
        current_directory = os.getcwd()
        instruction_path = os.path.abspath(os.path.join(current_directory, "How_to_Play_Trivial_Compute.pdf"))

        os_type = platform.system()

        if os_type == "Windows":
            # open PDF in default web browser
            webbrowser.open(instruction_path)
        else:
            subprocess.call(["open", instruction_path])

    def creator_mode(self):
        os_type = platform.system()

        if os_type == "Windows":
            os.system("start EXCEL.EXE question_creator_gui.xlsx")
        else:
            subprocess.call(["open", "-a", "Microsoft Excel", "question_creator_gui.xlsx"])

    def help(self):
        print("Help")
        current_directory = os.getcwd()
        instruction_path = os.path.abspath(os.path.join(current_directory, "Trivial_Compute_Help.pdf"))

        os_type = platform.system()

        if os_type == "Windows":
            # open PDF in default web browser
            webbrowser.open(instruction_path)
        else:
            subprocess.call(["open", instruction_path])

class PlayerSelection(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.central_widget = self.parent().central_widget

        self.bg_label = QLabel(self)
        self.bg_pixmap = QPixmap('images/playerselection_screen.png')
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(self.rect())

        self.button_layout = QHBoxLayout(self)
        self.button_layout.setContentsMargins(0, 350, 0, 0)
        self.button_layout.setAlignment(Qt.AlignCenter)

        player_counts = [1, 2, 3, 4]
        for count in player_counts:
            button_path = f'images/{count}_player_button.png'
            hover_path = f'images/{count}_player_button_hover.png'
            button = ImageButton(self, button_path, hover_path, lambda _, c=count: self.start_player_customization(c))
            self.button_layout.addWidget(button)

        overlay_layout = QVBoxLayout(self)
        overlay_layout.addWidget(self.bg_label)
        overlay_layout.addLayout(self.button_layout)

        if not self.layout():
            self.setLayout(overlay_layout)

        self.resizeEvent = self.resize_background

    def resize_background(self, event):
        self.bg_label.setGeometry(self.rect())
        
    def start_player_customization(self, player_count):
        print(f"Starting customization for {player_count} players")
        self.parent().parent().show_player_customization(player_count)

class PlayerCustomization(QWidget):
    def __init__(self, parent, num_players=1):
        super().__init__(parent)
        self.num_players = num_players
        self.player_name_inputs = []
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(100, 100, 100, 100)
        self.layout.setAlignment(Qt.AlignCenter)

        self.bg_label = QLabel(self)
        bg_pixmap = QPixmap('images/playercustomization_screen.png')
        self.bg_label.setPixmap(bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bg_label.setGeometry(self.rect())

        for i in range(self.num_players):
            h_layout = QHBoxLayout()
            label = QLabel(f"Player {i+1} Name:")
            line_edit = QLineEdit()
            line_edit.setMaxLength(15)
            line_edit.setPlaceholderText(f"Player {i+1}")
            self.player_name_inputs.append(line_edit)
            h_layout.addWidget(label)
            h_layout.addWidget(line_edit)
            self.layout.addLayout(h_layout)

        back_button = ImageButton(self, 'images/back_button.png', 'images/back_button_hover.png', self.show_player_selection)
        continue_button = ImageButton(self, 'images/continue_button.png', 'images/continue_button_hover.png', self.save_player_names_and_continue)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(back_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(continue_button)
        self.layout.addLayout(buttons_layout)

        self.setLayout(self.layout)
        
    def get_player_names(self):
        return [input.text() if input.text() else f"Player {i+1}" for i, input in enumerate(self.player_name_inputs)]

    def save_player_names_and_continue(self):
        player_names = self.get_player_names()
        print("Player names:", player_names)
        self.parent().parent().show_category_selection()

    def show_player_selection(self):
        self.parent().parent().show_player_selection()

    def resizeEvent(self, event):
        self.bg_label.resize(self.size())
        super().resizeEvent(event)

class CategorySelection(QWidget):
    def __init__(self, parent, num_players=1):
        super().__init__(parent)
        self.num_players = num_players
        self.categories = self.parent().server.get_categories_excel()
        self.initUI()

    def initUI(self):
        # Main layout for the entire screen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)

        # Background label setup
        self.bg_label = QLabel(self)
        bg_pixmap = QPixmap('images/categoryselection_screen.png')
        self.bg_label.setPixmap(bg_pixmap)
        self.bg_label.setScaledContents(True)
        main_layout.addWidget(self.bg_label)

        # Create a container widget for the form and buttons
        content_widget = QWidget(self.bg_label)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(50, 50, 50, 50)
        content_layout.setAlignment(Qt.AlignCenter)

        # Form layout for category selection
        self.form_layout = QVBoxLayout()
        self.form_layout.setAlignment(Qt.AlignCenter)

        self.category_layouts = []
        for i in range(4):
            h_layout = QHBoxLayout()
            label = QLabel(f"Category {i + 1}:")
            combo_box = QComboBox()
            combo_box.addItems(self.categories)
            h_layout.addWidget(label)
            h_layout.addWidget(combo_box)
            self.category_layouts.append((label, combo_box))
            self.form_layout.addLayout(h_layout)

        # Add form layout to content layout
        content_layout.addLayout(self.form_layout)

        # Add vertical spacing between the category selection and the buttons
        content_layout.addSpacing(40)  # Increase this value for more spacing

        # Buttons layout setup
        self.buttons_layout = QHBoxLayout()
        back_button = ImageButton(self, 'images/back_button.png', 'images/back_button_hover.png', self.show_player_customization)
        continue_button = ImageButton(self, 'images/continue_button.png', 'images/continue_button_hover.png', self.start_game)

        # Set the height of the buttons to prevent them from being cut off
        back_button.setFixedHeight(70)
        continue_button.setFixedHeight(70)

        # Add buttons to the layout
        self.buttons_layout.addWidget(back_button)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(continue_button)

        # Add buttons layout to the content layout (added after the form layout to ensure proper stacking)
        content_layout.addLayout(self.buttons_layout)

        # Set the geometry of the content widget to prevent clipping
        content_widget.setGeometry(100, 100, 600, 500)  # Adjust height for more spacing

        # Ensure buttons are raised above other elements
        back_button.raise_()
        continue_button.raise_()

        self.resizeEvent = self.resize_background

    def resize_background(self, event):
        # Dynamically resize the background label
        self.bg_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def show_player_customization(self):
        self.parent().parent().show_player_customization(self.num_players)

    def start_game(self):
        selected_categories = self.get_selected_categories()
        print("Selected Categories:", selected_categories)
        self.parent().parent().start_board_game(selected_categories)

    def get_selected_categories(self):
        return [combo.currentText() for _, combo in self.category_layouts]

class ImageButton(QPushButton):
    def __init__(self, parent, icon_path, hover_icon_path, action_func):
        super().__init__(parent)
        self.icon_path = icon_path
        self.hover_icon_path = hover_icon_path
        self.default_icon = QPixmap(icon_path)
        self.hover_icon = QPixmap(hover_icon_path)
        
        self.setIcon(QIcon(self.default_icon))
        self.setIconSize(self.default_icon.size())
        self.setFlat(True)
        self.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(action_func)

    def enterEvent(self, event):
        self.setIcon(QIcon(self.hover_icon))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(QIcon(self.default_icon))
        super().leaveEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TrivialComputeClient()
    client.show()
    sys.exit(app.exec_())
