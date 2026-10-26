"""
MYSTERYVERSE AI - HEADLESS BLENDER PYTHON 3D ENGINE
Executes in Blender headless mode (-b -P blender_render.py -- [args])
Generates 3D procedural scenes, lighting, materials, camera moves, and particle systems.
"""

import sys
import argparse
import math

def parse_args():
    # Everything after '--' is user arguments
    if "--" in sys.argv:
        args_start = sys.argv.index("--") + 1
        raw_args = sys.argv[args_start:]
    else:
        raw_args = []
        
    parser = argparse.ArgumentParser(description="Mysteryverse Blender 3D Procedural Scene Generator")
    parser.add_argument("--scene_type", default="space", choices=["space", "science", "history", "ocean", "abstract", "character_host"])
    parser.add_argument("--output", default="output.mp4")
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--duration_sec", type=float, default=5.0)
    parser.add_argument("--character_expression", default="explanation")
    return parser.parse_args(raw_args)

def main():
    try:
        import bpy
    except ImportError:
        print("[ERROR] bpy module is only available when executed inside Blender (`blender -b -P blender_render.py`).")
        sys.exit(1)

    args = parse_args()
    print(f"[*] Initializing Blender Scene: {args.scene_type} ({args.width}x{args.height} @ {args.fps}fps, {args.duration_sec}s)")

    # 1. Clear existing scene objects
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettingsEEVEENext') else 'BLENDER_EEVEE'
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.fps = args.fps
    total_frames = int(args.duration_sec * args.fps)
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Set output format to FFmpeg H.264
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.filepath = args.output

    # 2. Camera Setup with animated trajectory
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0, -7, 1.5)
    cam_obj.rotation_euler = (math.radians(78), 0, 0)

    # Animate Camera slow cinematic dolly / orbit
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.location = (0.5, -5.5, 1.8)
    cam_obj.keyframe_insert(data_path="location", frame=total_frames)

    # 3. Dynamic 3-Point Lighting Rig
    key_light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_light_data.energy = 500
    key_light_data.color = (1.0, 0.85, 0.7)  # Warm key
    key_light = bpy.data.objects.new("KeyLight", key_light_data)
    key_light.location = (3, -4, 4)
    scene.collection.objects.link(key_light)

    rim_light_data = bpy.data.lights.new(name="RimLight", type='SPOT')
    rim_light_data.energy = 800
    rim_light_data.color = (0.02, 0.7, 0.9)  # Electric cyan rim
    rim_light = bpy.data.objects.new("RimLight", rim_light_data)
    rim_light.location = (-3, 3, 3)
    rim_light.rotation_euler = (math.radians(-45), 0, math.radians(45))
    scene.collection.objects.link(rim_light)

    # 4. Generate Procedural Scene Content based on Template
    if args.scene_type == "space":
        # Create Exoplanet with atmospheric glow and ring
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.8, location=(0, 2, 0))
        planet = bpy.context.active_object
        planet.name = "Exoplanet"
        
        # Planet Material
        mat = bpy.data.materials.new(name="ExoplanetMat")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        principled.inputs["Base Color"].default_value = (0.08, 0.25, 0.65, 1.0)
        principled.inputs["Roughness"].default_value = 0.4
        planet.data.materials.append(mat)
        
        # Rotation animation
        planet.rotation_euler = (math.radians(15), 0, 0)
        planet.keyframe_insert(data_path="rotation_euler", frame=1)
        planet.rotation_euler = (math.radians(15), 0, math.radians(60))
        planet.keyframe_insert(data_path="rotation_euler", frame=total_frames)

    elif args.scene_type == "science":
        # Create Rotating Quantum Core / Holographic DNA
        bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.15, location=(0, 1, 0))
        ring1 = bpy.context.active_object
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.7, subdivisions=3, location=(0, 1, 0))
        core = bpy.context.active_object
        
        mat_core = bpy.data.materials.new(name="QuantumCoreMat")
        mat_core.use_nodes = True
        bsdf = mat_core.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Emission Color"].default_value = (0.0, 0.9, 1.0, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 8.0
        core.data.materials.append(mat_core)

    elif args.scene_type == "history":
        # Create Ancient Monolith / Obelisk with Glowing Runes
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1, 1.5))
        monolith = bpy.context.active_object
        monolith.scale = (0.8, 0.4, 3.2)
        
        mat_stone = bpy.data.materials.new(name="StoneMat")
        mat_stone.use_nodes = True
        nodes = mat_stone.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.15, 0.14, 0.13, 1.0)
        monolith.data.materials.append(mat_stone)

    else:
        # Default Abstract Concept Mystery Vortex
        bpy.ops.mesh.primitive_cone_add(radius1=2.0, depth=3.0, location=(0, 1, 0))
        vortex = bpy.context.active_object
        vortex.rotation_euler = (math.radians(90), 0, 0)

    print(f"[*] Rendering scene to: {args.output}...")
    bpy.ops.render.render(animation=True)
    print("[*] Blender 3D render completed successfully!")

if __name__ == "__main__":
    main()
