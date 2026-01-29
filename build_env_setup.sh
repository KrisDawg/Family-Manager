#!/bin/bash
# Family Household Manager - Android Build Environment Setup
# This script sets up the proper Android development environment before building

echo "🔧 Setting up Android build environment..."

# Set Android environment variables
export ANDROID_SDK_ROOT="/home/server1/.buildozer/android/platform/android-sdk"
export ANDROID_NDK_ROOT="/home/server1/.buildozer/android/platform/android-ndk-r25b"
export ANDROID_SDK_HOME="/home/server1/.buildozer/android/platform/android-sdk"
export ANDROID_NDK_HOME="/home/server1/.buildozer/android/platform/android-ndk-r25b"
export ANDROID_API_LEVEL="33"
export ANDROID_MIN_API_LEVEL="21"

# Add Android tools to PATH
export PATH="$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/33.0.2:$PATH"

# Verify critical tools are accessible
echo "🔍 Verifying Android tools..."

if [ ! -x "$ANDROID_SDK_ROOT/build-tools/33.0.2/aidl" ]; then
    echo "❌ ERROR: AIDL compiler not found or not executable"
    echo "   Expected: $ANDROID_SDK_ROOT/build-tools/33.0.2/aidl"
    exit 1
else
    echo "✅ AIDL compiler found: $ANDROID_SDK_ROOT/build-tools/33.0.2/aidl"
fi

if [ ! -x "$ANDROID_SDK_ROOT/platform-tools/adb" ]; then
    echo "⚠️  WARNING: ADB not found (not critical for build)"
else
    echo "✅ ADB found: $ANDROID_SDK_ROOT/platform-tools/adb"
fi

# Verify Java is available
if ! command -v java &> /dev/null; then
    echo "❌ ERROR: Java not found in PATH"
    exit 1
else
    echo "✅ Java found: $(java -version 2>&1 | head -n 1)"
fi

# Verify Python virtual environment
if [ ! -f "mobile_venv/bin/activate" ]; then
    echo "❌ ERROR: Python virtual environment not found"
    exit 1
else
    echo "✅ Python virtual environment found"
fi

echo "🎯 Android build environment ready!"
echo ""

# Now run the actual build with proper environment
echo ""
echo "🚀 Starting APK build process..."
source mobile_venv/bin/activate

# Export environment variables for buildozer subprocesses
export PYTHONPATH="$PYTHONPATH:$(pwd)/mobile_venv/lib/python3.12/site-packages"

# Make sure AIDL is in PATH for buildozer and subprocesses
export PATH="/home/server1/.buildozer/android/platform/android-sdk/build-tools/33.0.2:/usr/local/bin:$PATH"
# Also set it in the environment that buildozer uses
export BUILDOZER_ANDROID_SDK="/home/server1/.buildozer/android/platform/android-sdk"
export BUILDOZER_ANDROID_NDK="/home/server1/.buildozer/android/platform/android-ndk-r25b"

# Run buildozer
exec buildozer android release