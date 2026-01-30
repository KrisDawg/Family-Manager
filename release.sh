#!/bin/bash
# release.sh - Create a new release version
# Usage: ./release.sh <version>
# Example: ./release.sh 1.0.0

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "❌ Error: Version number required"
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 1.0.0"
    exit 1
fi

# Remove 'v' prefix if present
VERSION=${VERSION#v}

echo "🚀 Creating release version $VERSION..."
echo ""

# Update version in buildozer.spec
echo "📝 Updating buildozer.spec..."
sed -i "s/^version = .*/version = $VERSION/" buildozer.spec
sed -i "s/^version.code = .*/version.code = $(date +%Y%m%d)/" buildozer.spec

# Commit version changes
echo "💾 Committing version update..."
git add buildozer.spec
git commit -m "chore: Bump version to $VERSION" || echo "No changes to commit"

# Create and push tag
echo "🏷️  Creating and pushing tag v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION

## What's New in v$VERSION

### Features
- [Add features here]

### Bug Fixes
- [Add fixes here]

### Improvements
- [Add improvements here]
"

git push origin main
git push origin "v$VERSION"

echo ""
echo "✅ Release v$VERSION created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. GitHub Actions will automatically build the APK"
echo "2. Monitor build at: https://github.com/KrisDawg/Family-Manager/actions"
echo "3. Release will be created at: https://github.com/KrisDawg/Family-Manager/releases"
echo "4. Edit release notes on GitHub to describe changes"
echo ""
echo "⏱️  Build typically takes 15-20 minutes"
