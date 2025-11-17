# OpenSCAD Headless Renderer with SolidPython & CadQuery

This repository contains tools for running OpenSCAD in headless mode, rendering images locally, and generating 3D models using SolidPython and CadQuery.

## Installed Packages

The following packages are installed:

- `openscad` (2021.01): 3D modeling software
- `xvfb`: Virtual framebuffer (required for headless execution)
- `xauth`: X authentication utility
- `mesa-utils`: OpenGL utilities
- `libgl1-mesa-dri`: Mesa DRI driver
- `solidpython2`: Python library for OpenSCAD
- `cadquery`: Python-based parametric CAD library using OCCT

## File Structure

```
.
├── README.md                   # This file
├── test.scad                   # Test OpenSCAD file
├── render_headless.sh          # Bash rendering script
├── openscad_renderer.py        # Python rendering wrapper
├── example_advanced.py         # Advanced usage examples
├── solidpython_simple.py       # Simple SolidPython examples
├── solidpython_example.py      # Advanced SolidPython examples
└── cadquery_examples.py        # CadQuery examples with STEP/STL export
```

## Usage

### 1. Bash Script Execution

```bash
./render_headless.sh <input.scad> <output.png>
```

Example:
```bash
./render_headless.sh test.scad my_render.png
```

### 2. Python Script Execution

#### From command line:

```bash
python3 openscad_renderer.py <input.scad> <output.png>
```

Example:
```bash
python3 openscad_renderer.py test.scad my_render.png
```

#### Use in Python code:

```python
from openscad_renderer import OpenSCADRenderer

# Using context manager (recommended)
with OpenSCADRenderer() as renderer:
    renderer.render('test.scad', 'output.png')

# With detailed options
with OpenSCADRenderer(display=99) as renderer:
    renderer.render(
        scad_file='test.scad',
        output_file='output.png',
        imgsize=(1920, 1080),  # Image size
        colorscheme='Tomorrow',  # Color scheme
        projection='p',  # 'p'=perspective, 'o'=orthogonal
        render_mode=True  # True=full render, False=preview
    )
```

### 3. Advanced Examples

```bash
# Render multiple views
python3 example_advanced.py test.scad views

# Render with different color schemes
python3 example_advanced.py test.scad colors

# Generate animation frames
python3 example_advanced.py test.scad animation

# Compare preview and render modes
python3 example_advanced.py test.scad compare

# Run all examples
python3 example_advanced.py test.scad all
```

## SolidPython - Generate 3D Models with Python

SolidPython2 allows you to create 3D models using Python code.

### Installation

```bash
pip install solidpython2
```

### Basic Usage

```python
from solid2 import *

# Create a simple box
box = cube([10, 10, 10])

# Save to file
box.save_as_scad("box.scad")
```

### Sample Scripts

This repository includes two SolidPython samples:

1. `solidpython_simple.py` - Simple examples using standard OpenSCAD functions only
2. `solidpython_example.py` - Examples using BOSL2 extensions

Execution example:

```bash
# Generate 3D models and 2D drawings
python3 solidpython_simple.py

# Render generated SCAD files
python3 openscad_renderer.py mech_part_3d.scad mech_part_3d.png  # 3D image
python3 openscad_renderer.py mech_part_2d.scad mech_part_2d.png  # 2D drawing
```

### Generating 2D Drawings

Use OpenSCAD's `projection()` function to generate 2D drawings from 3D models:

```python
# Create 3D model with SolidPython
model_3d = cube([50, 40, 30]) - translate([5, 5, 5])(cube([40, 30, 25]))

# Generate OpenSCAD code
scad_code = scad_render(model_3d)

# Create 2D projection version
projection_code = f"""
module model_3d() {{
{scad_code}
}}

projection(cut=false) model_3d();
"""

# Save to file and render
with open("model_2d.scad", "w") as f:
    f.write(projection_code)
```

## Sample Models Generated with SolidPython

The repository includes several generated models:

1. **Mechanical Part** (`mech_part_*.scad`) - Base plate with mounting holes, boss, and ribs
2. **Simple Box** (`simple_box_*.scad`) - Hollow box
3. **Gear Shape** (`gear_shape_*.scad`) - Gear-like shape with teeth

Each model has both 3D (`*_3d.scad`) and 2D projection (`*_2d.scad`) versions.

## CadQuery - Professional CAD Modeling with Python

CadQuery is a Python library for building parametric 3D CAD models using the powerful OCCT (Open Cascade Technology) kernel.

### Installation

```bash
pip install cadquery
```

### Why CadQuery?

- **Powerful CAD Kernel**: Uses OCCT, the same kernel used by professional CAD software like FreeCAD
- **Multiple Export Formats**: STEP, STL, DXF, SVG, AMF, 3MF, and more
- **Precise Modeling**: Better for mechanical parts and engineering applications compared to OpenSCAD
- **Parametric Design**: Create designs that can be easily modified by changing parameters

### Basic Usage

```python
import cadquery as cq

# Create a simple bracket
result = (
    cq.Workplane("XY")
    .box(80, 60, 10)
    .faces(">Z")
    .workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .circle(3)
    .cutThruAll()
)

# Export to various formats
cq.exporters.export(result, "bracket.step")  # STEP format (CAD software)
cq.exporters.export(result, "bracket.stl")   # STL format (3D printing)
```

### Sample Script

This repository includes `cadquery_examples.py` with 5 different models:

1. **Simple Box** - Hollow box with shell operation
2. **Mechanical Bracket** - Bracket with mounting holes, boss, and fillets
3. **Parametric Flange** - Flange with bolt circle pattern
4. **Gear** - Simple gear with teeth
5. **Lego Brick** - Lego-compatible brick with studs

Execution example:

```bash
# Generate all models in multiple formats
python3 cadquery_examples.py

# This creates:
# - STEP files (for CAD software like FreeCAD, Fusion 360)
# - STL files (for 3D printing)
# - OpenSCAD files (for visualization)
```

### Export Formats

**STEP Format (.step):**
- Industry-standard CAD format
- Preserves exact geometry (lossless)
- Can be edited in professional CAD software
- Best for design exchange

**STL Format (.stl):**
- Standard format for 3D printing
- Mesh-based representation
- Supported by all slicing software

**DXF/SVG Formats (.dxf, .svg):**
- 2D technical drawings
- For laser cutting or documentation
- Requires 2D projection of 3D model

### Using CadQuery Models with OpenSCAD

CadQuery models can be rendered using our OpenSCAD renderer:

```bash
# CadQuery generates an OpenSCAD file that imports the STL
python3 cadquery_examples.py

# Render the model
python3 openscad_renderer.py cadquery_outputs/cq_bracket_for_openscad.scad output.png
```

### Sample Models in cadquery_outputs/

After running `cadquery_examples.py`, you'll find:

- `cq_simple_box.step`, `cq_simple_box.stl` - Hollow box
- `cq_bracket.step`, `cq_bracket.stl` - Mechanical bracket
- `cq_flange.step`, `cq_flange.stl` - Parametric flange
- `cq_gear.step`, `cq_gear.stl` - Gear with teeth
- `cq_lego_brick.step`, `cq_lego_brick.stl` - Lego-compatible brick

## OpenSCAD Command Line Options

When using OpenSCAD directly:

```bash
# Start Xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &

# Render with OpenSCAD
openscad -o output.png \
         --render \
         --imgsize=1920,1080 \
         --projection=p \
         --colorscheme=Tomorrow \
         --viewall \
         input.scad

# Stop Xvfb
killall Xvfb
```

### Main Options

- `-o <file>`: Output file (.png, .stl, .off, .amf, .3mf, etc.)
- `--render`: Full rendering (using CGAL)
- `--preview`: Preview mode (faster but lower quality)
- `--imgsize=<width>,<height>`: Image size
- `--projection=<p|o>`: Projection method (p=perspective, o=orthogonal)
- `--colorscheme=<name>`: Color scheme
- `--viewall`: Auto-adjust camera to fit entire object
- `--camera=<x,y,z,rotx,roty,rotz,dist>`: Specify camera position

## Available Color Schemes

- `Tomorrow` (default)
- `Cornfield`
- `Metallic`
- `Sunset`
- `Starnight`
- `BeforeDawn`
- `Nature`
- `DeepOcean`

## References

- [OpenSCAD Official Site](https://openscad.org/)
- [OpenSCAD Cheatsheet](https://openscad.org/cheatsheet/)
- [OpenSCAD User Manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual)
- [SolidPython2 GitHub](https://github.com/jeff-dh/SolidPython)
- [CadQuery Documentation](https://cadquery.readthedocs.io/)
- [CadQuery GitHub](https://github.com/CadQuery/cadquery)
