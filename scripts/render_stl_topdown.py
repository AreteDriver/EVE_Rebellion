"""
Blender script to render STL models as top-down sprites.
Run with: blender --background --python render_stl_topdown.py -- input.stl output.png [size]
"""

import bpy
import sys
import os
import math
from pathlib import Path
from mathutils import Vector


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


def import_stl(filepath):
    """Import STL file and return the imported object."""
    bpy.ops.wm.stl_import(filepath=filepath)
    obj = bpy.context.selected_objects[0]
    return obj


def setup_object(obj, rotate_180=False):
    """Center and orient the object for top-down view.

    Args:
        obj: Blender object to setup
        rotate_180: If True, rotate 180 degrees to flip ship direction
    """
    # Select and make active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Set origin to geometry center
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Move to world origin
    obj.location = (0, 0, 0)

    # Reset rotation - STL models often need orientation adjustment
    obj.rotation_euler = (0, 0, 0)

    # Get initial dimensions
    dims = obj.dimensions
    width, depth, height = dims.x, dims.y, dims.z

    # Determine rotation based on which axis is longest
    # For top-down shooter, we want the ship pointing "up" (positive Y in 2D)

    if height > width and height > depth:
        # Ship is standing up (Z is longest), rotate to lay flat
        # Rotate 90 degrees around X to make Z become Y
        obj.rotation_euler = (math.pi/2, 0, 0)
    elif width > depth and width > height:
        # Ship is along X axis, rotate to point along Y
        obj.rotation_euler = (0, 0, math.pi/2)  # Rotate 90 around Z
    # else: depth (Y) is longest, which is what we want - no rotation needed

    # Apply the 180 degree flip if requested (for models that render nose-down)
    if rotate_180:
        obj.rotation_euler = (obj.rotation_euler[0], obj.rotation_euler[1],
                              obj.rotation_euler[2] + math.pi)

    # Apply rotation to get accurate dimensions
    bpy.context.view_layer.update()

    # Get final dimensions after rotation for camera setup
    bbox = [obj.matrix_world @ Vector(obj.bound_box[i]) for i in range(8)]
    min_x = min(v[0] for v in bbox)
    max_x = max(v[0] for v in bbox)
    min_y = min(v[1] for v in bbox)
    max_y = max(v[1] for v in bbox)

    final_width = max_x - min_x
    final_depth = max_y - min_y

    # Return the larger of width/depth for orthographic scale
    return max(final_width, final_depth)


def create_material():
    """Create a material with EVE-like metallic look."""
    mat = bpy.data.materials.new(name="ShipMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')

    # EVE-like settings - darker metallic with Gallente olive/grey tint
    principled.inputs['Base Color'].default_value = (0.08, 0.10, 0.06, 1.0)  # Darker green-grey
    principled.inputs['Metallic'].default_value = 0.9
    principled.inputs['Roughness'].default_value = 0.3
    principled.inputs['Specular IOR Level'].default_value = 0.8

    # Connect
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    output.location = (300, 0)
    principled.location = (0, 0)

    return mat


def setup_camera(obj_size, render_size):
    """Create orthographic camera looking down."""
    # Create camera
    cam_data = bpy.data.cameras.new(name='TopDownCam')
    cam_obj = bpy.data.objects.new('TopDownCam', cam_data)
    bpy.context.collection.objects.link(cam_obj)

    # Position above looking down
    cam_obj.location = (0, 0, obj_size * 2)
    cam_obj.rotation_euler = (0, 0, 0)  # Looking down -Z

    # Orthographic for clean 2D look
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = obj_size * 1.2  # Padding

    # Set as active camera
    bpy.context.scene.camera = cam_obj

    return cam_obj


def setup_lighting(obj_size):
    """Create dramatic EVE-style lighting."""
    # Key light - from above-front (strong main light)
    key = bpy.data.lights.new(name='KeyLight', type='SUN')
    key.energy = 8.0  # Stronger
    key.color = (1.0, 0.95, 0.9)
    key_obj = bpy.data.objects.new('KeyLight', key)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (obj_size, -obj_size, obj_size * 2)
    key_obj.rotation_euler = (math.radians(45), math.radians(30), 0)

    # Rim light - from behind for edge definition
    rim = bpy.data.lights.new(name='RimLight', type='SUN')
    rim.energy = 5.0  # Stronger
    rim.color = (0.7, 0.8, 1.0)  # Slight blue
    rim_obj = bpy.data.objects.new('RimLight', rim)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (-obj_size, obj_size, obj_size)
    rim_obj.rotation_euler = (math.radians(135), math.radians(-30), 0)

    # Fill light - softer ambient
    fill = bpy.data.lights.new(name='FillLight', type='SUN')
    fill.energy = 3.0  # Stronger
    fill.color = (0.9, 0.9, 1.0)
    fill_obj = bpy.data.objects.new('FillLight', fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-obj_size, -obj_size, obj_size * 1.5)


def setup_render(output_path, size=256):
    """Configure render settings."""
    scene = bpy.context.scene

    # Render engine
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64  # Good quality, reasonable speed

    # Output settings
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100

    # Transparent background
    scene.render.film_transparent = True

    # Output format
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = output_path

    # World - dark background (for non-transparent preview)
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (0.01, 0.01, 0.02, 1.0)


def render_stl(input_path, output_path, size=256, rotate_180=False):
    """Main function to render an STL as a top-down sprite.

    Args:
        input_path: Path to STL file
        output_path: Path for output PNG
        size: Render resolution (square)
        rotate_180: If True, rotate ship 180 degrees (for nose-down models)
    """
    print(f"Rendering {input_path} -> {output_path} at {size}px (flip={rotate_180})")

    # Clear existing scene
    clear_scene()

    # Import STL
    obj = import_stl(input_path)

    # Setup object orientation
    obj_size = setup_object(obj, rotate_180=rotate_180)

    # Apply material
    mat = create_material()
    obj.data.materials.append(mat)

    # Setup scene
    setup_camera(obj_size, size)
    setup_lighting(obj_size)
    setup_render(output_path, size)

    # Render
    bpy.ops.render.render(write_still=True)

    print(f"Rendered: {output_path}")


def main():
    """Parse arguments and render."""
    # Get arguments after '--'
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        print("Usage: blender --background --python render_stl_topdown.py -- input.stl output.png [size] [--flip]")
        sys.exit(1)

    if len(argv) < 2:
        print("Usage: blender --background --python render_stl_topdown.py -- input.stl output.png [size] [--flip]")
        sys.exit(1)

    input_path = argv[0]
    output_path = argv[1]

    # Parse optional size and flip flag
    size = 256
    rotate_180 = False

    for arg in argv[2:]:
        if arg == '--flip':
            rotate_180 = True
        elif arg.isdigit():
            size = int(arg)

    render_stl(input_path, output_path, size, rotate_180)


if __name__ == "__main__":
    main()
