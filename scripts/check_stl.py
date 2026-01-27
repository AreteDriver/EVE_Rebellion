"""Quick STL dimension check."""

import sys

import bpy

# Clear scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Import STL
argv = sys.argv[sys.argv.index("--") + 1 :]
filepath = argv[0]
bpy.ops.wm.stl_import(filepath=filepath)
obj = bpy.context.selected_objects[0]

# Get dimensions
dims = obj.dimensions
print(f"\n=== {filepath} ===")
print(f"Dimensions: X={dims.x:.2f} Y={dims.y:.2f} Z={dims.z:.2f}")
print(f"Rotation: {obj.rotation_euler}")
print(f"Max dimension: {max(dims):.2f}")
