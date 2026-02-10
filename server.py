import random
import pandas as pd
from enum import Enum
from typing import Self, Union, Set

TO_WIN = 4

class Direction(Enum):
    CLOCKWISE = "CL"
    COUNTER_CLOCKWISE = "CC"
    DOWN = "D"
    UP = "U"
    LEFT = "L"
    RIGHT = "R"
    
    @classmethod
    def get_delta(cls, direction):
        delta = {
            Direction.LEFT: (0, -1),
            Direction.RIGHT: (0, 1),
            Direction.UP: (-1, 0),
            Direction.DOWN: (1, 0)
        }
        return delta[direction]

class Player:
    def __init__(self, name):
        self.name = name
        self.score: Set = set()
        self.direction = Direction.CLOCKWISE
        self.location = 99
        
    def __str__(self):
        return f"{self.name}: ind {self.location}, {self.direction}"

class Kind(Enum):
    EMPTY = 0
    CATEGORY1 = 1
    CATEGORY2 = 2
    CATEGORY3 = 3
    CATEGORY4 = 4
    ROLL_AGAIN = 5
    CHAMPION = 6
    
CategoryKind = Union[Kind.CATEGORY1, Kind.CATEGORY2, Kind.CATEGORY3, Kind.CATEGORY4]

class Square:
    def __init__(self, index: int, y_x: tuple, is_hub: bool, kind: Kind):
        self.index = index
        self.y_x = y_x
        self.is_hub = is_hub
        self.kind = kind

    def __str__(self) -> str:
        return f"Square(index={self.index}, y_x={self.y_x}, is_hub={self.is_hub}, kind={self.kind})"

class Board:
    def __init__(self):
        self.board_indexes = [
            [ 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [32,-1,-1,-1,35,-1,-1,-1,10],
            [31,-1,-1,-1,36,-1,-1,-1,11],
            [30,-1,-1,-1,37,-1,-1,-1,12],
            [29,59,60,61,99,45,44,43,13],
            [28,-1,-1,-1,53,-1,-1,-1,14],
            [27,-1,-1,-1,52,-1,-1,-1,15],
            [26,-1,-1,-1,51,-1,-1,-1,16],
            [25,24,23,22,21,20,19,18,17],
        ]
        self.hubs = [5, 13, 21, 29]
        self.champion = [99]
        self.roll_again = [1,9,17,25]
        self.category1 = [2,6,11,15,20,24,29,35,44,53]
        self.category2 = [3,7,12,16,21,26,30,36,45,59]
        self.category3 = [4,8,13,18,22,27,31,37,51,60]
        self.category4 = [5,10,14,19,23,28,32,43,52,61]

        self.index_map = self.create_index_map()

    def create_index_map(self):
        index_map = {}
        for i, row in enumerate(self.board_indexes):
            for j, idx in enumerate(row):
                if idx == -1:
                    kind = Kind.EMPTY
                elif idx in self.champion:
                    kind = Kind.CHAMPION
                elif idx in self.roll_again:
                    kind = Kind.ROLL_AGAIN
                elif idx in self.category1:
                    kind = Kind.CATEGORY1
                elif idx in self.category2:
                    kind = Kind.CATEGORY2
                elif idx in self.category3:
                    kind = Kind.CATEGORY3
                elif idx in self.category4:
                    kind = Kind.CATEGORY4
                y_x = (i, j)
                is_hub = idx in self.hubs
                square = Square(index=idx, y_x=y_x, is_hub=is_hub, kind=kind)
                index_map[idx] = square
        return index_map
        
    def force_center_direction(self, player: Player):
        if len(player.score) < TO_WIN:
            return

        if player.location in [5,35,36,37]:
            player.direction = Direction.DOWN
        if player.location in [13,43,44,45]:
            player.direction = Direction.LEFT
        if player.location in [21,51,52,53]:
            player.direction = Direction.UP
        if player.location in [29,59,60,61]:
            player.direction = Direction.RIGHT
    
    # ------------ KS Changes         
    def move_player(self, player: Player):
        # Force movement towards the center if the player has more than TO_WIN categories
        if player.location in self.hubs and len(player.score) >= TO_WIN:
            self.force_center_direction(player)      

        # Clockwise or counterclockwise movement around the outer ring
        if player.direction == Direction.CLOCKWISE:
            player.location = player.location + 1 if player.location != 32 else 1
        elif player.direction == Direction.COUNTER_CLOCKWISE:
            player.location = player.location - 1 if player.location != 1 else 32
        else:
            # Endgame logic: moving towards the center
            y, x = [v.y_x for v in self.index_map.values() if v.index == player.location][0]
            dy, dx = Direction.get_delta(player.direction)
            new_y, new_x = y + dy, x + dx

            # Boundary check to prevent IndexError
            if 0 <= new_y < len(self.board_indexes) and 0 <= new_x < len(self.board_indexes[0]):
                player.location = self.board_indexes[new_y][new_x]
            else:
                print("Invalid move: out of bounds")
                return "STOP"
            
        # Stop at hubs if not moving in the outer ring
        if player.location in self.hubs and player.direction not in {Direction.CLOCKWISE, Direction.COUNTER_CLOCKWISE}:
            return "STOP"

        print(f"Player moved to location {player.location}")
        return player.location


class Question:
    def __init__(self, category, question, answer):
        self.category = category
        self.question = question
        self.answer = answer
        self.media = None

class QuestionRetriever:
    def __init__(self):
        self.table = pd.read_excel('question_creator_gui.xlsx')[["Question", "Answer", "Category"]]

    def get_categories_excel(self):
        return self.table['Category'].unique().tolist()
    
    def set_categories(self, categories):
        self.categories = categories
        
        self.question_bank = {}
        for cat in self.categories:
            self.question_bank[cat] = [Question(cat, x["Question"], x["Answer"]) for _, x in self.table.iterrows() if x['Category'] == cat]
            print(f"Loaded {len(self.question_bank[cat])} questions for category: {cat}")
            
        print(self.question_bank)
            
    def get_question(self, category: Kind):
        cat_str = None
        if category == Kind.CATEGORY1:
            cat_str = self.categories[0]
        if category == Kind.CATEGORY2:
            cat_str = self.categories[1]
        if category == Kind.CATEGORY3:
            cat_str = self.categories[2]
        if category == Kind.CATEGORY4:
            cat_str = self.categories[3]
        if cat_str not in self.question_bank or not self.question_bank[cat_str]:
            raise Exception(f"No questions available for category: {cat_str}")
        return random.choice(self.question_bank[cat_str])

class State(Enum):
    ROLL = "ROLL"
    MOVE = "MOVE"
    QUESTION = "QUESTION"
    VERIFY = "VERIFY"
    
class Game:
    def __init__(self, players):
        self.board = Board()
        self.set_players(players)
        self.state = State.ROLL
        self.turn = 0
    
    def set_players(self, players):
        print("setting players!")
        self.players = [Player(player) for player in players]
        self.turn = 0
    
    def active_player(self) -> Player:
        return self.players[self.turn]
    
    def active_square(self) -> Square:
        return self.board.index_map[self.active_player().location]
    
    def increment_turn(self):
        self.turn = (self.turn + 1) % len(self.players)
    
    def state_check(self, expected_state):
        if self.state != expected_state:
            print(f"Incorrect State. Expected {expected_state.name} but got {self.state.name}")
            return(False)
        else:
            return(True)

    def roll_dice(self) -> int:
        self.roll = random.randint(1, 6)        
        # Used for testing final roll
        # self.roll = 4
        self.state = State.MOVE
        print(f"{self.active_player().name} rolled a {self.roll}!")
        return self.roll
        
    def move(self, direction: Direction = None) -> Self:
        if direction:
            self.active_player().direction = direction
        
        while self.roll > 0:
            res = self.board.move_player(self.active_player())
            self.roll -= 1
            if res == "STOP":
                if self.roll == 0:
                    self.state = State.QUESTION
                return self
            
        # repoint towards center if necessary
        self.board.force_center_direction(self.active_player())
        
        if self.active_square().kind == Kind.ROLL_AGAIN:
            self.state = State.ROLL
        else:
            self.state = State.QUESTION
            
        print(f"{self.active_player().name} moved to {self.active_player().location} going {self.active_player().direction}")
        
        return self

    def verify_question(self, correct):
        print(f"Verifying question. Correct: {correct}")
        if correct:
            if self.active_square().is_hub:
                self.active_player().score.add(self.active_square().kind)
                self.board.force_center_direction(self.active_player())
                print(f"{self.active_player().name} got a {self.active_square().kind.name} token")
        else:
            self.increment_turn()
        self.state = State.ROLL
        print(f"State updated to {self.state.name}")
        return self

class TrivialComputeServer:
    def __init__(self):
        self.question_retriever = QuestionRetriever()
        self.player_order = []
        
    def set_player_order(self, order):
        self.player_order = list(order)

    def get_next_player(self):
        # Logic to get the next player based on the determined order
        if self.player_order:
            current_player = self.player_order.pop(0)
            self.player_order.append(current_player)
            return current_player

    def start_game(self, players, categories):
        self.game = Game(players)
        self.categories = categories
        self.question_retriever.set_categories(categories)
        print(f"Server starting game with categories: {categories}")
        return self.game
    
    def set_order(self, players):
        self.game.set_players(players)
        
        return self.game

    def get_categories_excel(self):
        return self.question_retriever.get_categories_excel()
    
    def roll(self):
        if(not self.game.state_check(State.ROLL)):
            return -1
        
        return self.game.roll_dice()
    
    def get_available_directions(self):
        loc = self.game.active_square()
        
        outside_moves = set([Direction.CLOCKWISE, Direction.COUNTER_CLOCKWISE])
        inside_moves = set(Direction) - outside_moves
        
        if loc.index in [35,36,37,43,44,45,51,52,53,59,60,61]:
            return # predetermined move
        elif loc.is_hub and len(self.game.active_player().score) >= TO_WIN:
            return # predetermined move
        elif loc.is_hub:
            return outside_moves
        elif loc.index in [99]:
            return inside_moves
        else:
            return outside_moves
    
    def move(self, direction: Direction = None):
        if(not self.game.state_check(State.MOVE) or self.game.roll <= 0):
            return -1

        return self.game.move(direction)
    
    # --------- KS Changes
    def get_question(self, category=None):
        if category:
            # Retrieve a question from the specified final category (dropdown menu)
            if category not in self.question_retriever.question_bank:
                raise ValueError(f"Category {category} does not exist in the question bank.")
            
            questions = self.question_retriever.question_bank[category]
            if not questions:
                raise ValueError(f"No questions available for category: {category}")
            
            return random.choice(questions)
        
        # If no category is specified, use existing logic to retrieve a question based on the player's current square
        if not self.game.state_check(State.QUESTION):
            return -1
        
        active_square = self.game.active_square()
        if active_square.kind not in [Kind.CATEGORY1, Kind.CATEGORY2, Kind.CATEGORY3, Kind.CATEGORY4]:
            raise Exception("No category for active square!")
        
        return self.question_retriever.get_question(active_square.kind) 

    def verify_question(self, correct):
        return self.game.verify_question(correct)
    
    def get_score(self, player):
        score = []
        if Kind.CATEGORY1 in player.score:
            score.append(self.categories[0])
        if Kind.CATEGORY2 in player.score:
            score.append(self.categories[1])
        if Kind.CATEGORY3 in player.score:
            score.append(self.categories[2])
        if Kind.CATEGORY4 in player.score:
            score.append(self.categories[3])

        return(score)
