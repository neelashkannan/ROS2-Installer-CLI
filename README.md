# ROS2 Kilted Kaiju CLI Installer

## Overview

Command-line installer for ROS2 Kilted Kaiju distribution. This CLI-only version is designed for automation, server environments, and headless installations.

---

## Quick Start

### Basic Installation
```bash
# Standard installation with prompts
sudo python3 ros2_installer_cli.py

# Silent installation (no prompts)
sudo python3 ros2_installer_cli.py --silent

# Specific package set
sudo python3 ros2_installer_cli.py --package-set desktop --silent
```

### Validation & Testing
```bash
# Validate system requirements only
sudo python3 ros2_installer_cli.py --validate-only

# Dry run (simulate installation)
sudo python3 ros2_installer_cli.py --dry-run

# Show current configuration
sudo python3 ros2_installer_cli.py --show-config
```

### Custom Configuration
```bash
# Use custom config file
sudo python3 ros2_installer_cli.py --config production.yaml

# Override specific settings
sudo python3 ros2_installer_cli.py --ros-distro humble --package-set base

# High-performance installation
sudo python3 ros2_installer_cli.py --parallel-jobs 8 --silent
```

---

## Configuration Options

### Package Sets Available
| Package Set | Description | Best For |
|---|---|---|
| **minimal** | Core ROS2 + CLI tools | Lightweight servers |
| **base** | Standard ROS2 functionality | Basic development |
| **desktop** | GUI tools included | Development workstations |
| **desktop-full** | Complete development environment | Full robotics development |

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

---

## Command-Line Options

```bash
ROS2 Kilted Kaiju CLI Installer

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

---

## Usage Examples

### Basic Usage
```bash
# Interactive installation
sudo python3 ros2_installer_cli.py

# Silent installation with specific package set
sudo python3 ros2_installer_cli.py --silent --package-set desktop

# Using custom configuration
sudo python3 ros2_installer_cli.py --config custom.yaml --silent
```

---

## System Requirements

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

---

## Troubleshooting

### Common Issues

**Permission Denied**
```bash
# Solution: Run with sudo
sudo python3 ros2_installer_cli.py
```

**Package Not Found**
```bash
# Solution: Update package index
sudo apt-get update
sudo python3 ros2_installer_cli.py --validate-only
```

**Network Timeout**
```bash
# Solution: Increase timeout in config
sudo python3 ros2_installer_cli.py --config custom_config.yaml
```

### Debug Mode
```bash
# Enable detailed logging
sudo python3 ros2_installer_cli.py --log-level DEBUG

# Check installation logs
tail -f /tmp/ros2_installation.log
```

---

## Post-Installation

### Verify Installation
```bash
# Source ROS2 environment
source ~/.bashrc

# Verify installation
ros2 --help

# Run a simple test
ros2 run demo_nodes_cpp talker
```

---

## Author

**Neelash Kannan**  
📧 Email: [neelashkannan@outlook.com](mailto:neelashkannan@outlook.com)  
🐙 GitHub: [neelashkannan](https://github.com/neelashkannan)  
📂 Repository: [ROS2-Installer-CLI](https://github.com/neelashkannan/ROS2-Installer-CLI)

### Contributing
Feel free to open issues or submit pull requests to improve this installer. Your contributions are welcome!

