from server import Direction, State, TrivialComputeServer
import unittest
import random

class Test_Server(unittest.TestCase):
    def test_full_game(self):
        server = TrivialComputeServer()
        game = server.start_game(['Player 1','Player 2'],['art','science'])

        ended = False
        while not ended:
            while game.state == State.ROLL:
                server.roll()
                normal_options = [Direction.CLOCKWISE, Direction.COUNTER_CLOCKWISE]
                dir = None
                if server.game.active_player().direction in normal_options:
                    dir = random.choice(normal_options)
                    print(f"Chose to move {dir.name}")

                game = server.move(dir)
                if game.state == State.ROLL:
                    print("Rolling again!")
                    continue
                if game.active_square().index == 99:
                    print("game ended!")
                    ended = True
                    break
                question = server.get_question()
                answer = random.choice([True, False])
                print(f"{game.active_player().name} answered {answer}")
                game = server.verify_question(answer)

if __name__ == '__main__':
    unittest.main()
