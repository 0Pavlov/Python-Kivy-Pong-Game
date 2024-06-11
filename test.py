from kivy.app import App
from kivy.uix.widget import Widget
# noinspection PyProtectedMember
from kivy.app import Builder
from kivy.properties import (
    NumericProperty,
    ReferenceListProperty,
    ObjectProperty,
    ListProperty,
)
from kivy.vector import Vector
from kivy.clock import Clock

Builder.load_string(
    """
<PongBall>:
    size: self.size
    canvas:
        Color:
            rgba: self.color
        Ellipse:
            pos: self.pos
            size: self.size
            
<PongPaddle>:
    id: pong_paddle
    score: root.score
    canvas:
        Color:
            rgba: root.color
        Rectangle:
            pos: self.pos
            size: self.size
    
<PongGame>:
    ball: pong_ball
    player: player
    opponent: opponent
    # Backgrounds
    canvas:
        # Player background
        Color:
            rgba: 0, 0, 0, 1
        # Player background rectangle
        Rectangle:
            id: player_background
            pos: 0, 0  # Screen bottom half
            size: self.width, self.height / 2

        # Opponent background
        Color:
            rgba: 1, 1, 1, 1
        # Opponent background rectangle
        Rectangle:
            id: opponent_background
            pos: 0, self.height / 2 # Screen top half
            size: self.width, self.height / 2
            
        # Screen center line (debug)
        Color:
            rgba: 1, 0, 0, 0
        Rectangle:
            id: split_line
            pos: self.width / 2, self.y
            size: 1, self.height
    
    # Score labels        
    Label:
        id: player_score
        color: 1, 1, 1, 1
        # Size relative to the half of the screen
        font_size: root.height / 2 / 15
        size: self.texture_size
        center_x: root.width / 2
        # Vertical position relative to the half of the screen
        y: root.y
        text: '0'
            
    Label:
        id: opponent_score
        color: 0, 0, 0, 1
        # Size relative to the half of the screen
        font_size: root.height / 2 / 15
        size: self.texture_size
        center_x: root.width / 2
        # Vertical position relative to the half of the screen
        y: root.height - self.height
        text: '0'
        
    # Ball
    PongBall:
        id: pong_ball
        center: self.parent.center
        # Size relative to the size of the screen
        size: self.parent.height / 30, self.parent.height / 30
        
    # Paddles
    PongPaddle:
        id: player
        # Size relative to the half of the screen
        size: self.parent.width / 6, self.parent.height / 2 / 18
        center_x: self.parent.width / 2
        # Vertical position relative to the half of the screen
        center_y: self.parent.y + self.parent.height / 2 / 13
        color: 1, 1, 1, 0
        
    PongPaddle:
        id: opponent
        # Size relative to the half of the screen
        size: self.parent.width / 6, self.parent.height / 2 / 18
        center_x: self.parent.width / 2
        # Vertical position relative to the half of the screen
        center_y: self.parent.top - self.parent.height / 2 / 13
        color: 0, 0, 0, 0
    """
)


# Main game class (all game logic goes here)
# Serves as the root widget
class PongGame(Widget):
    ball = ObjectProperty(None)
    state_game_started = False
    state_game_over = False

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.serve_ball()

    def serve_ball(self, vel=(4, 4)):
        """
        Serve the ball to some direction

        Args:
             vel (tuple): Direction to serve the ball
        """
        self.ball.center = self.center
        self.ball.velocity = vel

    # noinspection PyUnusedLocal
    def update(self, dt):
        """
        Update the screen each time Apps Clock inside the build method, ticks

        Args:
            dt (delta-time): How often the screen updates
        """
        self.ball.move()

        # Bounce ball off sides
        if self.ball.x < self.x or self.ball.right > self.right:
            self.ball.velocity_x *= -1

        # Bounce ball off top or bottom
        if self.ball.y < self.y or self.ball.top > self.top:
            self.ball.velocity_y *= -1

        # Change ball color based on its position
        if self.ball.center_y > self.center_y:
            self.ball.color = [0, 0, 0, 1]
        elif self.ball.center_y < self.center_y:
            self.ball.color = [1, 1, 1, 1]

    class PongBall(Widget):
        color = ListProperty([0, 0, 0, 0])
        velocity_x = NumericProperty(0)
        velocity_y = NumericProperty(0)
        velocity = ReferenceListProperty(velocity_x, velocity_y)

        def move(self):
            """
            Move the ball from the current position with the current velocity
            """
            self.pos = Vector(*self.pos) + self.velocity

    class PongPaddle(Widget):
        color = ListProperty([1, 0, 0, 1])
        score = NumericProperty(0)


# App class (build method should return root widget object)
class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 120.0)
        return game


if __name__ == "__main__":
    PongApp().run()
