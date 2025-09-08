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
