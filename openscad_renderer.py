#!/usr/bin/env python3
"""
OpenSCAD Headless Renderer
Python wrapper for rendering OpenSCAD files to images in headless mode
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, Tuple


class OpenSCADRenderer:
    """Headless OpenSCAD renderer using Xvfb"""

    def __init__(self, display: int = 99):
        """
        Initialize the renderer

        Args:
            display: Virtual display number for Xvfb (default: 99)
        """
        self.display = display
        self.xvfb_process = None

    def start_xvfb(self) -> None:
        """Start Xvfb virtual display server"""
        env = os.environ.copy()
        env['DISPLAY'] = f':{self.display}'

        self.xvfb_process = subprocess.Popen(
            ['Xvfb', f':{self.display}', '-screen', '0', '1024x768x24'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env
        )
        # Wait for Xvfb to start
        import time
        time.sleep(2)

    def stop_xvfb(self) -> None:
        """Stop Xvfb virtual display server"""
        if self.xvfb_process:
            self.xvfb_process.terminate()
            self.xvfb_process.wait()
            self.xvfb_process = None

    def render(
        self,
        scad_file: str,
        output_file: str,
        imgsize: Tuple[int, int] = (1920, 1080),
        colorscheme: str = "Tomorrow",
        projection: str = "p",
        camera: Optional[Tuple[float, ...]] = None,
        render_mode: bool = True
    ) -> bool:
        """
        Render OpenSCAD file to image

        Args:
            scad_file: Path to .scad file
            output_file: Path to output image file
            imgsize: Image size as (width, height)
            colorscheme: Color scheme (Tomorrow, Cornfield, Metallic, Sunset, Starnight, BeforeDawn, Nature, DeepOcean)
            projection: 'p' for perspective or 'o' for orthogonal
            camera: Camera parameters (x, y, z, rotx, roty, rotz, dist) or None for auto
            render_mode: True for full render, False for preview

        Returns:
            True if rendering succeeded, False otherwise
        """
        if not Path(scad_file).exists():
            print(f"Error: {scad_file} does not exist", file=sys.stderr)
            return False

        env = os.environ.copy()
        env['DISPLAY'] = f':{self.display}'

        cmd = [
            'openscad',
            '-o', output_file,
            '--imgsize', f'{imgsize[0]},{imgsize[1]}',
            '--projection', projection,
            '--colorscheme', colorscheme,
        ]

        if render_mode:
            cmd.append('--render')
        else:
            cmd.append('--preview')

        if camera:
            cam_str = ','.join(map(str, camera))
            cmd.extend(['--camera', cam_str])
        else:
            cmd.append('--viewall')

        cmd.append(scad_file)

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and Path(output_file).exists():
                print(f"[SUCCESS] Rendered successfully: {output_file}")
                file_size = Path(output_file).stat().st_size
                print(f"  File size: {file_size / 1024:.1f} KB")
                return True
            else:
                print(f"[FAILED] Rendering failed", file=sys.stderr)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("[FAILED] Rendering timed out", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] Error during rendering: {e}", file=sys.stderr)
            return False

    def __enter__(self):
        """Context manager entry"""
        self.start_xvfb()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_xvfb()


def main():
    """Example usage"""
    if len(sys.argv) < 2:
        print("Usage: python openscad_renderer.py <scad_file> [output_file]")
        print("Example: python openscad_renderer.py test.scad output.png")
        sys.exit(1)

    scad_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.png"

    # Use context manager to automatically start/stop Xvfb
    with OpenSCADRenderer() as renderer:
        success = renderer.render(scad_file, output_file)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
