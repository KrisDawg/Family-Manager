#!/bin/bash
# Monitor APK build progress

echo "=== APK Build Monitor ==="
echo "Time: $(date)"
echo ""

# Check if build is running
BUILD_PROCESSES=$(ps aux | grep -E "(buildozer|p4a|python.*toolchain|make|gcc)" | grep -v grep | wc -l)
echo "Active build processes: $BUILD_PROCESSES"

if [ $BUILD_PROCESSES -gt 0 ]; then
    echo "✅ Build is running"
else
    echo "❌ No build processes found"
fi

echo ""

# Check for APK files
APK_COUNT=$(ls -la bin/ | grep "\.apk$" | wc -l)
echo "APK files found: $APK_COUNT"

if [ $APK_COUNT -gt 0 ]; then
    echo "📱 Generated APK files:"
    ls -la bin/*.apk 2>/dev/null
fi

echo ""

# Check disk usage
echo "Build directory size:"
du -sh .buildozer/ 2>/dev/null || echo "Build directory not found"

echo ""
echo "=== End Monitor ==="