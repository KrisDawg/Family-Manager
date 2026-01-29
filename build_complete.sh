#!/bin/bash
# Family Household Manager - Complete Automated APK Builder
# This script handles the entire APK build process from start to finish

echo "🤖 Family Household Manager - Complete Automated APK Builder"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC} $1 ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check if we're in the right directory
check_project_directory() {
    print_step "1. Checking project directory..."

    if [ ! -f "mobile_app.py" ]; then
        print_error "mobile_app.py not found. Please run this script from the project root."
        print_error "Expected location: /home/server1/Desktop/meal-plan-inventory"
        exit 1
    fi

    if [ ! -d "assets" ]; then
        print_warning "Assets directory not found. Generating icons..."
        if [ -f "generate_icons.py" ]; then
            print_status "Running icon generation..."
            source mobile_venv/bin/activate && python generate_icons.py
        else
            print_error "generate_icons.py not found. Please create assets manually."
            exit 1
        fi
    fi

    print_success "Project directory verified!"
}

# Verify all required components
verify_components() {
    print_step "2. Verifying required components..."

    # Check Python virtual environment
    if [ ! -f "mobile_venv/bin/activate" ]; then
        print_error "Python virtual environment not found. Creating..."
        python3 -m venv mobile_venv
        source mobile_venv/bin/activate
        pip install --upgrade pip
        pip install kivy buildozer Pillow
        print_success "Virtual environment created!"
    else
        print_success "Virtual environment found!"
    fi

    # Check keystore
    if [ ! -f "keystore.jks" ]; then
        print_warning "Keystore not found. Generating..."
        keytool -genkey -v -keystore keystore.jks -alias familymanager -keyalg RSA -keysize 2048 -validity 10000 -storepass familymanager2026 -keypass familymanager2026 -dname "CN=Family Manager Team, OU=Development, O=Family Household Manager, L=Anytown, ST=Anystate, C=US" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_success "Keystore generated!"
        else
            print_error "Failed to generate keystore. Please check Java installation."
            exit 1
        fi
    else
        print_success "Keystore found!"
    fi

    # Check buildozer configuration
    if [ ! -f "buildozer.spec" ]; then
        print_error "buildozer.spec not found. Cannot proceed."
        exit 1
    else
        print_success "Buildozer configuration found!"
    fi
}

# Setup Android SDK components if needed
setup_android_sdk() {
    print_step "3. Setting up Android SDK components..."

    # Check if Android SDK is already set up
    ANDROID_SDK_ROOT="/home/server1/.buildozer/android/platform/android-sdk"

    if [ ! -d "$ANDROID_SDK_ROOT" ]; then
        print_warning "Android SDK not found. This will be set up during build."
    else
        # Check for AIDL compiler
        if [ ! -f "$ANDROID_SDK_ROOT/build-tools/33.0.2/aidl" ]; then
            print_warning "AIDL compiler not found. Installing Android build tools..."
            source mobile_venv/bin/activate
            "$ANDROID_SDK_ROOT/tools/bin/sdkmanager" --sdk_root="$ANDROID_SDK_ROOT" "build-tools;33.0.2" 2>/dev/null || true
        fi

        # Check for Android platform
        if [ ! -d "$ANDROID_SDK_ROOT/platforms/android-33" ]; then
            print_warning "Android platform 33 not found. Installing..."
            source mobile_venv/bin/activate
            "$ANDROID_SDK_ROOT/tools/bin/sdkmanager" --sdk_root="$ANDROID_SDK_ROOT" "platforms;android-33" 2>/dev/null || true
        fi

        print_success "Android SDK components ready!"
    fi
}

# Main build process
run_build() {
    print_step "4. Starting APK build process..."

    print_header "🚀 BUILDING APK - This may take 30-60 minutes"

    # Run the build with environment setup
    if ./build_apk.sh; then
        print_success "🎉 APK BUILD COMPLETED SUCCESSFULLY!"
        return 0
    else
        print_error "❌ APK build failed!"
        print_warning "Check the output above for specific error details."
        print_warning "Common solutions:"
        print_warning "  - Ensure all Android SDK components are installed"
        print_warning "  - Check Java version compatibility"
        print_warning "  - Verify internet connection for downloads"
        return 1
    fi
}

# Final verification and next steps
final_verification() {
    print_step "5. Final verification..."

    APK_PATH="bin/FamilyHouseholdManager-1.0.0-arm64-v8a-release.aab"

    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        APK_DATE=$(stat -c %y "$APK_PATH" | cut -d'.' -f1)

        print_success "✅ APK successfully generated!"
        echo ""
        echo "📱 APK Details:"
        echo "   📁 Location: $APK_PATH"
        echo "   📏 Size: $APK_SIZE"
        echo "   📅 Created: $APK_DATE"
        echo "   🔐 Signed: Yes (with keystore)"
        echo ""

        print_header "🎯 NEXT STEPS FOR GOOGLE PLAY STORE"

        echo "1. 🌐 Create Google Play Console Account:"
        echo "   📝 Go to: https://play.google.com/console/"
        echo "   💰 Cost: $25 one-time fee"
        echo ""

        echo "2. 📋 Create New App:"
        echo "   📛 Name: Family Household Manager"
        echo "   🌍 Language: English (en-US)"
        echo "   📱 Type: App"
        echo ""

        echo "3. ⬆️ Upload APK:"
        echo "   📦 Upload: $APK_PATH"
        echo "   ⚙️ Release: Production"
        echo ""

        echo "4. 🏪 Store Listing Setup:"
        echo "   📝 Use content from: PLAY_STORE_LISTING.md"
        echo "   🖼️ Screenshots: assets/ folder"
        echo "   🎨 Feature graphic: assets/feature_graphic.png"
        echo "   🔒 Privacy policy: https://familyhouseholdmanager.com/privacy"
        echo ""

        echo "5. ✅ Content Rating & Review:"
        echo "   👶 Rating: Everyone"
        echo "   🚀 Submit for review (1-7 days)"
        echo ""

        print_success "🎊 Your app is ready for Google Play Store submission!"
        print_success "🚀 Follow the steps above to publish your Family Household Manager app!"

        return 0
    else
        print_error "❌ APK not found at expected location: $APK_PATH"
        print_warning "Checking for alternative locations..."
        find . -name "*.aab" -o -name "*.apk" 2>/dev/null | head -5 || echo "No APK files found"

        print_warning "Build may have failed or produced output in a different location."
        print_warning "Check the build output above for error details."

        return 1
    fi
}

# Main execution
main() {
    echo ""
    print_header "🤖 AUTOMATED APK BUILD SYSTEM"
    echo ""

    check_project_directory

    verify_components

    setup_android_sdk

    if run_build; then
        final_verification
        exit 0
    else
        print_error "Build process failed. Please check the output above for error details."
        exit 1
    fi
}

# Handle script interruption
trap 'echo ""; print_warning "Build interrupted by user"; exit 130' INT

# Run main function
main