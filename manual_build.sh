#!/bin/bash
# Manual APK Build Script - Bypasses problematic SDK updates
# This script uses python-for-android directly to build the APK

echo "🔧 Manual APK Build - Bypassing SDK Update Issues"
echo "================================================"

# Set environment variables
export ANDROID_SDK_ROOT="/home/server1/.buildozer/android/platform/android-sdk"
export ANDROID_NDK_ROOT="/home/server1/.buildozer/android/platform/android-ndk-r25b"
export PATH="$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/33.0.2:$PATH"

# Change to project directory
cd "/home/server1/Desktop/meal-plan-inventory"

# Activate virtual environment
source mobile_venv/bin/activate

echo "📦 Building APK with python-for-android..."
echo "This may take 20-40 minutes..."

# Use p4a directly to create the APK
p4a apk \
    --private . \
    --package com.familyhousehold.manager \
    --name "Family Household Manager" \
    --version 1.0.0 \
    --bootstrap sdl2 \
    --requirements sqlite3,kivy \
    --arch arm64-v8a \
    --dist-name com.familyhousehold.manager \
    --sdk-dir /home/server1/.buildozer/android/platform/android-sdk \
    --ndk-dir /home/server1/.buildozer/android/platform/android-ndk-r25b \
    --release

# Check if build succeeded
if [ -f "bin/FamilyHouseholdManager-1.0.0-arm64-v8a-release.apk" ]; then
    echo "✅ SUCCESS: APK built successfully!"
    echo "📁 Location: bin/FamilyHouseholdManager-1.0.0-arm64-v8a-release.apk"
    ls -lh bin/FamilyHouseholdManager-1.0.0-arm64-v8a-release.apk
else
    echo "❌ FAILED: APK build failed"
    exit 1
fi