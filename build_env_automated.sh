#!/bin/bash

################################################################################
# Family Household Manager - Automated Build Environment Setup
# This script sets up all necessary environment variables for successful APK build
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

################################################################################
# CONFIGURATION
################################################################################

ANDROID_SDK_ROOT="${HOME}/.buildozer/android/platform/android-sdk"
ANDROID_NDK_ROOT="${HOME}/.buildozer/android/platform/android-ndk-r25b"
ANDROID_HOME="${ANDROID_SDK_ROOT}"
BUILD_TOOLS_PATH="${ANDROID_SDK_ROOT}/build-tools/33.0.2"
PLATFORM_TOOLS_PATH="${ANDROID_SDK_ROOT}/platform-tools"

print_status "Setting up build environment..."
print_status "SDK Root: ${ANDROID_SDK_ROOT}"
print_status "NDK Root: ${ANDROID_NDK_ROOT}"
print_status "Build Tools: ${BUILD_TOOLS_PATH}"

################################################################################
# VERIFY COMPONENTS EXIST
################################################################################

print_status "Verifying Android SDK components..."

if [ ! -d "${ANDROID_SDK_ROOT}" ]; then
    print_error "Android SDK not found at: ${ANDROID_SDK_ROOT}"
    exit 1
fi
print_success "Android SDK found"

if [ ! -d "${ANDROID_NDK_ROOT}" ]; then
    print_error "Android NDK not found at: ${ANDROID_NDK_ROOT}"
    exit 1
fi
print_success "Android NDK found"

if [ ! -f "${BUILD_TOOLS_PATH}/aidl" ]; then
    print_error "AIDL compiler not found at: ${BUILD_TOOLS_PATH}/aidl"
    print_warning "Available build tools:"
    ls -la "${ANDROID_SDK_ROOT}/build-tools/" 2>/dev/null || echo "  None found"
    exit 1
fi
print_success "AIDL compiler found: ${BUILD_TOOLS_PATH}/aidl"

################################################################################
# EXPORT ENVIRONMENT VARIABLES
################################################################################

print_status "Exporting environment variables..."

export ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT}"
export ANDROID_HOME="${ANDROID_HOME}"
export ANDROID_NDK_ROOT="${ANDROID_NDK_ROOT}"
export ANDROID_NDK="${ANDROID_NDK_ROOT}"
export ANDROID_NDK_PATH="${ANDROID_NDK_ROOT}"

# Set PATH to include build-tools and platform-tools
export PATH="${BUILD_TOOLS_PATH}:${PLATFORM_TOOLS_PATH}:/usr/local/bin:/usr/bin:/bin:${PATH}"

print_success "ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT}"
print_success "ANDROID_NDK_ROOT=${ANDROID_NDK_ROOT}"
print_success "ANDROID_HOME=${ANDROID_HOME}"

################################################################################
# VERIFY AIDL IS ACCESSIBLE
################################################################################

print_status "Verifying AIDL accessibility..."

if ! command -v aidl &> /dev/null; then
    print_error "aidl command not found in PATH"
    exit 1
fi

AIDL_PATH=$(command -v aidl)
AIDL_VERSION=$(aidl --version 2>&1 || echo "unknown")
print_success "AIDL found at: ${AIDL_PATH}"
print_success "AIDL version: ${AIDL_VERSION}"

################################################################################
# VERIFY KEYTOOL (Java)
################################################################################

print_status "Verifying Java tools..."

if ! command -v keytool &> /dev/null; then
    print_error "keytool not found - Java Development Kit may not be installed"
    exit 1
fi
print_success "keytool found"

if ! command -v javac &> /dev/null; then
    print_error "javac not found - Java Development Kit may not be installed"
    exit 1
fi
print_success "javac found"

################################################################################
# VERIFY PYTHON ENVIRONMENT
################################################################################

print_status "Verifying Python environment..."

if [ ! -d "mobile_venv" ]; then
    print_error "mobile_venv not found. Please run: python3 -m venv mobile_venv"
    exit 1
fi
print_success "mobile_venv found"

# Activate virtual environment
source mobile_venv/bin/activate
print_success "Virtual environment activated"

# Verify buildozer is installed
if ! command -v buildozer &> /dev/null; then
    print_warning "buildozer not found in venv, installing..."
    pip install buildozer -q
    print_success "buildozer installed"
else
    print_success "buildozer found"
fi

################################################################################
# SELECT BUILD TYPE
################################################################################

print_status "Build environment ready!"
echo ""
echo "Available build options:"
echo "  1) Debug APK (faster, for testing)"
echo "  2) Release APK (signed, for Play Store)"
echo "  3) Clean and Build (removes old build artifacts)"
echo ""

read -p "Select build type (1-3): " BUILD_CHOICE

case $BUILD_CHOICE in
    1)
        print_status "Building DEBUG APK..."
        buildozer android debug
        ;;
    2)
        print_status "Building RELEASE APK..."
        buildozer android release
        ;;
    3)
        print_status "Cleaning previous builds..."
        buildozer clean
        print_status "Building RELEASE APK..."
        buildozer android release
        ;;
    *)
        print_error "Invalid selection"
        exit 1
        ;;
esac

################################################################################
# POST-BUILD VERIFICATION
################################################################################

if [ $? -eq 0 ]; then
    print_success "Build completed successfully!"
    
    # Find and display APK location
    APK_PATH=$(find ./bin -name "*.apk" -o -name "*.aab" 2>/dev/null | head -1)
    if [ -n "${APK_PATH}" ]; then
        print_success "Output: ${APK_PATH}"
        ls -lh "${APK_PATH}"
    fi
else
    print_error "Build failed. Check output above for errors."
    exit 1
fi

# Deactivate virtual environment
deactivate

print_success "Build environment cleanup complete"
