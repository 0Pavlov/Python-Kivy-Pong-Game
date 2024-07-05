from kivy.animation import Animation
# noinspection PyProtectedMember
from kivy.app import App, Builder
from kivy.clock import Clock
from kivy.properties import (
    NumericProperty,
    ReferenceListProperty,
    ObjectProperty,
    ListProperty,
)
from kivy.uix.widget import Widget
from kivy.vector import Vector

from plyer import notification, vibrator

Builder.load_string(
    """
<Menu>:
    size: self.size
    center: root.parent.center
    canvas:
        Color:
            rgba: self.color
        Ellipse:
            size: self.size
            pos: self.pos
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
    menu: menu
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
    # Menu
    Menu:
        id: menu
        # Size of the circle relative to screen width
        size: self.parent.width / 4, self.parent.width / 4
        color: [0.2, 0.2, 0.2, 0.5] # Dark grey color
        # Text
        Label:
            color: 1, 1, 1, 0.7
            # Font size matches the circle size
            font_size: self.parent.width / 4
            text: 'Touch'
            # Centering the text only after defining size and the content
            center: menu.center
    """
)


# Main game class (all game logic goes here)
# Serves as the root widget
class PongGame(Widget):
    ball = ObjectProperty(None)
    player = ObjectProperty(None)
    opponent = ObjectProperty(None)
    menu = ObjectProperty(None)
    state_game_started = False

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
        # Send notification
        notification.notify('Official project page:', 'github.com/0Pavlov/Python-Kivy-Pong-Game')

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
        if self.state_game_started:
            # Reset menu size and move away the screen
            self.menu.x = self.width
            self.menu.size = self.width / 4, self.width / 4

            # Reset menu color
            self.menu.color = [0.2, 0.2, 0.2, 0.5]

            # Move the ball each frame
            self.ball.move()

            # Bounce off paddles
            self.player.bounce_ball(self.ball)
            self.opponent.bounce_ball(self.ball)

            # Bounce ball off sides
            if self.ball.x < self.x or self.ball.right > self.right:
                self.ball.velocity_x *= -1

            # Ball collision with the top or bottom of the screen
            if self.ball.top > self.top:  # Top
                vibrator.vibrate(time=0.08)
                self.player.score += 1
                self.serve_ball(vel=(4, 4))
            if self.ball.y < self.y:  # Bottom
                vibrator.vibrate(time=0.08)
                self.opponent.score += 1
                self.serve_ball(vel=(4, -4))

            # Change ball color based on its position
            if self.ball.center_y > self.center_y:
                self.ball.color = [0, 0, 0, 1]
            elif self.ball.center_y < self.center_y:
                self.ball.color = [1, 1, 1, 1]

            # Game end condition
            if self.opponent.score == 3 or self.player.score == 3:
                # Hide the ball when game waits for restart
                self.ball.color = [0, 0, 0, 0]
                # Update the game state
                self.state_game_started = False
                # Bring the menu back from the out the screen
                self.menu.center = self.center
                # Do something if player wins
                if self.player.score == 3:
                    pass
                # Do something if opponent wins
                elif self.opponent.score == 3:
                    pass

    # Make paddles movable
    def on_touch_move(self, touch):
        touch_player_side = touch.y < self.height / 2
        touch_opponent_side = touch.y > self.height / 2
        ball_to_player_distance = abs(self.ball.center_y) - abs(self.player.top)
        ball_to_opponent_distance = abs(self.opponent.y) - abs(self.ball.center_y)
        ball_radius = self.ball.height / 2

        # Restrict paddle movement to avoid tunneling
        if touch_player_side:
            if ball_to_player_distance > ball_radius:
                self.player.center_x = touch.x
        elif touch_opponent_side:
            if ball_to_opponent_distance > ball_radius:
                self.opponent.center_x = touch.x

    # Register the touch for the menu button
    def on_touch_down(self, touch):
        anim = Animation(
            size=(self.ball.width * 1.5, self.ball.width * 1.5),
            color=(0, 0, 0, 0),
            center=self.ball.center,
            t='in_out_cubic',
            duration=0.7,
        )
        if self.menu.collide_point(*touch.pos):
            # Animation
            anim.start(self.menu)
            # Reset the scores
            self.opponent.score = 0
            self.player.score = 0
            # Update the game state
            self.state_game_started = True

    class Menu(Widget):
        color = ListProperty([0, 0, 0, 0])

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
            # Ball center vertex
            ball_center = Vector(ball.center_x, ball.center_y)

            # Ball velocity
            vx, vy = ball.velocity

            if self.collide_widget(ball):
                # Find the closest point on the paddle to the ball's center
                closest_point = self.get_closest_point(ball_center)

                # Calculate the collision normal vector
                normal = (ball_center - closest_point).normalize()

                # Calculate the relative velocity of the ball to the paddle
                relative_velocity = Vector(vx, vy)  # Assuming the paddle is stationary

                # Calculate the dot product of the relative velocity and the normal
                dot_product = relative_velocity.dot(normal)

                # Reflect the relative velocity across the collision normal
                reflection = relative_velocity - 2 * dot_product * normal

                # Speed increase
                speed_multiplier = 1.2  # Adjust this value for the desired speed increase
                if abs(reflection.y) < self.height:
                    reflection *= speed_multiplier

                # Apply the reflected velocity to the ball
                ball.velocity = reflection.x, reflection.y

        def get_closest_point(self, point):
            """Finds the closest point on the paddle's rectangle to a given point."""
            closest_x = max(self.x, min(point.x, self.right))
            closest_y = max(self.y, min(point.y, self.top))
            return Vector(closest_x, closest_y)


# App class (build method should return root widget object)
class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 120.0)
        return game


if __name__ == "__main__":
    PongApp().run()