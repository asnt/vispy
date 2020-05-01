import argparse

import numpy as np
from vispy import app, scene
from vispy.io import imread, load_data_file, read_mesh
from vispy.scene.visuals import Mesh
from vispy.visuals.filters import TextureFilter


parser = argparse.ArgumentParser()
parser.add_argument('--shading', default='smooth',
                    choices=['none', 'flat', 'smooth'],
                    help="shading mode")
args = parser.parse_args()

mesh_path = load_data_file('spot/spot.obj.gz')
texture_path = load_data_file('spot/spot.png')
vertices, faces, normals, texcoords = read_mesh(mesh_path)
texture = np.flipud(imread(texture_path))

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600))
view = canvas.central_widget.add_view()

view.camera = 'arcball'
# Adapt the depth to the scale of the mesh to avoid rendering artefacts.
view.camera.depth_value = 10 * (vertices.max() - vertices.min())

shading = None if args.shading == 'none' else args.shading
mesh = Mesh(vertices, faces, shading=shading, color='lightgreen')
mesh.shininess = 1e-3
view.add(mesh)

texture_filter = TextureFilter(texture, texcoords)
mesh.attach(texture_filter)


ctrl_down = False

@canvas.events.key_press.connect
def on_key_press(event):
    global ctrl_down
    if event.key == "t":
        texture_filter.enabled = not texture_filter.enabled
        mesh.update()
    elif event.key == "control":
        ctrl_down = True


@canvas.events.key_release.connect
def on_key_release(event):
    global ctrl_down
    if event.key == "control":
        ctrl_down = False


@canvas.events.mouse_wheel.connect
def on_mouse_wheel(event):
    print(ctrl_down)
    if ctrl_down:
        factor = texture_filter.blending_factor + 0.05 * event.delta[1]
        print(event.delta)
        texture_filter.blending_factor = max(min(factor, 1.0), 0.0)
        event.handled = True
        event.blocked = True


def attach_headlight(mesh, view, canvas):
    light_dir = (0, -1, 0, 0)
    mesh.light_dir = light_dir[:3]
    initial_light_dir = view.camera.transform.imap(light_dir)

    @view.scene.transform.changed.connect
    def on_transform_change(event):
        transform = view.camera.transform
        mesh.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(mesh, view, canvas)


canvas.show()

if __name__ == "__main__":
    app.run()
