import os
import subprocess
import logging
from pathlib import Path
from typing import Optional
from app.config import get_blender_path, WORKSPACE_DIR, VIDEOS_DIR
from app.animation.procedural_engine import ProceduralSceneEngine

logger = logging.getLogger("mysteryverse.animation")

class AnimationPipeline:
    def __init__(self):
        self.blender_exe = get_blender_path()
        self.blender_script = WORKSPACE_DIR / "scripts" / "blender_render.py"

    def is_blender_available(self) -> bool:
        return self.blender_exe is not None and os.path.exists(self.blender_exe)

    def render_scene(
        self,
        output_path: str,
        scene_type: str = "space",
        duration_sec: float = 5.0,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        expression: str = "explanation"
    ) -> str:
        """
        Renders a scene either via headless Blender if present, or using the high-performance
        built-in procedural graphics engine.
        """
        if self.is_blender_available() and self.blender_script.exists():
            try:
                logger.info("Executing headless Blender render: %s", scene_type)
                cmd = [
                    self.blender_exe,
                    "-b",
                    "-P", str(self.blender_script),
                    "--",
                    "--scene_type", scene_type,
                    "--output", output_path,
                    "--width", str(width),
                    "--height", str(height),
                    "--fps", str(fps),
                    "--duration_sec", str(duration_sec),
                    "--character_expression", expression
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if res.returncode == 0 and os.path.exists(output_path):
                    return output_path
                else:
                    logger.warning("Blender render returned non-zero, falling back to procedural engine: %s", res.stderr)
            except Exception as e:
                logger.error("Blender execution failed, falling back: %s", e)

        # Standalone procedural animation engine
        logger.info("Using Procedural Animation Engine: %s (%dx%d, %s)", scene_type, width, height, expression)
        engine = ProceduralSceneEngine(width=width, height=height, fps=fps)
        return engine.generate_scene_clip(
            output_mp4=output_path,
            duration_sec=duration_sec,
            theme=scene_type,
            expression=expression
        )
