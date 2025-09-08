#!/bin/bash
# Release Preparation Script

VERSION=${1:-$(grep "__version__" ros2_installer_cli.py | cut -d'"' -f2)}

if [[ -z "$VERSION" ]]; then
    echo "❌ Could not determine version. Please specify: ./prepare-release.sh 2.1.0"
    exit 1
fi

echo "📦 Preparing release v$VERSION..."

# Create release directory
mkdir -p "release-v$VERSION"

# Copy essential files
cp ros2_installer_cli.py "release-v$VERSION/"
cp config_cli.yaml "release-v$VERSION/"
cp requirements.txt "release-v$VERSION/"
cp README.md "release-v$VERSION/"

# Create tarball
tar -czf "release-v$VERSION.tar.gz" -C "release-v$VERSION" .

# Calculate SHA256
SHA256=$(shasum -a 256 "release-v$VERSION.tar.gz" | cut -d' ' -f1)

echo "✅ Release prepared:"
echo "   📁 Directory: release-v$VERSION/"
echo "   📦 Tarball: release-v$VERSION.tar.gz"
echo "   🔐 SHA256: $SHA256"
echo ""
echo "Next steps:"
echo "1. Upload release-v$VERSION.tar.gz to GitHub releases"
echo "2. Update Formula/ros2-installer.rb with:"
echo "   - url: your-release-url"
echo "   - sha256: $SHA256"
echo "3. Test the formula locally"
echo "4. Push to your Homebrew tap repository"
