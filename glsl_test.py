from kivy.app import App
from kivy.clock import Clock
from kivy.properties import DictProperty
from kivy.uix.effectwidget import AdvancedEffectBase, EffectWidget
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.lang import Builder

Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 1000)

Builder.load_string("""
<PongBall>:
    size: 500, 500

<PongGame>:    
    ball: pong_ball
    PongBall:
        id: pong_ball
        center: self.parent.center
""")


class PongBall(Widget):
    velocity_x = NumericProperty(14.0)
    velocity_y = NumericProperty(12.0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_size,1/60)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        app = App.get_running_app()
        app.shader.x = self.pos[0]
        app.shader.y = self.pos[1]

    def on_size(self, *args):
        self.set_size()

    def set_size(self, *args):
        app = App.get_running_app()
        app.shader.width = self.width
        app.shader.height = self.height


class PongGame(Widget):
    ball = ObjectProperty(None)

    def update(self, dt):
        self.ball.move()
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1
        if (self.ball.x < 0) or (self.ball.right > self.width):
            self.ball.velocity_x *= -1

    def on_size(self, *args):
        app = App.get_running_app()
        app.ew.size = self.size
        app.shader.screen_width = self.width
        app.shader.screen_height = self.height


class Shader(AdvancedEffectBase):
    uniforms = DictProperty({'x': 0.0, 'y': 0.0, 'width': 10.0, 'height': 10.0, 'screen_width': 500.0, 'screen_height': 500.0})
    x = NumericProperty(0.0)
    y = NumericProperty(0.0)
    width = NumericProperty(10.0)
    height = NumericProperty(10.0)
    screen_width = NumericProperty(500.0)
    screen_height = NumericProperty(500.0)

    def on_x(self, _, x):
        self.uniforms['x'] = x + self.width/2

    def on_y(self, _, y):
        self.uniforms['y'] = y + self.height/2

    def on_screen_width(self, _, screen_width):
        print(screen_width)
        self.uniforms['screen_width'] = float(screen_width)

    def on_screen_height(self, _, screen_height):
        self.uniforms['screen_height'] = float(screen_height)
        print(self.uniforms)

    def on_width(self, _, width):
        self.uniforms['width'] = float(width)

    def on_height(self, _, height):
        self.uniforms['height'] = float(height)


    glsl = '''
uniform float x;
uniform float y;
uniform float width;
uniform float height;
uniform float screen_width;
uniform float screen_height;

vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords) {
    float half_screen =  screen_height * 0.5;
    float radius = width / 2.0;

    vec2 ball_pos = vec2(x, y);
    vec2 pixel_pos = tex_coords * vec2(screen_width, screen_height);

    float distance = length(ball_pos - pixel_pos);

    if (distance < radius && pixel_pos.y <= half_screen) {
        return vec4(1.0, 1.0, 1.0, 1.0);
    }
    if (distance < radius && pixel_pos.y > half_screen) {
        return vec4(0.0, 0.0, 0.0, 1.0);
    }  
    if (pixel_pos.y > half_screen) {
        return vec4(1.0, 1.0, 1.0, 1.0);
    } 
    if (pixel_pos.y <= half_screen) {
        return vec4(0.0, 0.0, 0.0, 1.0);
    }    
}
'''


class PongApp(App):
    def build(self):
        self.shader = Shader()
        self.ew = EffectWidget(effects=[self.shader])
        game = PongGame()
        game.add_widget(self.ew)
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
