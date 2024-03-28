#!/bin/bash


UI_PATH="./resources/ui"
PY_PATH="./resources/py"


mkdir -p "$PY_PATH"

for ui_file in "$UI_PATH"/*.ui; do
    echo "Building $(basename "$ui_file")..."
    pyuic5 -x "$ui_file" -o "$PY_PATH/$(basename "${ui_file%.ui}.py")"
done

echo "UI build process completed!"