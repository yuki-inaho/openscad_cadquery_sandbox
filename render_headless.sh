#!/bin/bash
# OpenSCAD headless rendering script

# Set display for Xvfb
export DISPLAY=:99

# Start Xvfb in the background
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

# Input and output file paths
SCAD_FILE="${1:-test.scad}"
OUTPUT_PNG="${2:-output.png}"

echo "Rendering $SCAD_FILE to $OUTPUT_PNG using headless OpenSCAD..."

# Render the OpenSCAD file to PNG
# --render: Use full geometry evaluation
# --imgsize: Set image size (width,height)
# --view: Set camera view (axes,scales)
# --projection: o for orthogonal, p for perspective
# --colorscheme: Color scheme to use
openscad -o "$OUTPUT_PNG" \
         --render \
         --imgsize=1920,1080 \
         --projection=p \
         --colorscheme=Tomorrow \
         --viewall \
         "$SCAD_FILE"

RENDER_EXIT_CODE=$?

# Kill Xvfb
kill $XVFB_PID

if [ $RENDER_EXIT_CODE -eq 0 ]; then
    echo "✓ Rendering completed successfully!"
    echo "Output saved to: $OUTPUT_PNG"

    if [ -f "$OUTPUT_PNG" ]; then
        FILE_SIZE=$(du -h "$OUTPUT_PNG" | cut -f1)
        echo "File size: $FILE_SIZE"
    fi
else
    echo "✗ Rendering failed with exit code $RENDER_EXIT_CODE"
    exit $RENDER_EXIT_CODE
fi
