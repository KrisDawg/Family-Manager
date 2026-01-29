#!/bin/bash
# Create AIDL symlink in common locations where buildozer might look

AIDL_SOURCE="/home/server1/.buildozer/android/platform/android-sdk/build-tools/33.0.2/aidl"
TARGET_DIRS=(
    "/usr/local/bin"
    "/usr/bin"
    "/home/server1/.buildozer/android/platform/android-sdk/tools"
    "/home/server1/.buildozer/android/platform/android-sdk/tools/bin"
)

echo "🔗 Creating AIDL symlinks in common locations..."

for dir in "${TARGET_DIRS[@]}"; do
    if [ -w "$dir" ] && [ -f "$AIDL_SOURCE" ]; then
        echo "Creating symlink in: $dir"
        ln -sf "$AIDL_SOURCE" "$dir/aidl" 2>/dev/null || true
    fi
done

# Also add to PATH
export PATH="$PATH:/home/server1/.buildozer/android/platform/android-sdk/build-tools/33.0.2"

echo "✅ AIDL symlinks created"
echo "📍 AIDL available at: $AIDL_SOURCE"

# Test if aidl is now accessible
if command -v aidl &> /dev/null; then
    echo "✅ AIDL found in PATH: $(which aidl)"
else
    echo "❌ AIDL still not in PATH"
fi

# Now run the build
echo "🚀 Starting APK build..."
exec ./build_apk.sh