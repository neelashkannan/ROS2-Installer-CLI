# ROS2 Kilted Kaiju CLI Installer

A production-grade command-line installer for ROS2 Kilted Kaiju distribution, designed for automation, server environments, and headless installations.

## 🚀 Quick Start

### Installation Methods

#### 🍺 Homebrew Installation (x86_64 Recommended)
```bash
# Add the tap
brew tap neelashkannan/ros-installer

# Install the tool
brew install ros2-installer

# Use it
sudo ros2-installer --help
```

> **Note:** Homebrew installation works best on x86_64 systems. For ARM64 systems (like Apple Silicon Macs or ARM-based Linux), manual installation is recommended due to Homebrew's limited ARM64 support.

#### 📦 Manual Installation (All Architectures)
```bash
# Clone the repository
git clone https://github.com/neelashkannan/ROS2-Installer-CLI.git
cd ROS2-Installer-CLI

# Install dependencies
pip3 install -r requirements.txt

# Use the tool
sudo python3 ros2_installer_cli.py --help
```

### Basic Usage

```bash
# Interactive installation
sudo ros2-installer

# Silent installation with specific package set
sudo ros2-installer --silent --package-set desktop

# Validate system requirements only
sudo ros2-installer --validate-only

# Show help
ros2-installer --help
```

## 📦 Package Sets

| Package Set | Description | Best For |
|-------------|-------------|----------|
| **minimal** | Core ROS2 + CLI tools | Lightweight servers |
| **base** | Standard ROS2 functionality | Basic development |
| **desktop** | GUI tools included | Development workstations |
| **desktop-full** | Complete development environment | Full robotics development |

## ⚙️ Configuration

### Command-Line Options

```bash
Options:
  -h, --help           Show help message and exit
  --version            Show version number
  --config CONFIG      Configuration file path (default: config.yaml)
  --package-set SET    Package set: minimal, base, desktop, desktop-full
  --ros-distro DISTRO  ROS distribution: kilted, jazzy, iron, humble, rolling
  --log-level LEVEL    Logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
  --silent             Silent installation (no user interaction)
  --validate-only      Only validate system requirements
  --dry-run            Simulate installation without changes
  --show-config        Display current configuration
  --parallel-jobs N    Number of parallel installation jobs
```

### Configuration File Example

```yaml
# config_cli.yaml
installation:
  ros_distro: "kilted"
  package_set: "desktop-full"
  uninstall_existing: true
  parallel_jobs: 4
  retry_attempts: 3

system:
  update_system: true
  install_dependencies: true
  backup_configs: true

logging:
  level: "INFO"
  console: true
  file: "/tmp/ros2_installation.log"

performance:
  parallel_downloads: true
  download_cache: true
  compression: true
```

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Ubuntu 24.04 LTS (Noble Numbat)
- **Architecture**: AMD64, ARM64, AArch64
- **Memory**: 2 GB RAM
- **Disk**: 4 GB free space
- **Network**: Internet connection for package downloads

### Recommended Specifications
- **Memory**: 8 GB RAM for desktop-full installation
- **Disk**: 10 GB free space for complete development environment
- **CPU**: Multi-core for parallel installation benefits

## 🔧 Troubleshooting

### Common Issues

**Permission Denied**
```bash
# Solution: Run with sudo
sudo ros2-installer
```

**Package Not Found**
```bash
# Solution: Update package index
sudo apt-get update
sudo ros2-installer --validate-only
```

**Network Timeout**
```bash
# Solution: Increase timeout in config
sudo ros2-installer --config custom_config.yaml
```

**ARM64 Homebrew Issues**
```bash
# Solution: Use manual installation
git clone https://github.com/neelashkannan/ROS2-Installer-CLI.git
cd ROS2-Installer-CLI
pip3 install -r requirements.txt
sudo python3 ros2_installer_cli.py
```

### Debug Mode
```bash
# Enable detailed logging
sudo ros2-installer --log-level DEBUG

# Check installation logs
tail -f /tmp/ros2_installation.log
```

## 📋 Post-Installation

### Verify Installation
```bash
# Source ROS2 environment
source ~/.bashrc

# Verify installation
ros2 --help

# Run a simple test
ros2 run demo_nodes_cpp talker
```

## 🏗️ Architecture Support

| Architecture | Homebrew | Manual | Status |
|-------------|----------|--------|--------|
| x86_64 (Intel) | ✅ | ✅ | Fully Supported |
| ARM64 (Apple Silicon) | ⚠️ | ✅ | Manual Recommended |
| ARM64 (Linux) | ⚠️ | ✅ | Manual Recommended |

## 📁 Project Structure

```
ROS2-Installer-CLI/
├── ros2_installer_cli.py      # Main installer script
├── config_cli.yaml            # Default configuration
├── requirements.txt           # Python dependencies
├── Formula/                   # Homebrew formula
│   └── ros2-installer.rb
└── README.md                  # This file
```

## 🎯 Features

- **Cross-platform**: Works on x86_64 and ARM64 systems
- **Multiple installation methods**: Homebrew and manual installation
- **Flexible configuration**: Command-line options and YAML config files
- **Package set selection**: Choose from minimal to desktop-full
- **Silent installation**: Perfect for automation and CI/CD
- **Validation mode**: Check system requirements without installing
- **Parallel processing**: Faster installation with multiple jobs
- **Comprehensive logging**: Debug and monitor installation process

## 👨‍💻 Author

**Neelash Kannan**  
📧 Email: [neelashkannan@outlook.com](mailto:neelashkannan@outlook.com)  
🐙 GitHub: [neelashkannan](https://github.com/neelashkannan)  
📂 Repository: [ROS2-Installer-CLI](https://github.com/neelashkannan/ROS2-Installer-CLI)

## 🤝 Contributing

Feel free to open issues or submit pull requests to improve this installer. Your contributions are welcome!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to install ROS2?** Choose your preferred method above and get started! 🚀