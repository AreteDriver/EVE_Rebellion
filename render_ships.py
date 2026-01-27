#!/usr/bin/env python3
"""
EVE Ship Top-Down Renderer for Blender

Renders STL ship models as top-down sprites for use in the game.
Run with: blender --background --python render_ships.py

Uses orthographic camera from above to create 2D sprites.
"""

import math
import os

import bpy

# Configuration
OUTPUT_DIR = "/home/arete/EVE_Rebellion/assets/ship_sprites"
STL_BASE = "/tmp/eve-stls/ships"

# Ships to render for the game
SHIPS_TO_RENDER = {
    # Minmatar (Player ships) - rusty brown/red colors
    "rifter": {
        "stl": f"{STL_BASE}/minmatar/frigate/rifter.stl",
        "color": (0.6, 0.25, 0.1, 1.0),  # Rusty brown
        "size": 64,
        "faction": "minmatar",
    },
    "slasher": {
        "stl": f"{STL_BASE}/minmatar/frigate/slasher.stl",
        "color": (0.5, 0.2, 0.1, 1.0),  # Dark rust
        "size": 64,
        "faction": "minmatar",
    },
    "hurricane": {
        "stl": f"{STL_BASE}/minmatar/battlecruiser/hurricane.stl",
        "color": (0.55, 0.22, 0.12, 1.0),  # Rust
        "size": 96,
        "faction": "minmatar",
    },
    # Amarr (Enemy ships) - gold/bronze colors
    "executioner": {
        "stl": f"{STL_BASE}/amarr/frigate/executioner.stl",
        "color": (0.8, 0.6, 0.2, 1.0),  # Gold
        "size": 48,
        "faction": "amarr",
    },
    "punisher": {
        "stl": f"{STL_BASE}/amarr/frigate/punisher.stl",
        "color": (0.75, 0.55, 0.25, 1.0),  # Bronze
        "size": 48,
        "faction": "amarr",
    },
    "tormentor": {
        "stl": f"{STL_BASE}/amarr/frigate/tormentor.stl",
        "color": (0.7, 0.5, 0.2, 1.0),  # Gold-bronze
        "size": 48,
        "faction": "amarr",
    },
    "crucifier": {
        "stl": f"{STL_BASE}/amarr/frigate/crucifier.stl",
        "color": (0.85, 0.65, 0.3, 1.0),  # Light gold
        "size": 48,
        "faction": "amarr",
    },
    "coercer": {
        "stl": f"{STL_BASE}/amarr/destroyer/coercer.stl",
        "color": (0.78, 0.58, 0.22, 1.0),  # Gold
        "size": 56,
        "faction": "amarr",
    },
    "omen": {
        "stl": f"{STL_BASE}/amarr/cruiser/omen.stl",
        "color": (0.8, 0.6, 0.25, 1.0),  # Gold
        "size": 72,
        "faction": "amarr",
    },
    "maller": {
        "stl": f"{STL_BASE}/amarr/cruiser/maller.stl",
        "color": (0.72, 0.52, 0.2, 1.0),  # Bronze
        "size": 72,
        "faction": "amarr",
    },
    "harbinger": {
        "stl": f"{STL_BASE}/amarr/battlecruiser/harbringer.stl",
        "color": (0.82, 0.62, 0.28, 1.0),  # Gold
        "size": 88,
        "faction": "amarr",
    },
    "prophecy": {
        "stl": f"{STL_BASE}/amarr/battlecruiser/prophecy.stl",
        "color": (0.76, 0.56, 0.24, 1.0),  # Bronze-gold
        "size": 88,
        "faction": "amarr",
    },
    "apocalypse": {
        "stl": f"{STL_BASE}/amarr/battleship/apocalypse.stl",
        "color": (0.85, 0.65, 0.3, 1.0),  # Bright gold
        "size": 112,
        "faction": "amarr",
    },
    "abaddon": {
        "stl": f"{STL_BASE}/amarr/battleship/abaddon.stl",
        "color": (0.8, 0.55, 0.2, 1.0),  # Deep gold
        "size": 128,
        "faction": "amarr",
    },
    "archon": {
        "stl": f"{STL_BASE}/amarr/capital/archon.stl",
        "color": (0.88, 0.68, 0.32, 1.0),  # Bright gold
        "size": 160,
        "faction": "amarr",
    },
    "avatar": {
        "stl": f"{STL_BASE}/amarr/capital/avatar.stl",
        "color": (0.9, 0.7, 0.35, 1.0),  # Brilliant gold
        "size": 256,
        "faction": "amarr",
    },
}


def clear_scene():
    """Remove all objects from scene"""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


def setup_render_settings(resolution):
    """Configure render settings for sprites"""
    scene = bpy.context.scene

    # Render engine - use Eevee for speed
    scene.render.engine = (
        "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "BLENDER_EEVEE_NEXT") else "BLENDER_EEVEE"
    )

    # Resolution
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100

    # Transparent background
    scene.render.film_transparent = True

    # Output format
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"


def create_camera():
    """Create orthographic camera looking straight down"""
    bpy.ops.object.camera_add(location=(0, 0, 10))
    camera = bpy.context.active_object
    camera.name = "TopDownCamera"

    # Set to orthographic
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 5.0  # Will be adjusted per model

    # Point straight down
    camera.rotation_euler = (0, 0, 0)

    bpy.context.scene.camera = camera
    return camera


def create_lighting():
    """Create lighting setup for top-down view"""
    # Key light from front-top
    bpy.ops.object.light_add(type="SUN", location=(2, -2, 8))
    key_light = bpy.context.active_object
    key_light.name = "KeyLight"
    key_light.data.energy = 3.0
    key_light.rotation_euler = (math.radians(30), math.radians(20), 0)

    # Fill light from side
    bpy.ops.object.light_add(type="SUN", location=(-3, 0, 6))
    fill_light = bpy.context.active_object
    fill_light.name = "FillLight"
    fill_light.data.energy = 1.5
    fill_light.rotation_euler = (math.radians(45), math.radians(-30), 0)

    # Rim light for definition
    bpy.ops.object.light_add(type="SUN", location=(0, 3, 4))
    rim_light = bpy.context.active_object
    rim_light.name = "RimLight"
    rim_light.data.energy = 2.0
    rim_light.rotation_euler = (math.radians(60), 0, 0)


def import_stl(filepath):
    """Import STL file and return the object"""
    bpy.ops.wm.stl_import(filepath=filepath)
    obj = bpy.context.active_object
    return obj


def create_material(name, color, metallic=0.8, roughness=0.3):
    """Create a material with the given color"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    # Get the principled BSDF node
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        # Add slight emission for visibility
        bsdf.inputs["Emission Color"].default_value = (
            color[0] * 0.1,
            color[1] * 0.1,
            color[2] * 0.1,
            1.0,
        )
        bsdf.inputs["Emission Strength"].default_value = 0.2

    return mat


def center_and_scale_object(obj, camera):
    """Center object and scale to fit view"""
    # Apply transforms
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    # Move to origin
    obj.location = (0, 0, 0)

    # Get bounding box dimensions
    bbox = obj.bound_box
    min_x = min(v[0] for v in bbox)
    max_x = max(v[0] for v in bbox)
    min_y = min(v[1] for v in bbox)
    max_y = max(v[1] for v in bbox)

    width = (max_x - min_x) * obj.scale.x
    height = (max_y - min_y) * obj.scale.y
    max_dim = max(width, height)

    # Adjust camera ortho scale
    camera.data.ortho_scale = max_dim * 1.3  # Add padding


def render_ship(ship_name, config):
    """Render a single ship to sprite"""
    stl_path = config["stl"]
    color = config["color"]
    size = config["size"]
    config["faction"]

    if not os.path.exists(stl_path):
        print(f"  [SKIP] {ship_name}: STL not found at {stl_path}")
        return False

    print(f"  [RENDER] {ship_name} ({size}x{size})...")

    # Clear and setup scene
    clear_scene()
    setup_render_settings(size)
    camera = create_camera()
    create_lighting()

    # Import model
    obj = import_stl(stl_path)
    if obj is None:
        print(f"  [ERROR] Failed to import {ship_name}")
        return False

    # Rotate for top-down view (ships typically face +Y in STL)
    # Rotate so front points up in the sprite
    obj.rotation_euler = (0, 0, math.radians(180))  # Rotate to face up

    # Apply material
    mat = create_material(f"{ship_name}_mat", color)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Center and scale
    center_and_scale_object(obj, camera)

    # Render
    output_path = os.path.join(OUTPUT_DIR, f"{ship_name}.png")
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

    print(f"  [OK] {ship_name} saved to {output_path}")
    return True


def main():
    """Main render function"""
    print("=" * 60)
    print("EVE Ship Top-Down Renderer")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    success_count = 0
    total = len(SHIPS_TO_RENDER)

    for ship_name, config in SHIPS_TO_RENDER.items():
        if render_ship(ship_name, config):
            success_count += 1

    print("=" * 60)
    print(f"Rendered {success_count}/{total} ships")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
