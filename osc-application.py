from engine import start_main_loop, Window
from engine.standard_components import ObjectMover
from osc_game_objects import *

g = OscGameObject(500, 500)
g.add_component(ObjectMover())
w = Window(game_objects=[g])
w.set_size(1000, 1000)
w2 = Window(game_objects=[SidePanel(g)])
w2.set_size(400, 1000)
w2.set_position(1000 + 60, 0)
start_main_loop()
