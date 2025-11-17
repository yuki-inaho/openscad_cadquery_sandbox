"""
OpenSCAD Sandbox Scripts Package

再利用可能なモジュールのパッケージ:
- renderer: OpenSCADレンダリング共通モジュール
- cadquery_utils: CadQuery共通ユーティリティ
- solidpython_utils: SolidPython共通ユーティリティ
"""

from .renderer import OpenSCADRenderer, render_multiple_views
from .cadquery_utils import (
    export_step,
    export_stl,
    export_all_formats,
    convert_to_openscad,
    create_2d_projections,
    save_model_with_openscad_support,
)
from .solidpython_utils import (
    save_scad_3d,
    create_2d_projection_scad,
    save_model_with_2d,
    create_multiple_2d_projections,
    batch_save_models,
)

__all__ = [
    # renderer
    "OpenSCADRenderer",
    "render_multiple_views",
    # cadquery_utils
    "export_step",
    "export_stl",
    "export_all_formats",
    "convert_to_openscad",
    "create_2d_projections",
    "save_model_with_openscad_support",
    # solidpython_utils
    "save_scad_3d",
    "create_2d_projection_scad",
    "save_model_with_2d",
    "create_multiple_2d_projections",
    "batch_save_models",
]
