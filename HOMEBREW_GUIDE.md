# 🍺 Homebrew Integration Guide

This guide will help you distribute your ROS2 Installer via Homebrew, making it easy for users to install with a simple `brew install` command.

## Overview

Your ROS2 Installer is now ready for Homebrew distribution with:
- ✅ Complete Homebrew formula (`Formula/ros2-installer.rb`)
- ✅ Tap repository structure (`homebrew-ros-installer/`)
- ✅ Python dependencies handling
- ✅ Automated setup scripts
- ✅ Testing instructions

## 🚀 Quick Setup Steps

### 1. Prepare Your Release

```bash
# Create a release package
./prepare-release.sh 2.1.0

# This creates:
# - release-v2.1.0/ directory
# - release-v2.1.0.tar.gz archive  
# - SHA256 checksum
```

### 2. Create GitHub Repositories

You'll need TWO repositories:

#### Main Repository (your-username/ros_installer)
```bash
# Upload your main code
git add .
git commit -m "Add Homebrew support"
git tag v2.1.0
git push origin main --tags
```

#### Homebrew Tap Repository (your-username/homebrew-ros-installer)
```bash
# Create the tap repository
cd homebrew-ros-installer
git init
git add .
git commit -m "Initial Homebrew tap for ROS2 Installer"
git remote add origin https://github.com/your-username/homebrew-ros-installer.git
git push -u origin main
```

### 3. Create a GitHub Release

1. Go to your main repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag: `v2.1.0`
4. Upload the `release-v2.1.0.tar.gz` file
5. Copy the download URL

### 4. Update the Formula

Edit `Formula/ros2-installer.rb`:

```ruby
url "https://github.com/your-username/ros_installer/releases/download/v2.1.0/release-v2.1.0.tar.gz"
sha256 "ACTUAL_SHA256_FROM_PREPARE_SCRIPT"
```

### 5. Test Locally

```bash
# Test the formula
brew install --build-from-source ./Formula/ros2-installer.rb

# Verify installation
ros2-installer --help
ros2-installer --version

# Clean up
brew uninstall ros2-installer
```

### 6. Publish Your Tap

```bash
cd homebrew-ros-installer
git add Formula/ros2-installer.rb
git commit -m "Update formula with release v2.1.0"
git push
```

## 📦 User Installation

Once published, users can install with:

```bash
# Add your tap
brew tap your-username/ros-installer

# Install the tool
brew install ros2-installer

# Use it
sudo ros2-installer --help
```

## 🔧 Formula Features

Your Homebrew formula includes:

- **Binary Installation**: Creates `ros2-installer` command
- **Configuration**: Installs default config to `/opt/homebrew/etc/`
- **Dependencies**: Automatically handles Python dependencies
- **Cross-platform**: Works on both Intel and Apple Silicon Macs
- **Tests**: Includes verification tests

## 🧪 Testing & Validation

### Local Testing
```bash
# Syntax check
brew audit --strict Formula/ros2-installer.rb

# Install test
brew install --verbose Formula/ros2-installer.rb

# Function test
ros2-installer --validate-only
```

### Continuous Integration
Consider adding GitHub Actions to your tap repository:

```yaml
# .github/workflows/test.yml
name: Test Formula
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test formula
        run: brew test-bot Formula/ros2-installer.rb
```

## 📋 Maintenance

### Updating Versions
1. Update version in `ros2_installer_cli.py`
2. Run `./prepare-release.sh NEW_VERSION`
3. Create GitHub release with new tarball
4. Update formula with new URL and SHA256
5. Test and commit

### Adding Dependencies
Edit the formula's `depends_on` section:
```ruby
depends_on "python@3.11"
depends_on "new-dependency"
```

## 🐛 Troubleshooting

### Common Issues

**Formula Not Found**
```bash
# Ensure tap is added
brew tap your-username/ros-installer
```

**Python Path Issues**
```bash
# Check Python installation
brew info python@3.11
```

**Permission Errors**
```bash
# ROS2 installer needs sudo
sudo ros2-installer
```

## 🎯 Best Practices

1. **Versioning**: Use semantic versioning (v2.1.0)
2. **Testing**: Always test locally before publishing
3. **Documentation**: Keep formula comments updated
4. **Dependencies**: Pin Python versions for stability
5. **Security**: Verify SHA256 checksums

## 📞 Support

For Homebrew-specific issues:
- Check the formula syntax with `brew audit`
- Test installation with `brew install --verbose`
- Review Homebrew documentation

For ROS2 Installer issues:
- Check the main repository README
- Use `ros2-installer --validate-only` for system checks
- Enable debug logging with `--log-level DEBUG`

---

🎉 **Congratulations!** Your ROS2 Installer is now ready for Homebrew distribution!

Users can now install it with a simple `brew install ros2-installer` command instead of cloning repositories and managing dependencies manually.
