#!/bin/bash
# Refactor all usages of .instance.signals, .instance.data, .instance.framework, .instance.run to use convenience properties

echo "Refactoring all files..."

# Source files
files=(
    "src/mw4/logic/modelBuild/modelRun.py"
    "src/mw4/gui/mainWindow/mainWindow.py"
    "src/mw4/gui/extWindows/image/imageW.py"
    "src/mw4/gui/mainWaddon/tabEnviron_Weather.py"
    "src/mw4/gui/extWindows/hemisphere/hemisphereDraw.py"
    "src/mw4/gui/mainWaddon/tabSat_Track.py"
    "src/mw4/gui/mainWaddon/slewInterface.py"
    "tests/unit_tests/gui/extWindows/image/test_imageW.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        # Use sed to replace patterns
        sed -i '' 's/\.instance\.signals\b/.signals/g' "$file"
        sed -i '' 's/\.instance\.data\b/.data/g' "$file"
        sed -i '' 's/\.instance\.framework\b/.framework/g' "$file"
        sed -i '' 's/\.instance\.run\b/.run/g' "$file"
        echo "✅ $file"
    else
        echo "❌ $file not found"
    fi
done

echo "✅ Refactoring complete!"

