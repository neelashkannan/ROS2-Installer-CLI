# ROS2 CLI Installer

A simple command-line tool to install ROS2 on **Ubuntu** (native) or **any other OS** (via Docker).

Supports: `kilted` · `jazzy` · `iron` · `humble` · `rolling`

## Install

```bash
brew tap neelashkannan/ros-installer
brew install ros2-installer
```

Or manually:

```bash
git clone https://github.com/neelashkannan/ROS2-Installer-CLI.git
cd ROS2-Installer-CLI
pip3 install -r requirements.txt
```

## Usage

```bash
# Interactive install
ros2-installer

# Silent install with options
ros2-installer --silent --ros-distro humble --package-set desktop

# Validate system only
ros2-installer --validate-only

# Dry run (no changes)
ros2-installer --dry-run

# Show current config
ros2-installer --show-config
```

> If installed manually, replace `ros2-installer` with `python3 ros2_installer_cli.py` (use `sudo` on Ubuntu).

## How It Works

| System | What happens |
|--------|-------------|
| **Ubuntu** | Installs ROS2 natively via apt |
| **macOS / other Linux** | Installs Docker (if needed), builds a ROS2 container, and creates a `ros2` wrapper script so you can use ROS2 commands directly |

## Package Sets

| Set | Description |
|-----|-------------|
| `minimal` | Core ROS2 + CLI tools |
| `base` | Standard ROS2 packages |
| `desktop` | Includes GUI tools |
| `desktop-full` | Everything |

## Options

| Flag | Description |
|------|-------------|
| `--ros-distro` | ROS2 distro (`kilted`, `jazzy`, `iron`, `humble`, `rolling`) |
| `--package-set` | Package set (`minimal`, `base`, `desktop`, `desktop-full`) |
| `--silent` | No prompts |
| `--dry-run` | Simulate without installing |
| `--validate-only` | Check system requirements |
| `--show-config` | Print current configuration |
| `--config FILE` | Use a custom YAML config file |
| `--log-level LEVEL` | Set log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Requirements

- **Python 3** with `pyyaml` and `psutil`
- **Ubuntu**: 24.04 LTS, sudo access
- **macOS / other**: Docker (auto-installed if missing)

## Post-Install

```bash
# Ubuntu
source ~/.bashrc
ros2 --help

# macOS / Docker
ros2 topic list
```

## Project Structure

```
├── ros2_installer_cli.py   # Main script
├── config_cli.yaml         # Default config
├── requirements.txt        # Python deps
├── Formula/                # Homebrew formula
└── README.md
```

## Author

**Neelash Kannan** — [GitHub](https://github.com/neelashkannan) · [Email](mailto:neelashkannan@outlook.com)

## Contributing

Issues and pull requests are welcome.
