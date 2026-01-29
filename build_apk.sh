#!/bin/bash
# Family Household Manager - Android APK Build Script
# This script automates the build process for Google Play Store submission

echo "🚀 Family Household Manager - Android APK Build Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if we're in the right directory
    if [ ! -f "mobile_app.py" ]; then
        print_error "mobile_app.py not found. Please run this script from the project root."
        exit 1
    fi

    if [ ! -f "buildozer.spec" ]; then
        print_error "buildozer.spec not found. Please ensure buildozer is configured."
        exit 1
    fi

    if [ ! -d "assets" ]; then
        print_error "assets directory not found. Please run generate_icons.py first."
        exit 1
    fi

    if [ ! -f "keystore.jks" ]; then
        print_error "keystore.jks not found. Please generate a keystore first."
        exit 1
    fi

    print_success "Prerequisites check passed!"
}

# Clean previous builds
clean_build() {
    print_status "Cleaning previous builds..."
    rm -rf .buildozer
    rm -rf bin
    print_success "Clean complete!"
}

# Build APK
build_apk() {
    print_status "Setting up Android build environment..."
    print_warning "This may take 30-60 minutes on first run..."

    # Run the environment setup script which handles everything
    if ./build_env_setup.sh; then
        print_success "APK build completed successfully!"
    else
        print_error "APK build failed. Check the buildozer output above for errors."
        exit 1
    fi
}

# Verify build output
verify_build() {
    print_status "Verifying build output..."

    APK_PATH="bin/FamilyHouseholdManager-1.0.0-arm64-v8a-release.aab"

    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        print_success "APK generated successfully: $APK_PATH ($APK_SIZE)"
    else
        print_error "APK not found at expected location: $APK_PATH"
        print_status "Checking for alternative locations..."
        find . -name "*.aab" -o -name "*.apk" | head -5
        exit 1
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 BUILD COMPLETE!"
    echo "=================="
    echo ""
    echo "Your APK is ready for Google Play Store submission:"
    echo "📁 Location: bin/FamilyHouseholdManager-1.0.0-arm64-v8a-release.aab"
    echo ""
    echo "📋 NEXT STEPS:"
    echo "1. Create Google Play Console account (if not done):"
    echo "   https://play.google.com/console/"
    echo ""
    echo "2. Create new app in Play Console:"
    echo "   - App name: Family Household Manager"
    echo "   - Default language: English"
    echo "   - App type: App"
    echo ""
    echo "3. Upload AAB file from step 1"
    echo ""
    echo "4. Fill store listing:"
    echo "   - Use content from PLAY_STORE_LISTING.md"
    echo "   - Upload screenshots from assets/ folder"
    echo "   - Upload feature graphic (assets/feature_graphic.png)"
    echo "   - Set privacy policy URL"
    echo ""
    echo "5. Set content rating and pricing"
    echo ""
    echo "6. Submit for review!"
    echo ""
    echo "📚 RESOURCES:"
    echo "• Play Console Help: https://support.google.com/googleplay/android-developer"
    echo "• App Bundle Guide: https://developer.android.com/guide/app-bundle"
    echo "• Store Listing Best Practices: https://developer.android.com/distribute/best-practices/launch/store-listing"
}

# Main execution
main() {
    check_prerequisites
    clean_build
    build_apk
    verify_build
    show_next_steps
}

# Run main function
main