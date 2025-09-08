#!/bin/bash
# Homebrew Setup Script for ROS2 Installer
# This script helps you set up your tool for Homebrew distribution

set -e

echo "🍺 Setting up ROS2 Installer for Homebrew..."

# Function to print colored output
print_step() {
    echo -e "\n🔧 $1"
}

print_success() {
    echo -e "✅ $1"
}

print_warning() {
    echo -e "⚠️  $1"
}

print_error() {
    echo -e "❌ $1"
}

# Check if we're in the right directory
if [[ ! -f "ros2_installer_cli.py" ]]; then
    print_error "Please run this script from the ros_installer directory"
    exit 1
fi

print_step "Creating Homebrew tap structure..."

# Create the Homebrew tap directory structure
mkdir -p homebrew-ros-installer/Formula

# Copy the formula
cp Formula/ros2-installer.rb homebrew-ros-installer/Formula/

print_success "Homebrew tap structure created in 'homebrew-ros-installer/'"

print_step "Creating GitHub repository setup..."

# Create .gitignore for the tap
cat > homebrew-ros-installer/.gitignore << 'EOF'
# macOS
.DS_Store

# IDE
.vscode/
.idea/

# Logs
*.log

# Temporary files
*.tmp
EOF

# Create README for the tap
cat > homebrew-ros-installer/README.md << 'EOF'
# Homebrew Tap for ROS2 Installer

This tap provides the ROS2 Installer CLI tool via Homebrew.

## Installation

```bash
# Add this tap
brew tap your-username/ros-installer

# Install the tool
brew install ros2-installer
```

## Usage

```bash
# Show help
ros2-installer --help

# Install ROS2
sudo ros2-installer
```

## Formula

The formula installs:
- The main CLI script as `ros2-installer`
- Default configuration file
- All Python dependencies

## Support

For issues with the installer itself, please visit the main repository.
EOF

print_success "Tap repository structure created"

print_step "Creating release preparation script..."

# Create a script to help with releases
cat > prepare-release.sh << 'EOF'
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
EOF

chmod +x prepare-release.sh

print_success "Release preparation script created"

print_step "Creating local testing instructions..."

cat > test-formula.md << 'EOF'
# Testing Your Homebrew Formula Locally

## 1. Test the Formula

```bash
# Install from local formula
brew install --build-from-source ./Formula/ros2-installer.rb

# Test the installation
ros2-installer --help
ros2-installer --version
```

## 2. Uninstall for Testing

```bash
# Uninstall to test fresh installations
brew uninstall ros2-installer
```

## 3. Test from Tap

```bash
# After setting up your tap repository
brew tap your-username/ros-installer
brew install ros2-installer
```

## 4. Debug Issues

```bash
# Install with verbose output
brew install --verbose ros2-installer

# Check formula syntax
brew audit --strict ros2-installer
```
EOF

print_success "Testing instructions created"

print_step "Summary of created files:"
echo "   📁 homebrew-ros-installer/        - Homebrew tap repository"
echo "   📁 homebrew-ros-installer/Formula/ - Formula directory"
echo "   📄 homebrew-ros-installer/README.md - Tap documentation"
echo "   📄 prepare-release.sh             - Release preparation script"
echo "   📄 test-formula.md               - Testing instructions"
echo "   📄 requirements.txt              - Python dependencies"

print_step "Next steps:"
echo "1. Update Formula/ros2-installer.rb with your actual GitHub repository URL"
echo "2. Create a GitHub repository for the tap (homebrew-ros-installer)"
echo "3. Create a release of your main repository"
echo "4. Run ./prepare-release.sh to create a release package"
echo "5. Update the formula with the actual SHA256"
echo "6. Test locally using instructions in test-formula.md"
echo "7. Push to your Homebrew tap repository"

print_success "Homebrew setup complete! 🎉"
EOF
