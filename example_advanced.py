#!/usr/bin/env python3
"""
Advanced OpenSCAD rendering examples
複数のビューや設定でレンダリングする例
"""

from openscad_renderer import OpenSCADRenderer
from pathlib import Path


def render_multiple_views(scad_file: str, output_dir: str = "outputs"):
    """
    同じモデルを異なるカメラアングルでレンダリング

    Args:
        scad_file: OpenSCADファイルのパス
        output_dir: 出力ディレクトリ
    """
    Path(output_dir).mkdir(exist_ok=True)

    views = {
        'front': (0, 0, 0, 0, 0, 0, 500),
        'top': (0, 0, 0, 90, 0, 0, 500),
        'side': (0, 0, 0, 0, 0, 90, 500),
        'isometric': (0, 0, 0, 55, 0, 25, 500),
    }

    with OpenSCADRenderer() as renderer:
        for view_name, camera in views.items():
            output_file = f"{output_dir}/{Path(scad_file).stem}_{view_name}.png"
            print(f"Rendering {view_name} view...")

            renderer.render(
                scad_file=scad_file,
                output_file=output_file,
                camera=camera,
                imgsize=(1920, 1080)
            )


def render_different_colorschemes(scad_file: str, output_dir: str = "outputs"):
    """
    異なるカラースキームでレンダリング

    Args:
        scad_file: OpenSCADファイルのパス
        output_dir: 出力ディレクトリ
    """
    Path(output_dir).mkdir(exist_ok=True)

    colorschemes = [
        'Tomorrow',
        'Cornfield',
        'Metallic',
        'Sunset',
        'Starnight',
        'BeforeDawn',
        'Nature',
        'DeepOcean'
    ]

    with OpenSCADRenderer() as renderer:
        for scheme in colorschemes:
            output_file = f"{output_dir}/{Path(scad_file).stem}_{scheme}.png"
            print(f"Rendering with {scheme} color scheme...")

            renderer.render(
                scad_file=scad_file,
                output_file=output_file,
                colorscheme=scheme,
                imgsize=(1280, 720)
            )


def render_animation_frames(scad_file: str, output_dir: str = "animation", num_frames: int = 36):
    """
    アニメーション用のフレームをレンダリング（360度回転）

    Args:
        scad_file: OpenSCADファイルのパス
        output_dir: 出力ディレクトリ
        num_frames: フレーム数
    """
    Path(output_dir).mkdir(exist_ok=True)

    with OpenSCADRenderer() as renderer:
        for i in range(num_frames):
            angle = (360 / num_frames) * i
            output_file = f"{output_dir}/frame_{i:03d}.png"

            print(f"Rendering frame {i+1}/{num_frames} (angle: {angle:.1f}°)...")

            # カメラを回転させる
            camera = (0, 0, 0, 55, 0, angle, 500)

            renderer.render(
                scad_file=scad_file,
                output_file=output_file,
                camera=camera,
                imgsize=(1920, 1080)
            )

    print(f"\n✓ Generated {num_frames} frames in {output_dir}/")
    print(f"Create video with: ffmpeg -framerate 24 -i {output_dir}/frame_%03d.png -c:v libx264 -pix_fmt yuv420p output.mp4")


def compare_render_modes(scad_file: str, output_dir: str = "outputs"):
    """
    プレビューモードとレンダーモードを比較

    Args:
        scad_file: OpenSCADファイルのパス
        output_dir: 出力ディレクトリ
    """
    Path(output_dir).mkdir(exist_ok=True)

    import time

    with OpenSCADRenderer() as renderer:
        # Preview mode (fast)
        print("Rendering in preview mode (fast)...")
        start = time.time()
        renderer.render(
            scad_file=scad_file,
            output_file=f"{output_dir}/{Path(scad_file).stem}_preview.png",
            render_mode=False
        )
        preview_time = time.time() - start

        # Render mode (high quality)
        print("Rendering in full render mode (slow, high quality)...")
        start = time.time()
        renderer.render(
            scad_file=scad_file,
            output_file=f"{output_dir}/{Path(scad_file).stem}_render.png",
            render_mode=True
        )
        render_time = time.time() - start

        print(f"\nPreview mode: {preview_time:.2f}s")
        print(f"Render mode:  {render_time:.2f}s")
        print(f"Speed difference: {render_time/preview_time:.1f}x")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python example_advanced.py <scad_file> [mode]")
        print("\nModes:")
        print("  views       - Render multiple camera views")
        print("  colors      - Render with different color schemes")
        print("  animation   - Generate animation frames (360° rotation)")
        print("  compare     - Compare preview vs render mode")
        print("  all         - Run all examples")
        print("\nExample: python example_advanced.py test.scad views")
        sys.exit(1)

    scad_file = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "all"

    if not Path(scad_file).exists():
        print(f"Error: {scad_file} not found")
        sys.exit(1)

    if mode in ["views", "all"]:
        print("\n=== Rendering multiple views ===")
        render_multiple_views(scad_file)

    if mode in ["colors", "all"]:
        print("\n=== Rendering different color schemes ===")
        render_different_colorschemes(scad_file)

    if mode in ["animation", "all"]:
        print("\n=== Generating animation frames ===")
        render_animation_frames(scad_file, num_frames=36)

    if mode in ["compare", "all"]:
        print("\n=== Comparing render modes ===")
        compare_render_modes(scad_file)

    print("\n✓ All rendering tasks completed!")
