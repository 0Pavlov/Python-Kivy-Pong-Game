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


class PongGame(Widget):
    """Main game class for the Game. This class contains all the game logic and serves
    as the root widget.

    Attributes:
        ball (ObjectProperty): The pong ball used in the game.
        player (ObjectProperty): The player's paddle.
        opponent (ObjectProperty): The opponent's paddle.
        menu (ObjectProperty): The game menu.
        state_game_started (bool): The state of the game, indicating whether the game
        has started.
    """

    ball = ObjectProperty(None)
    player = ObjectProperty(None)
    opponent = ObjectProperty(None)
    menu = ObjectProperty(None)
    state_game_started = False

    def __init__(self, **kwargs):
        """Initializes the PongGame instance.

        Centers the ball using `center_ball_on_init()` after the layout calculation
        completes to ensure correct ball positioning. This is achieved by scheduling
        `center_ball_on_init()` for the next frame using `Clock.schedule_once()`.

        Serves the ball using `serve_ball()`.

        Sends the notification to the user about the project page.
        """
        super(PongGame, self).__init__(**kwargs)

        # Center the ball
        Clock.schedule_once(self.center_ball_on_init, 1.5)

        # Send notification
        try:
            notification.notify(
                app_name="Pong",
                title="Official project page:",
                message="github.com/0Pavlov/Python-Kivy-Pong-Game",
            )
        except Exception as e:
            print(f"NotificationError: can't send the notification. {type(e)}")

        # Initial serve
        self.serve_ball(vel=(4, -4))

    # noinspection PyUnusedLocal
    def center_ball_on_init(self, dt: float) -> None:
        """Centers the ball.

        Args:
            dt (float): Delta time parameter, used during the `__init__` for being able
            to schedule functions.
        """
        self.ball.center = self.center

    def serve_ball(self, vel: tuple = (4, 4)) -> None:
        """Serves the ball.

        Serves the ball from the center of the screen with a given velocity.

        Args:
            vel (tuple, optional): Velocity of the ball. Defaults to (4, 4).
        """
        self.ball.center = self.center
        self.ball.velocity = vel

    # noinspection PyUnusedLocal
    def update(self, dt: float) -> None:
        """Updates the game state.

        Moves the ball, checks for collisions, updates scores, and handles game logic.
        Updates the screen each time `PongApp()`s `Clock.schedule_interval()` inside
        the `build()` method ticks.

        Args:
            dt (float): Delta time parameter.
        """
        if self.state_game_started:
            # Reset menu size and move off the screen
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
                try:
                    vibrator.vibrate(time=0.08)
                except Exception as e:
                    print(
                        "Ball hit the top.",
                        "Bzzzz: vibration not supported on your device ;((",
                        f"\n{type(e)}",
                    )
                finally:
                    self.player.score += 1
                    self.serve_ball(vel=(4, 4))

            if self.ball.y < self.y:  # Bottom
                try:
                    vibrator.vibrate(time=0.08)
                except Exception as e:
                    print(
                        "Ball hit the bottom.",
                        "Bzzzz: vibration not supported on your device ;((",
                        f"\n{type(e)}",
                    )
                finally:
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
                # Bring the menu back from out of the screen
                self.menu.center = self.center
                # Do something if player wins
                if self.player.score == 3:
                    pass
                # Do something if opponent wins
                elif self.opponent.score == 3:
                    pass

    def on_touch_move(self, touch) -> None:
        """Moves the paddles.

        Moves paddles based on touch position and restricts movement to prevent
        tunneling. Utilizes Kivy touch detection for that matter.

        Args:
            touch (kivy.input.motionevent.MotionEvent): The touch event.
        """
        touch_player_side = touch.y < self.height / 2
        touch_opponent_side = touch.y > self.height / 2
        ball_to_player_distance = abs(self.ball.center_y) - abs(self.player.top)
        ball_to_opponent_distance = abs(self.opponent.y) - abs(self.ball.center_y)
        ball_radius = self.ball.height / 2
        half_paddle = self.player.width / 2
        touch_scope = self.x + half_paddle < touch.x < self.right - half_paddle
        out_of_scope_left = self.x + half_paddle > touch.x
        out_of_scope_right = touch.x > self.right - half_paddle

        if touch_player_side:
            # Restrict paddle movement to avoid tunneling
            if ball_to_player_distance > ball_radius:
                # Restrict paddle movement within screen borders
                if touch_scope:
                    self.player.center_x = touch.x
                # Clip paddle to the screen border
                elif out_of_scope_left:
                    self.player.x = self.x
                elif out_of_scope_right:
                    self.player.right = self.right
        elif touch_opponent_side:
            # Restrict paddle movement to avoid tunneling
            if ball_to_opponent_distance > ball_radius:
                # Restrict paddle movement within screen borders
                if touch_scope:
                    self.opponent.center_x = touch.x
                # Clip paddle to the screen border
                elif out_of_scope_left:
                    self.opponent.x = self.x
                elif out_of_scope_right:
                    self.opponent.right = self.right

    def on_touch_down(self, touch) -> None:
        """Detects menu touch.

        Registers the touch for the menu button and updates the game state if the menu
        is touched. Utilizes Kivy touch detection for that matter.

        Args:
            touch (kivy.input.motionevent.MotionEvent): The touch event.
        """
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
        """Represents the game menu widget.

        Attributes:
            color (ListProperty): The color of the widget.
        """

        color = ListProperty([0, 0, 0, 0])

    class PongBall(Widget):
        """Represents the pong ball.

        Attributes:
        color (ListProperty): The color of the ball.
        velocity_x (NumericProperty): The velocity of the ball in the x direction.
        velocity_y (NumericProperty): The velocity of the ball in the y direction.
        velocity (ReferenceListProperty): The combined velocity of the ball in both
        directions.
        """

        color = ListProperty([0, 0, 0, 0])
        velocity_x = NumericProperty(0)
        velocity_y = NumericProperty(0)
        velocity = ReferenceListProperty(velocity_x, velocity_y)

        def move(self) -> None:
            """Moves the ball based on its current velocity."""
            self.pos = Vector(*self.pos) + self.velocity

    class PongPaddle(Widget):
        """Represents a pong paddle.

        Inherits from Kivy's Widget class to handle positioning and rendering.

        Attributes:
            color (ListProperty): The paddle's color (default: red).
            score (NumericProperty): The player's current score.
        """

        color = ListProperty([1, 0, 0, 1])
        score = NumericProperty(0)

        def bounce_ball(self, ball) -> None:
            """Bounces the ball off the paddle.

            Calculates the collision and adjusts the ball's velocity accordingly.

            Args:
                ball (PongBall): The ball to bounce.
            """
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
                # Assuming the paddle is stationary
                relative_velocity = Vector(vx, vy)

                # Calculate the dot product of the relative velocity and the normal
                dot_product = relative_velocity.dot(normal)

                # Reflect the relative velocity across the collision normal
                reflection = relative_velocity - 2 * dot_product * normal

                # Speed increase
                # Adjust this value for the desired speed increase
                speed_multiplier = 1.2
                if abs(reflection.y) < self.height:
                    reflection *= speed_multiplier

                # Apply the reflected velocity to the ball
                ball.velocity = reflection.x, reflection.y

        def get_closest_point(self, point: Vector) -> Vector:
            """Finds the closest point on the paddle's rectangle to a given point.

            Args:
                point (Vector): The point to find the closest point to.

            Returns:
                Vector: The closest point on the paddle.
            """
            closest_x = max(self.x, min(point.x, self.right))
            closest_y = max(self.y, min(point.y, self.top))
            return Vector(closest_x, closest_y)


class PongApp(App):
    """Main application class for the Pong game.

    This class is responsible for setting up the game window and initializing the game
    logic. It inherits from Kivy's App class, which provides the main event loop and
    window management.

    Methods:
        build(): Initializes the game by creating an instance of PongGame and scheduling
        the game's update method to be called at regular intervals.
    """

    def build(self) -> PongGame:
        """Builds the Pong game application.

        Initializes the game and sets the update interval.

        Returns:
             PongGame: The game instance. Root widget object.
        """
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 120.0)
        return game


if __name__ == "__main__":
    PongApp().run()
