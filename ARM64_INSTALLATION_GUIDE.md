# 🍎 ARM64 Installation Guide for ROS2 Installer CLI

## The Issue

Homebrew on ARM64 systems (including Apple Silicon Macs and ARM-based Linux) has limited support and may fail to install formulas due to architecture compatibility issues.

## ✅ **RECOMMENDED SOLUTION: Manual Installation**

For ARM64 systems, use the manual installation method which works perfectly:

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/neelashkannan/ROS2-Installer-CLI.git
cd ROS2-Installer-CLI
```

### **Step 2: Install Dependencies**
```bash
pip3 install -r requirements.txt
```

### **Step 3: Use the Tool**
```bash
# Show help
sudo python3 ros2_installer_cli.py --help

# Install ROS2
sudo python3 ros2_installer_cli.py

# Silent installation
sudo python3 ros2_installer_cli.py --silent
```

## 🔧 **Alternative: Create a Simple Wrapper Script**

If you want a `ros2-installer` command on ARM64, create a simple wrapper:

### **Step 1: Create the Wrapper**
```bash
# Create a wrapper script
sudo tee /usr/local/bin/ros2-installer << 'EOF'
#!/bin/bash
cd /path/to/ROS2-Installer-CLI
sudo python3 ros2_installer_cli.py "$@"
EOF

# Make it executable
sudo chmod +x /usr/local/bin/ros2-installer
```

### **Step 2: Update the Path**
Replace `/path/to/ROS2-Installer-CLI` with your actual path:
```bash
# Find your path
pwd
# Update the wrapper script with the correct path
```

## 🐳 **Docker Solution (Recommended for Containers)**

If you're running in a container, create a Dockerfile:

```dockerfile
FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone and install
RUN git clone https://github.com/neelashkannan/ROS2-Installer-CLI.git /opt/ros2-installer
WORKDIR /opt/ros2-installer
RUN pip3 install -r requirements.txt

# Create wrapper
RUN echo '#!/bin/bash\ncd /opt/ros2-installer\npython3 ros2_installer_cli.py "$@"' > /usr/local/bin/ros2-installer
RUN chmod +x /usr/local/bin/ros2-installer

# Set entrypoint
ENTRYPOINT ["ros2-installer"]
```

## 📊 **Architecture Compatibility Summary**

| Architecture | Homebrew | Manual | Docker | Status |
|-------------|----------|--------|--------|--------|
| x86_64 (Intel) | ✅ | ✅ | ✅ | Fully Supported |
| ARM64 (Apple Silicon) | ⚠️ | ✅ | ✅ | Manual Recommended |
| ARM64 (Linux) | ❌ | ✅ | ✅ | Manual Required |

## 🎯 **Why This Happens**

1. **Homebrew ARM64 Support**: Homebrew on ARM64 is "Tier 2" support
2. **Bottle Availability**: Many formulas don't have ARM64 bottles
3. **Dependency Issues**: Some dependencies may not be available for ARM64
4. **Container Limitations**: Docker containers may have additional restrictions

## 🚀 **Quick Start for ARM64**

```bash
# One-liner installation
git clone https://github.com/neelashkannan/ROS2-Installer-CLI.git && \
cd ROS2-Installer-CLI && \
pip3 install -r requirements.txt && \
sudo python3 ros2_installer_cli.py --help
```

## 🔍 **Verification**

After installation, verify it works:
```bash
# Check version
python3 ros2_installer_cli.py --version

# Check help
python3 ros2_installer_cli.py --help

# Validate system
sudo python3 ros2_installer_cli.py --validate-only
```

## 📝 **Note**

The manual installation method is actually **more reliable** than Homebrew on ARM64 systems and gives you the same functionality. The `pyyaml` dependency issue you encountered was just a symptom of the broader ARM64 compatibility challenges with Homebrew.

**Bottom line**: Use manual installation on ARM64 - it's faster, more reliable, and gives you the same result! 🎉
