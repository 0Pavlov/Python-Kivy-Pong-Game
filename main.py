from kivy.app import App
from kivy.uix.widget import Widget
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
<PongGame>:
    ball: pong_ball
    player: player
    opponent: opponent

    canvas:
        Color:
            rgba: 1, 1, 1, 1    
        Rectangle:
            id: background
            size: self.width, self.height / 2
            pos: 0, self.height / 2

    Label:
        id: opponent_score
        font_size: 70
        color: 0, 0, 0, 1
        center_x: root.width / 2
        center_y: root.top - 100
        text: str(root.player.score)

    Label:
        id: player_score
        font_size: 70
        center_x: root.width / 2
        center_y: root.y + 100
        text: str(root.opponent.score)

    PongBall:
        id: pong_ball
        center: self.parent.center

    PongPaddle:
        id: opponent
        center_x: root.width / 2
        y: root.y + 300
        color: 1, 1, 1, 1

    PongPaddle:
        id: player
        center_x: root.width / 2
        y: root.top - self.height - 300
        color: 0, 0, 0, 1

<PongBall>:
    size: root.size
    canvas:
        Color:
            rgba: root.color
        Ellipse:
            pos: self.pos
            size: self.size

<PongPaddle>:
    id: pong_paddle
    score: root.score
    size: 200, 50
    on_score: self.size[0] -= 50
    canvas:
        Color:
            rgba: root.color
        Rectangle:
            pos: self.pos
            size: self.size
    """
)


class PongGame(Widget):
    player = ObjectProperty(None)
    opponent = ObjectProperty(None)
    ball = ObjectProperty(None)

    def change_color(self):
        if self.ball.center_y > self.center_y:
            self.ball.color = [0, 0, 0, 1]
        elif self.ball.center_y < self.center_y:
            self.ball.color = [1, 1, 1, 1]

    def serve_ball(self, vel=(0, 4)):
        self.ball.center = self.center
        self.ball.vel = vel

    def update(self, dt):
        self.change_color()
        self.ball.move()

        # Bounce off paddles
        self.player.bounce_ball(self.ball)
        self.opponent.bounce_ball(self.ball)

        # Bounce x
        if self.ball.x < 0 or self.ball.right > self.width:
            self.ball.vel_x *= -1
        # Bounce y
        if self.ball.top > self.height:
            self.opponent.score += 1
            self.serve_ball(vel=(0, 4))
        if self.ball.y < self.y:
            self.player.score += 1
            self.serve_ball(vel=(0, -4))

    def on_touch_move(self, touch):
        if touch.y < self.height / 2:
            self.opponent.center_x = touch.x
        if touch.y > self.height - self.height / 2:
            self.player.center_x = touch.x


class PongBall(Widget):
    size = ListProperty([70, 70])
    color = ListProperty([0.5, 0.5, 0.5, 1])

    # Ball velocity
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)

    def move(self):
        self.pos = Vector(*self.vel) + self.pos


class PongPaddle(Widget):
    color = ListProperty([1, 1, 1, 1])
    score = NumericProperty(0)

    def bounce_ball(self, ball):

        # Ball radius
        radius = ball.size[0]

        # Ball velocity
        vx, vy = ball.vel[0], ball.vel[1]

        # Ball direction based on its vertical velocity
        ball_down = vy < 0
        ball_up = vy > 0

        # Ball bottom, top, left, right points coordinates
        bottom_x, bottom_y = ball.center_x, ball.center_y - radius
        top_x, top_y = ball.center_x, ball.center_y + radius
        left_x, left_y = ball.center_x - radius, ball.center_y
        right_x, right_y = ball.center_x + radius, ball.center_y

        if self.collide_widget(ball):
            # Bounce of top and bottom paddles
            if (
                self.collide_point(bottom_x, bottom_y)
                and ball_down
                or self.collide_point(top_x, top_y)
                and ball_up
            ):
                # Adjust the horizontal bounce based on contact point
                offset = (ball.center_y - self.center_y) / (self.height / 2)

                # Reverse vertical velocity
                bounced = Vector(vx, vy * -1)

                # Speed up on each bounce
                vel = bounced * 1.1

                # Apply changes
                ball.vel = vel[0] + offset, vel[1]

            # Bounce of paddle sides
            elif (
                self.collide_point(left_x, left_y)
                or self.collide_point(right_x, right_y)
            ):
                ball.vel = Vector(ball.vel[0] * -1, ball.vel[1])


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 120.0)
        return game


if __name__ == "__main__":
    PongApp().run()
