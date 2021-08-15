from engine.game_object import GameObject
from engine.standard_game_objects import ButtonTable, Button, TextInputField
from engine.rendering.renderer_factory import create_renderer_from_string
from osc import OscController
import numpy as np

oscRenderer = create_renderer_from_string('''
#version 440 core
layout(location=0) in vec3 vertex_buffer;
layout(location=1) in float color_buffer;

out vec3 fragmentColor;
uniform mat4x4 rotMat;
uniform vec3 color;
void main(){
        gl_Position = rotMat * vec4(vertex_buffer.xyz, 1);
            fragmentColor = color*color_buffer;//vec3(0.0, color_buffer, 0.0);
            }

    ''',
    '''
#version 440 core
in vec3 fragmentColor;
out vec4 vertex_color;
void main(){
    vertex_color=vec4(fragmentColor, 1);
}
    ''', 
)

class OscGameObject(GameObject):
    def __init__(self, n, m):
        super().__init__()
        self.renderer = oscRenderer()
        self.osc = OscController(n, m)
        self.add_renderer(self.renderer)
        self.set_osc(self.osc)
        self.renderer.color = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    def generate_points(self):
        n = self.osc.n
        m = self.osc.m
        points = []
        for i in range(n):
            for j in range(m):
                points.append(np.array([0.5 - i/n, 0.5 -j/m, -1.0]).astype(np.float32))
        self.renderer.vertex_buffer = np.array(points)
        self.renderer.n_points = len(self.renderer.vertex_buffer)

    def set_osc(self, osc):
        self.osc = osc
        self.generate_points()
        self.renderer.color_buffer = self.osc.states 
        
    def update(self):
        self.osc.advance_states()
        self.renderer.color_buffer = self.osc.states

class SidePanel(GameObject):
    def __init__(self, osc_controller):
        super().__init__()

        self.buttons = [
            [Button(lambda x: x, 1, 1, text="f'(x)=a-b*x", color = (0, 0, 0))],
            [Button(lambda x: x, 1, 1, text="a=", color=(0,0,0)), TextInputField("2", 1, 1, lambda x: x, color=(0.2, 0, 0.2)), Button(lambda x: x, 1, 1, text="b=", color=(0,0,0)), TextInputField("0.01", 1, 1, lambda x: x, color=(0.2, 0, 0.2))],
            [Button(lambda x: x, 1, 1, text="dt=", color=(0,0,0)), TextInputField("0.001", 1, 1, lambda x: x, color=(0.2, 0, 0.2))],
            [Button(lambda x: x, 1, 1, text="kick=", color=(0,0,0)), TextInputField("0.01", 1, 1, lambda x: x, color=(0.2, 0, 0.2))],
            [Button(lambda x: x, 1, 1, text="height=", color=(0,0,0)), TextInputField("500", 1, 1, lambda x: x, color=(0.2, 0, 0.2))],
            [Button(lambda x: x, 1, 1, text="width=", color=(0,0,0)), TextInputField("500", 1, 1, lambda x: x, color=(0.2, 0, 0.2))],
            [Button(self.update_color_button_cb, 1, 1, text="R", color=[1, 0, 0]), Button( self.update_color_button_cb, 1, 1, text="G", color = [0, 0 ,0]), Button( self.update_color_button_cb, 1, 1, text="B", color=[0, 0, 0])],
            [Button(self.submit_cb, 1, 1, text="submit", color=(0,0,0))],
        ]
        layout = [
            [1],
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.75],
            [0.25, 0.75],
            [0.25, 0.75],
            [0.25, 0.75],
            [0.3333, 0.3333, 0.3333],
            [1],
        ]
        self.button_table = ButtonTable(1, 1, self.buttons, h_weights=layout)
        self.button_table.set_parent(self)
        self.button_table.transform.translate(0, 0, -1.3)
        self.osc_controller = osc_controller

    def update_color_button_cb(self, button):
        c = max(button.color)
        c += 0.05
        if c > 1:
            c = 0
        if button.text == 'R':
            button.update_color([c, 0, 0])
        if button.text == 'G':
            button.update_color([0, c, 0])
        if button.text == 'B':
            button.update_color([0, 0, c])


    def submit_cb(self, button):
        n_int = int(self.buttons[4][1].text)
        m_int = int(self.buttons[5][1].text)
        if n_int != self.osc_controller.osc.n or m_int != self.osc_controller.osc.m:
            self.osc_controller.set_osc(OscController(n_int, m_int))
        self.osc_controller.osc.alpha = float(self.buttons[1][1].text)
        self.osc_controller.osc.beta = float(self.buttons[1][3].text)
        self.osc_controller.osc.dt = float(self.buttons[2][1].text)
        self.osc_controller.osc.kick_str = float(self.buttons[3][1].text)
        self.osc_controller.renderer.color = [max(self.buttons[6][0].color), max(self.buttons[6][1].color), max(self.buttons[6][2].color)] 
