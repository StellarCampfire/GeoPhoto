#!/bin/bash

# Update the repository
git pull

# Run the build
python build_project.py --os linux --ui

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

# Get the home directory path
HOME_DIR=$(eval echo ~${USER})

# Define the path to the Geo directory
GEO_DIR="${HOME_DIR}/Geo"

# Check if the Geo directory exists, if not - create it
if [ ! -d "$GEO_DIR" ]; then
    mkdir -p "$GEO_DIR"
fi

# Remove the old GeoPhoto.exe file if it exists, then move the new file
if [ -f "${GEO_DIR}/GeoPhoto.exe" ]; then
    rm "${GEO_DIR}/GeoPhoto.exe"
fi

mv dist/GeoPhoto.exe "$GEO_DIR/"

# Check if the file move was successful
if [ $? -ne 0 ]; then
    echo "Failed to move GeoPhoto.exe to $GEO_DIR"
    exit 1
fi

# Define the path to the Desktop
DESKTOP_DIR="${HOME_DIR}/Desktop"

# Create the .desktop file content
DESKTOP_ENTRY="[Desktop Entry]
Name=GeoPhoto
Exec=${GEO_DIR}/GeoPhoto.exe
Type=Application
Terminal=false
Icon=${GEO_DIR}/GeoPhoto.ico"

# Remove the old desktop shortcut if it exists
if [ -f "${DESKTOP_DIR}/GeoPhoto.desktop" ]; then
    rm "${DESKTOP_DIR}/GeoPhoto.desktop"
fi

# Create the new desktop shortcut
echo "$DESKTOP_ENTRY" > "${DESKTOP_DIR}/GeoPhoto.desktop"

# Make the desktop shortcut executable
chmod +x "${DESKTOP_DIR}/GeoPhoto.desktop"

echo "Build, move, and shortcut creation completed successfully!"
