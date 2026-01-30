# Release Process Guide

## Automated Release System

Your project now has **fully automated releases**! When you create a version tag, GitHub Actions will automatically build a signed release APK and create a GitHub Release.

## Quick Start - Creating a New Release

### Method 1: Using the Release Script (Recommended)

```bash
# Create and push a new release
./release.sh 1.0.0

# Or with 'v' prefix (will be normalized)
./release.sh v1.0.1
```

The script will:
1. ✅ Update version in `buildozer.spec`
2. ✅ Update version code (date-based)
3. ✅ Commit the changes
4. ✅ Create a git tag
5. ✅ Push to GitHub
6. ✅ Automatically trigger the release build

### Method 2: Manual Release

```bash
# Update version in buildozer.spec manually
nano buildozer.spec
# Change: version = 1.0.0
# Change: version.code = 20260129

# Commit changes
git add buildozer.spec
git commit -m "chore: Bump version to 1.0.0"

# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main
git push origin v1.0.0
```

## What Happens After You Push a Tag?

1. **GitHub Actions Triggers** (automatically)
   - Builds the release APK
   - Signs the APK (if keystore configured)
   - Runs in ~15-20 minutes

2. **GitHub Release Created** (automatically)
   - APK file attached for download
   - Release notes template generated
   - Published at: https://github.com/KrisDawg/Family-Manager/releases

3. **Users Can Download**
   - Direct APK download from release page
   - No need to navigate through Actions artifacts

## Monitoring the Build

```bash
# Check build status
# Visit: https://github.com/KrisDawg/Family-Manager/actions

# The release workflow will show:
# - Build progress
# - APK signing status
# - Release creation status
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features (1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (1.0.0 → 1.0.1)

Examples:
```bash
./release.sh 1.0.0   # First stable release
./release.sh 1.1.0   # Added new features
./release.sh 1.1.1   # Fixed bugs in 1.1.0
./release.sh 2.0.0   # Major rewrite/breaking changes
```

## Signing Your APK (For Play Store)

### Generate a Keystore (One-Time Setup)

```bash
# Generate release keystore
keytool -genkey -v -keystore release.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias family-manager-release

# Enter secure passwords when prompted
# Store passwords safely (you'll need them for every release)
```

### Configure GitHub Secrets

1. Go to: https://github.com/KrisDawg/Family-Manager/settings/secrets/actions
2. Add these secrets:
   - `KEYSTORE_FILE`: Base64-encoded keystore file
   - `KEYSTORE_PASSWORD`: Your keystore password
   - `KEY_ALIAS`: Your key alias (e.g., "family-manager-release")
   - `KEY_PASSWORD`: Your key password

```bash
# Encode keystore to base64 for GitHub Secret
base64 release.keystore | tr -d '\n' > keystore.b64
# Copy contents of keystore.b64 to KEYSTORE_FILE secret
```

### Update buildozer.spec

The keystore is already configured in buildozer.spec:
```ini
android.keystore = %(source.dir)s/keystore.jks
android.keystore.password = your_secure_password
android.alias = familymanager
android.alias.password = your_secure_password
```

⚠️ **Security Note**: Don't commit your actual keystore or passwords to git!

## Release Checklist

Before creating a release:

- [ ] All tests passing
- [ ] Code quality checks passed
- [ ] Version number decided
- [ ] CHANGELOG.md updated (recommended)
- [ ] No hardcoded API keys or secrets
- [ ] Assets (icons, images) up to date
- [ ] Tested on actual Android device
- [ ] Release notes prepared

## Editing Release Notes

After the release is created:

1. Go to: https://github.com/KrisDawg/Family-Manager/releases
2. Find your release (e.g., "v1.0.0")
3. Click "Edit" button
4. Update the release notes with:
   - New features
   - Bug fixes
   - Breaking changes
   - Known issues
   - Screenshots (optional)

Example release notes:
```markdown
## 🎉 Family Manager v1.0.0

### ✨ New Features
- Enhanced meal planning with AI suggestions
- Improved inventory tracking
- New bill reminder system

### 🐛 Bug Fixes
- Fixed crash on app startup
- Resolved database sync issues

### 📱 Installation
1. Download the APK below
2. Enable "Install from Unknown Sources"
3. Install and enjoy!

### 📋 Requirements
- Android 5.0 (API 21) or higher
- 50MB free space
```

## Manual Build (Without GitHub Actions)

If you need to build locally:

```bash
# Activate virtual environment
source mobile_venv/bin/activate

# Clean previous builds
buildozer android clean

# Build release APK
buildozer android release

# APK will be in: bin/familyhouseholdmanager-1.0.0-arm64-v8a-release.apk
```

## Troubleshooting

### Build Fails on GitHub Actions
- Check Actions tab for error logs
- Verify all secrets are set correctly
- Ensure buildozer.spec is properly configured

### Release Not Created
- Verify tag was pushed: `git push origin v1.0.0`
- Check that tag follows `v*` pattern (v1.0.0, v2.1.3, etc.)
- Review workflow logs in Actions tab

### APK Not Signed
- Verify keystore secrets are configured in GitHub
- Check keystore path in buildozer.spec
- Review release workflow logs

## Play Store Submission

Once you have a signed release APK:

1. **Create Google Play Console Account**
   - https://play.google.com/console/signup
   - One-time $25 registration fee

2. **Prepare Store Listing**
   - App screenshots (see `assets/screenshots/`)
   - Feature graphic (1024x500)
   - App description (see `PLAY_STORE_LISTING.md`)
   - Privacy policy (see `PRIVACY_POLICY.md`)

3. **Upload APK/AAB**
   - Use the signed release APK
   - Or use AAB format for smaller download size

4. **Submit for Review**
   - Typically takes 1-3 days
   - May require adjustments based on feedback

## Automated Release on Every Commit (Optional)

To build APK on **every push** (not recommended for production):

Edit `.github/workflows/release.yml`:
```yaml
on:
  push:
    branches: [ main ]  # Build on every push to main
  tags:
    - 'v*'
```

## Future Enhancements

- [ ] Set up Fastlane for automated Play Store uploads
- [ ] Add beta testing workflow
- [ ] Implement automated testing before release
- [ ] Set up crash reporting (Firebase Crashlytics)
- [ ] Add automated changelog generation

---

**Need Help?** Open an issue on GitHub or check the Actions logs for detailed error messages.
