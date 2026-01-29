#!/bin/bash
# Minimal test APK build

echo "🧪 Building minimal test APK..."

cd "/home/server1/Desktop/meal-plan-inventory"

# Create a simple test app
cat > test_main.py << 'EOF'
from kivy.app import App
from kivy.uix.label import Label

class TestApp(App):
    def build(self):
        return Label(text='Hello World!')

if __name__ == '__main__':
    TestApp().run()
EOF

# Build minimal APK
source mobile_venv/bin/activate
p4a apk \
    --private . \
    --package com.test.app \
    --name "Test App" \
    --version 1.0.0 \
    --bootstrap sdl2 \
    --requirements kivy \
    --arch arm64-v8a \
    --dist-name test \
    --sdk-dir /home/server1/.buildozer/android/platform/android-sdk \
    --ndk-dir /home/server1/.buildozer/android/platform/android-ndk-r25b \
    --release \
    --debug

# Check result
if [ -f "bin/TestApp-1.0.0-arm64-v8a-release.apk" ]; then
    echo "✅ Minimal APK built successfully!"
    ls -lh bin/TestApp-1.0.0-arm64-v8a-release.apk
else
    echo "❌ Minimal APK build failed"
fi