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
        x: root.width / 2 - self.width / 2
        # Vertical position relative to the half of the screen
        y: root.y + self.height
        text: str(root.player.score)

    Label:
        id: opponent_score
        color: 0, 0, 0, 1
        # Size relative to the half of the screen
        font_size: root.height / 2 / 15
        size: self.texture_size
        x: root.width / 2 - self.width / 2
        # Vertical position relative to the half of the screen
        y: root.height - self.height * 2
        text: str(root.opponent.score)

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
        # Vertical position relative to the player score
        y: player_score.top + player_score.height
        color: 1, 1, 1, 1

    PongPaddle:
        id: opponent
        # Size relative to the half of the screen
        size: self.parent.width / 6, self.parent.height / 2 / 18
        center_x: self.parent.width / 2
        # Vertical position relative to the opponent score
        top: opponent_score.y - opponent_score.height
        color: 0, 0, 0, 1
    """
)


# Main game class (all game logic goes here)
# Serves as the root widget
class PongGame(Widget):
    ball = ObjectProperty(None)
    player = ObjectProperty(None)
    opponent = ObjectProperty(None)
    state_game_started = False
    state_game_over = False

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        """
        Call the center_ball_on_init function only after the layout is calculated.
        The ball serving is scheduled for the next frame using Clock.schedule_once()
        to ensure that it happens after the initial layout is calculated. This
        prevents issues with incorrect ball positioning.
        """
        Clock.schedule_once(self.center_ball_on_init, 0.4)
        self.serve_ball(vel=(4, -4))  # Initial serve

    # noinspection PyUnusedLocal
    def center_ball_on_init(self, dt):
        """
        Center the ball

        Args:
            dt(float): delta time parameter, used during the __init__
        """
        self.ball.center = self.center

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

        # Bounce off paddles
        self.player.bounce_ball(self.ball)
        self.opponent.bounce_ball(self.ball)

        # Bounce ball off sides
        if self.ball.x < self.x or self.ball.right > self.right:
            self.ball.velocity_x *= -1

        # Bounce ball off top or bottom
        if self.ball.top > self.top:  # Top
            self.serve_ball(vel=(4, 4))
            self.player.score += 1
        if self.ball.y < self.y:
            self.serve_ball(vel=(4, -4))
            self.opponent.score += 1

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

        def bounce_ball(self, ball):
            if self.collide_widget(ball):
                # Ball velocity
                vx, vy = ball.velocity

                # Adjust the horizontal bounce based on contact point
                offset = (ball.center_y - self.center_y) / (self.height / 2)

                # Reverse vertical velocity
                bounced = Vector(vx, vy * -1)

                # Speed up on each bounce
                vel = bounced * 1.1

                # Apply changes
                ball.velocity = vel.x, vel.y + offset


# App class (build method should return root widget object)
class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 120.0)
        return game


if __name__ == "__main__":
    PongApp().run()
