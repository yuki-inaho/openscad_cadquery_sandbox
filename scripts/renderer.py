#!/usr/bin/env python3
"""
OpenSCADレンダリング共通モジュール

headlessモードでOpenSCADを実行し、画像を生成するための再利用可能なモジュール。
"""

import subprocess
import signal
import time
import os
from pathlib import Path


class OpenSCADRenderer:
    """
    OpenSCADをheadlessモードで実行するためのレンダラークラス

    Usage:
        with OpenSCADRenderer(display=99) as renderer:
            renderer.render("model.scad", "output.png")
    """

    def __init__(self, display: int = 99):
        """
        Args:
            display: Xvfbディスプレイ番号（デフォルト: 99）
        """
        self.display = display
        self.xvfb_process = None

    def __enter__(self):
        """コンテキストマネージャー: Xvfbを起動"""
        self.start_xvfb()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: Xvfbを停止"""
        self.stop_xvfb()

    def start_xvfb(self):
        """Xvfb（仮想フレームバッファ）を起動"""
        print(f"Starting Xvfb on display :{self.display}...")
        self.xvfb_process = subprocess.Popen(
            [
                "Xvfb",
                f":{self.display}",
                "-screen", "0", "1920x1080x24",
                "-ac",
                "+extension", "GLX",
                "+render",
                "-noreset"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        print(f"[SUCCESS] Xvfb started on display :{self.display}")

    def stop_xvfb(self):
        """Xvfbを停止"""
        if self.xvfb_process:
            print("Stopping Xvfb...")
            self.xvfb_process.terminate()
            try:
                self.xvfb_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.xvfb_process.kill()
            print("[SUCCESS] Xvfb stopped")

    def render(
        self,
        scad_file: str,
        output_file: str,
        imgsize: tuple = (1920, 1080),
        colorscheme: str = "Tomorrow",
        projection: str = "p",
        render_mode: bool = True,
        camera: tuple = None,
        autocenter: bool = True,
        viewall: bool = True
    ):
        """
        OpenSCADファイルをレンダリングして画像を生成

        Args:
            scad_file: 入力SCADファイルパス
            output_file: 出力画像ファイルパス
            imgsize: 画像サイズ (width, height)
            colorscheme: カラースキーム（Tomorrow, Cornfield, Metallic等）
            projection: 投影タイプ（"p"=透視投影, "o"=平行投影）
            render_mode: True=完全レンダリング, False=プレビューモード
            camera: カメラ位置 (x,y,z,rx,ry,rz,d) または None
            autocenter: 自動センタリング
            viewall: 全体表示

        Returns:
            bool: 成功時True、失敗時False
        """
        # 環境変数を設定
        env = os.environ.copy()
        env["DISPLAY"] = f":{self.display}"

        # OpenSCADコマンドを構築
        cmd = [
            "openscad",
            "-o", output_file,
            "--imgsize", f"{imgsize[0]},{imgsize[1]}",
            "--colorscheme", colorscheme,
            f"--projection={projection}",
        ]

        if render_mode:
            cmd.append("--render")

        if camera:
            cam_str = ",".join(map(str, camera))
            cmd.extend(["--camera", cam_str])

        if autocenter:
            cmd.append("--autocenter")

        if viewall:
            cmd.append("--viewall")

        cmd.append(scad_file)

        # レンダリング実行
        print(f"Rendering {scad_file}...")
        print(f"  Mode: {'Render' if render_mode else 'Preview'}")
        print(f"  Projection: {'Perspective' if projection == 'p' else 'Orthogonal'}")
        print(f"  Color scheme: {colorscheme}")

        start_time = time.time()

        result = subprocess.run(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        elapsed_time = time.time() - start_time

        if result.returncode == 0:
            file_size = Path(output_file).stat().st_size / 1024
            print(f"[SUCCESS] Rendered successfully: {output_file}")
            print(f"  File size: {file_size:.1f} KB")
            print(f"  Time: {elapsed_time:.2f}s")
            return True
        else:
            print(f"[FAILED] Rendering failed")
            print(f"  Error: {result.stderr.decode()}")
            return False


def render_multiple_views(
    scad_file: str,
    output_prefix: str,
    views: dict = None,
    display: int = 99
):
    """
    複数のビューを一度にレンダリング

    Args:
        scad_file: 入力SCADファイル
        output_prefix: 出力ファイル名のプレフィックス
        views: ビュー設定の辞書 {"view_name": {"camera": (...), ...}}
        display: Xvfbディスプレイ番号

    Returns:
        dict: {"view_name": "output_file_path", ...}
    """
    if views is None:
        # デフォルトビュー
        views = {
            "front": {"camera": (0, -150, 50, 60, 0, 0, 250)},
            "top": {"camera": (0, 0, 200, 0, 0, 0, 250)},
            "side": {"camera": (150, 0, 50, 60, 0, 90, 250)},
            "iso": {"camera": (100, -100, 100, 55, 0, 45, 300)},
        }

    results = {}

    with OpenSCADRenderer(display=display) as renderer:
        for view_name, settings in views.items():
            output_file = f"{output_prefix}_{view_name}.png"
            success = renderer.render(scad_file, output_file, **settings)
            if success:
                results[view_name] = output_file

    return results


def main():
    """コマンドライン実行時のエントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenSCAD headless renderer"
    )
    parser.add_argument("scad_file", help="Input SCAD file")
    parser.add_argument("output_file", help="Output PNG file")
    parser.add_argument(
        "--imgsize",
        nargs=2,
        type=int,
        default=[1920, 1080],
        metavar=("WIDTH", "HEIGHT"),
        help="Image size (default: 1920 1080)"
    )
    parser.add_argument(
        "--colorscheme",
        default="Tomorrow",
        help="Color scheme (default: Tomorrow)"
    )
    parser.add_argument(
        "--projection",
        choices=["p", "o"],
        default="p",
        help="Projection: p=perspective, o=orthogonal (default: p)"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview mode (faster, lower quality)"
    )
    parser.add_argument(
        "--display",
        type=int,
        default=99,
        help="Xvfb display number (default: 99)"
    )

    args = parser.parse_args()

    with OpenSCADRenderer(display=args.display) as renderer:
        success = renderer.render(
            scad_file=args.scad_file,
            output_file=args.output_file,
            imgsize=tuple(args.imgsize),
            colorscheme=args.colorscheme,
            projection=args.projection,
            render_mode=not args.preview
        )

        return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
