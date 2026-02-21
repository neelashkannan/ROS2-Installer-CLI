#!/usr/bin/env python3
"""
ROS2 Kilted Kaiju CLI Installer
============================================

Simple ROS2 installation system for command-line use.

Author: neelash kannan
Version: 2.1.0 (CLI-Only)
"""

import copy
import os
import sys
import platform
import shutil
import yaml
import time
import uuid
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from contextlib import contextmanager

# Version and metadata
__version__ = "2.1.0"
__author__ = "neelash kannan"

@dataclass
class InstallationResult:
    """Container for installation results."""
    success: bool
    duration: float
    packages_installed: int
    errors: List[str]
    warnings: List[str]
    session_id: str

@dataclass
class SystemInfo:
    """Container for system information."""
    os_name: str
    os_version: str
    architecture: str
    memory_gb: float
    disk_space_gb: float
    cpu_cores: int
    is_ubuntu: bool = False
    is_macos: bool = False
    linux_distro: str = ""

class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass

class ValidationError(Exception):
    """Validation-related errors."""
    pass

class InstallationError(Exception):
    """Installation-related errors."""
    pass

class CLIInstaller:
    """Production-grade CLI-only ROS2 installer with enterprise features."""
    
    def __init__(self, config_file: str = "config_cli.yaml"):
        """Initialize the CLI installer."""
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.logger = None  # Set early so error paths don't AttributeError
        self.config = self._load_configuration(config_file)
        self.logger = self._setup_logging()
        self.system_info = self._gather_system_info()
        self.installation_state = {
            'packages_installed': [],
            'repositories_added': [],
            'files_modified': [],
            'backup_files': []
        }
        
        # Performance tracking
        self.metrics = {
            'download_time': 0,
            'install_time': 0,
            'verification_time': 0,
            'total_packages': 0
        }
        
        self.logger.info(f"🚀 ROS2 CLI Installer v{__version__}")
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"System: {self.system_info.os_name} {self.system_info.os_version}")
    
    def _load_configuration(self, config_file: str) -> Dict[str, Any]:
        """Load and validate configuration."""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                self._create_default_config(config_path)
            
            with open(config_path, 'r') as f:
                if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            return self._validate_configuration(config)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _create_default_config(self, config_path: Path):
        """Create default configuration file."""
        default_config = {
            'installation': {
                'ros_distro': 'kilted',
                'package_set': 'desktop-full',
                'uninstall_existing': True,
                'parallel_jobs': 4,
                'retry_attempts': 3,
                'timeout_seconds': 300
            },
            'system': {
                'update_system': True,
                'install_dependencies': True,
                'backup_configs': True,
                'verify_compatibility': True
            },
            'logging': {
                'level': 'INFO',
                'file': '/tmp/ros2_installation.log',
                'console': True
            },
            'validation': {
                'min_disk_space_gb': 4,
                'min_memory_gb': 2,
                'required_ubuntu_version': '24.04',
                'supported_architectures': ['amd64', 'arm64', 'aarch64','x86_64']
            },
            'performance': {
                'parallel_downloads': True,
                'download_cache': True,
                'compression': True
            },
            'security': {
                'verify_signatures': True,
                'check_checksums': True,
                'secure_permissions': True,
                'audit_logging': True
            },
            'docker': {
                'container_name': 'ros2-kilted',
                'workspace_dir': str(Path.home() / 'ros2_ws'),
                'network_mode': 'host'
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def _validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration parameters."""
        required_sections = ['installation', 'logging']
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required section: {section}")
        
        # Validate ROS distro
        valid_distros = ['kilted', 'jazzy', 'iron', 'humble', 'rolling']
        distro = config['installation'].get('ros_distro', 'kilted')
        if distro not in valid_distros:
            raise ConfigurationError(f"Invalid ROS distro: {distro}")
        
        return config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger('ros2_cli_installer')
        logger.setLevel(getattr(logging, self.config['logging'].get('level', 'INFO')))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler
        log_file = self.config['logging'].get('file', '/tmp/ros2_installation.log')
        try:
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(session_id)s] - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except PermissionError:
            # Fallback to user home directory
            log_file = os.path.expanduser(f"~/ros2_installation_{self.session_id}.log")
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(session_id)s] - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # Console handler
        if self.config['logging'].get('console', True):
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # Add session ID via a filter instead of global setLogRecordFactory
        class SessionFilter(logging.Filter):
            def __init__(self, session_id):
                super().__init__()
                self._session_id = session_id
            def filter(self, record):
                record.session_id = self._session_id
                return True
        logger.addFilter(SessionFilter(self.session_id))
        
        return logger
    
    def _gather_system_info(self) -> SystemInfo:
        """Gather comprehensive system information."""
        try:
            import psutil  # type: ignore[import-untyped]
            
            os_name = platform.system()
            os_version = platform.release()
            architecture = platform.machine()
            
            # Memory information
            memory_bytes = psutil.virtual_memory().total
            memory_gb = memory_bytes / (1024**3)
            
            # Disk space
            disk_usage = shutil.disk_usage('/')
            disk_space_gb = disk_usage.free / (1024**3)
            
            # CPU information
            cpu_cores = psutil.cpu_count()
            
            # Detect OS type
            is_macos = (os_name == "Darwin")
            is_ubuntu = False
            linux_distro = ""
            
            if os_name == "Linux":
                try:
                    with open('/etc/os-release', 'r') as f:
                        os_release = f.read().lower()
                        if 'ubuntu' in os_release:
                            is_ubuntu = True
                            linux_distro = "ubuntu"
                        elif 'debian' in os_release:
                            linux_distro = "debian"
                        elif 'fedora' in os_release:
                            linux_distro = "fedora"
                        elif 'arch' in os_release:
                            linux_distro = "arch"
                        elif 'centos' in os_release or 'rhel' in os_release:
                            linux_distro = "rhel"
                        else:
                            linux_distro = "other"
                except FileNotFoundError:
                    linux_distro = "unknown"
            
            return SystemInfo(
                os_name=os_name,
                os_version=os_version,
                architecture=architecture,
                memory_gb=memory_gb,
                disk_space_gb=disk_space_gb,
                cpu_cores=cpu_cores,
                is_ubuntu=is_ubuntu,
                is_macos=is_macos,
                linux_distro=linux_distro
            )
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not gather complete system info: {e}")
            return SystemInfo("Unknown", "Unknown", "Unknown", 0, 0, 1)
    
    def _is_ubuntu(self) -> bool:
        """Check if the current system is Ubuntu."""
        return self.system_info.is_ubuntu

    def _is_docker_mode(self) -> bool:
        """Check if installation should use Docker (non-Ubuntu systems)."""
        return not self._is_ubuntu()

    def validate_system(self) -> bool:
        """Validate system requirements."""
        self.logger.info("🔍 Validating system requirements...")
        
        validation_config = self.config.get('validation', {})
        issues = []
        
        # Check disk space
        min_disk = validation_config.get('min_disk_space_gb', 4)
        if self.system_info.disk_space_gb < min_disk:
            issues.append(f"Insufficient disk space: {self.system_info.disk_space_gb:.1f}GB < {min_disk}GB")
        
        # Check memory
        min_memory = validation_config.get('min_memory_gb', 2)
        if self.system_info.memory_gb < min_memory:
            issues.append(f"Insufficient memory: {self.system_info.memory_gb:.1f}GB < {min_memory}GB")
        
        # Check architecture
        supported_archs = validation_config.get('supported_architectures', ['amd64', 'arm64', 'aarch64', 'x86_64'])
        if self.system_info.architecture not in supported_archs:
            issues.append(f"Unsupported architecture: {self.system_info.architecture}")
        
        if self._is_ubuntu():
            # Ubuntu-specific checks
            required_version = validation_config.get('required_ubuntu_version', '24.04')
            # Try to read actual Ubuntu version from /etc/os-release
            try:
                result = subprocess.run('lsb_release -rs', shell=True, capture_output=True, text=True)
                ubuntu_ver = result.stdout.strip()
                if ubuntu_ver and required_version not in ubuntu_ver:
                    self.logger.warning(f"Ubuntu version mismatch: {ubuntu_ver} != {required_version}")
            except Exception:
                pass
            
            # Check sudo privileges (required for native install)
            if os.geteuid() != 0:
                issues.append("Script must be run with sudo privileges for native Ubuntu installation")
        else:
            # Docker mode — just need Docker or ability to install it
            self.logger.info(f"🐳 Non-Ubuntu system detected ({self.system_info.os_name}), will use Docker")
            docker_available = self._check_docker_installed()
            if not docker_available:
                self.logger.info("🐳 Docker not found — it will be installed automatically")
        
        if issues:
            for issue in issues:
                self.logger.error(f"❌ {issue}")
            return False
        
        self.logger.info("✅ System validation passed")
        return True
    
    def display_system_info(self):
        """Display comprehensive system information."""
        self.logger.info("📊 System Information:")
        self.logger.info(f"  • OS: {self.system_info.os_name} {self.system_info.os_version}")
        if self.system_info.linux_distro:
            self.logger.info(f"  • Linux Distro: {self.system_info.linux_distro}")
        self.logger.info(f"  • Architecture: {self.system_info.architecture}")
        self.logger.info(f"  • Memory: {self.system_info.memory_gb:.1f} GB")
        self.logger.info(f"  • Disk Space: {self.system_info.disk_space_gb:.1f} GB")
        self.logger.info(f"  • CPU Cores: {self.system_info.cpu_cores}")
        self.logger.info(f"  • Install Mode: {'Native (Ubuntu)' if self._is_ubuntu() else 'Docker'}")
    
    def prompt_user_confirmation(self, silent: bool = False) -> bool:
        """Prompt user for installation confirmation."""
        if silent:
            return True
        
        self.logger.info("\n" + "="*60)
        self.logger.info("🤖 ROS2 Installation Summary")
        self.logger.info("="*60)
        
        config = self.config['installation']
        self.logger.info(f"  • ROS Distribution: {config['ros_distro']}")
        self.logger.info(f"  • Package Set: {config['package_set']}")
        
        if self._is_docker_mode():
            self.logger.info(f"  • Install Mode: 🐳 Docker container")
            container_name = self.config.get('docker', {}).get('container_name', f"ros2-{config['ros_distro']}")
            self.logger.info(f"  • Container Name: {container_name}")
        else:
            self.logger.info(f"  • Install Mode: Native Ubuntu")
            self.logger.info(f"  • Uninstall Existing: {config.get('uninstall_existing', True)}")
            self.logger.info(f"  • Parallel Jobs: {config.get('parallel_jobs', 4)}")
        
        self.display_system_info()
        
        self.logger.info("\n⚠️  This will modify your system by:")
        if self._is_docker_mode():
            if not self._check_docker_installed():
                self.logger.info("   - Installing Docker")
            self.logger.info("   - Building a Docker image with ROS2")
            self.logger.info("   - Creating a ROS2 Docker container")
            self.logger.info("   - Installing a 'ros2' wrapper command")
        else:
            self.logger.info("   - Installing ROS2 packages and dependencies")
            self.logger.info("   - Adding ROS2 repositories")
            self.logger.info("   - Modifying ~/.bashrc for environment setup")
            if config.get('uninstall_existing', True):
                self.logger.info("   - Removing existing ROS installations")
        
        print("\n" + "="*60)
        response = input("🚀 Proceed with installation? [y/N]: ").strip().lower()
        return response in ['y', 'yes']
    
    @contextmanager
    def _rollback_on_failure(self):
        """Context manager for automatic rollback on failure."""
        initial_state = copy.deepcopy(self.installation_state)
        try:
            yield
        except Exception as e:
            self.logger.error(f"Installation failed, initiating rollback: {e}")
            self._rollback_installation(initial_state)
            raise
    
    def _rollback_installation(self, initial_state: Dict):
        """Rollback installation to previous state."""
        self.logger.info("🔄 Rolling back installation...")
        
        # Remove installed packages
        new_packages = set(self.installation_state['packages_installed']) - set(initial_state.get('packages_installed', []))
        if new_packages:
            package_list = ' '.join(new_packages)
            try:
                self._run_command(f"sudo apt-get remove -y {package_list}", "Removing newly installed packages")
            except Exception as e:
                self.logger.warning(f"Failed to remove packages during rollback: {e}")
        
        # Restore backup files
        for backup_file in self.installation_state.get('backup_files', []):
            try:
                # Strip the .backup.<session_id> suffix to recover the original path
                original_file = backup_file.rsplit('.backup.', 1)[0]
                if os.path.exists(backup_file):
                    os.rename(backup_file, original_file)
                    self.logger.info(f"Restored {original_file}")
            except Exception as e:
                self.logger.warning(f"Failed to restore {backup_file}: {e}")
        
        self.logger.info("✅ Rollback completed")
    
    def _run_command(self, command: str, description: str = "", timeout: int = None, retries: int = None) -> subprocess.CompletedProcess:
        """Execute command with retry logic and error handling."""
        timeout = timeout or self.config.get('installation', {}).get('timeout_seconds', 300)
        retries = retries or self.config.get('installation', {}).get('retry_attempts', 3)
        
        self.logger.debug(f"Executing: {command}")
        
        for attempt in range(retries):
            try:
                start_time = time.time()
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    capture_output=True,
                    timeout=timeout,
                    text=True
                )
                duration = time.time() - start_time
                self.logger.info(f"✅ {description} (took {duration:.2f}s)")
                return result
            except subprocess.TimeoutExpired:
                self.logger.warning(f"⏰ Command timed out (attempt {attempt + 1}/{retries}): {command}")
                # Clean up any remaining apt-get/dpkg processes before retrying
                if 'apt-get' in command or 'dpkg' in command:
                    self._cleanup_package_processes()
                if attempt == retries - 1:
                    raise
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"❌ Command failed (attempt {attempt + 1}/{retries}): {command}")
                self.logger.warning(f"Exit code: {e.returncode}")
                # Clean up any remaining apt-get/dpkg processes before retrying
                if 'apt-get' in command or 'dpkg' in command:
                    self._cleanup_package_processes()
                if attempt == retries - 1:
                    raise
            
            # Exponential backoff
            time.sleep(2 ** attempt)
    
    def _cleanup_package_processes(self):
        """Clean up any remaining apt-get or dpkg processes."""
        try:
            self.logger.info("🧹 Cleaning up package management processes...")
            # Kill any running apt-get processes
            subprocess.run("sudo pkill -f apt-get", shell=True, capture_output=True)
            # Kill any running dpkg processes
            subprocess.run("sudo pkill -f dpkg", shell=True, capture_output=True)
            # Wait a moment for processes to terminate
            time.sleep(2)
            # Clean up any stale locks
            subprocess.run("sudo dpkg --configure -a", shell=True, capture_output=True)
            self.logger.info("✅ Package management cleanup completed")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup package processes: {e}")
    
    def _install_package_sequential(self, packages: List[str]) -> Dict[str, bool]:
        """Install packages sequentially (apt/dpkg does not support parallel installs)."""
        self.logger.info(f"📦 Installing {len(packages)} packages...")
        
        results = {}
        
        for package in packages:
            try:
                self._run_command(f"sudo apt-get install -y {package}", f"Installing {package}")
                self.installation_state['packages_installed'].append(package)
                results[package] = True
            except Exception as e:
                self.logger.error(f"Failed to install {package}: {e}")
                results[package] = False
        
        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"✅ Installed {successful}/{len(packages)} packages successfully")
        
        return results
    
    # ─── Docker helper methods ───────────────────────────────────────

    def _check_docker_installed(self) -> bool:
        """Check if Docker is installed and accessible."""
        try:
            result = subprocess.run(
                "docker --version", shell=True,
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_docker_running(self) -> bool:
        """Check if the Docker daemon is running."""
        try:
            result = subprocess.run(
                "docker info", shell=True,
                capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except Exception:
            return False

    def _install_docker(self):
        """Install Docker on the current system."""
        self.logger.info("🐳 Installing Docker...")

        if self.system_info.is_macos:
            self._install_docker_macos()
        elif self.system_info.os_name == "Linux":
            self._install_docker_linux()
        else:
            raise InstallationError(
                f"Automatic Docker installation is not supported on {self.system_info.os_name}. "
                "Please install Docker manually and re-run this installer."
            )

    def _install_docker_macos(self):
        """Install Docker on macOS via Homebrew."""
        # Check for Homebrew
        if not shutil.which("brew"):
            raise InstallationError(
                "Homebrew is required to install Docker on macOS. "
                "Install it from https://brew.sh and re-run this installer."
            )

        self.logger.info("🍺 Installing Docker via Homebrew...")
        subprocess.run(
            "brew install --cask docker",
            shell=True, check=True, timeout=600
        )

        self.logger.info("🐳 Please open the Docker Desktop application to start the Docker daemon.")
        self.logger.info("   Waiting for Docker daemon to become available...")
        self._wait_for_docker_daemon()

    def _install_docker_linux(self):
        """Install Docker on a non-Ubuntu Linux distribution."""
        distro = self.system_info.linux_distro

        if distro in ("debian",):
            cmds = [
                "sudo apt-get update",
                "sudo apt-get install -y ca-certificates curl gnupg",
                "sudo install -m 0755 -d /etc/apt/keyrings",
                "curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
                "sudo chmod a+r /etc/apt/keyrings/docker.gpg",
                'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] '
                'https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" '
                '| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
                "sudo apt-get update",
                "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
            ]
        elif distro in ("fedora", "rhel"):
            cmds = [
                "sudo dnf -y install dnf-plugins-core",
                "sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo",
                "sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                "sudo systemctl start docker",
                "sudo systemctl enable docker",
            ]
        elif distro == "arch":
            cmds = [
                "sudo pacman -Sy --noconfirm docker",
                "sudo systemctl start docker",
                "sudo systemctl enable docker",
            ]
        else:
            raise InstallationError(
                f"Automatic Docker installation is not supported on '{distro}'. "
                "Please install Docker manually: https://docs.docker.com/engine/install/"
            )

        for cmd in cmds:
            self.logger.debug(f"Running: {cmd}")
            subprocess.run(cmd, shell=True, check=True, timeout=300)

        self.logger.info("🐳 Docker installed successfully")
        self._wait_for_docker_daemon()

    def _wait_for_docker_daemon(self, timeout: int = 120):
        """Wait for the Docker daemon to become responsive."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._check_docker_running():
                self.logger.info("✅ Docker daemon is running")
                return
            time.sleep(3)
        raise InstallationError(
            "Docker daemon did not start within the timeout. "
            "Please start Docker manually and re-run this installer."
        )

    def _get_ros_docker_image(self) -> str:
        """Return the official Docker image tag for the selected distro and package set.

        The official 'ros' images on Docker Hub provide ros-core and ros-base.
        The 'osrf/ros' images provide desktop and desktop-full.
        """
        distro = self.config['installation']['ros_distro']
        package_set = self.config['installation'].get('package_set', 'desktop-full')

        # Official 'ros' repo has ros-core and ros-base tags
        # OSRF 'osrf/ros' repo has desktop and desktop-full tags
        image_map = {
            'minimal':      f"ros:{distro}-ros-core",
            'base':         f"ros:{distro}-ros-base",
            'desktop':      f"osrf/ros:{distro}-desktop",
            'desktop-full': f"osrf/ros:{distro}-desktop-full",
        }
        return image_map.get(package_set, f"osrf/ros:{distro}-desktop-full")

    def _generate_dockerfile(self) -> str:
        """Generate a Dockerfile for the requested ROS2 setup."""
        base_image = self._get_ros_docker_image()
        distro = self.config['installation']['ros_distro']
        package_set = self.config['installation'].get('package_set', 'desktop-full')

        # Build the list of extra apt packages for desktop variants
        extra_apt_lines = ""
        if package_set in ('desktop', 'desktop-full'):
            extra_packages = [
                f"ros-{distro}-gazebo-ros-pkgs",
                f"ros-{distro}-navigation2",
                f"ros-{distro}-moveit",
                f"ros-{distro}-slam-toolbox",
                f"ros-{distro}-robot-localization",
            ]
            extra_apt_lines = "".join(f"    {pkg} \\\n" for pkg in extra_packages)

        # Build the dev-tools install line list
        dev_packages = [
            "python3-rosdep",
            "python3-colcon-common-extensions",
            "python3-vcstool",
            "python3-argcomplete",
            "python3-flake8",
            "python3-pytest",
        ]
        dev_apt_lines = "".join(f"    {pkg} \\\n" for pkg in dev_packages)

        dockerfile = (
            f"# Auto-generated by ROS2 CLI Installer v{__version__}\n"
            f"FROM {base_image}\n"
            f"\n"
            f"ENV DEBIAN_FRONTEND=noninteractive\n"
            f"\n"
            f"# Install development tools\n"
            f"RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
            f"{dev_apt_lines}"
            f"{extra_apt_lines}"
            f"    && rm -rf /var/lib/apt/lists/*\n"
            f"\n"
            f"# Initialize rosdep\n"
            f"RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \\\n"
            f"      rosdep init; \\\n"
            f"    fi && rosdep update\n"
            f"\n"
            f"# Setup entrypoint\n"
            f"RUN echo '#!/bin/bash' > /ros_entrypoint.sh && \\\n"
            f"    echo 'set -e' >> /ros_entrypoint.sh && \\\n"
            f"    echo 'source /opt/ros/{distro}/setup.bash' >> /ros_entrypoint.sh && \\\n"
            f"    echo 'exec \"$@\"' >> /ros_entrypoint.sh && \\\n"
            f"    chmod +x /ros_entrypoint.sh\n"
            f"\n"
            f"ENTRYPOINT [\"/ros_entrypoint.sh\"]\n"
            f"CMD [\"bash\"]\n"
        )
        return dockerfile

    def _build_docker_image(self) -> str:
        """Build the ROS2 Docker image and return its tag."""
        distro = self.config['installation']['ros_distro']
        image_tag = f"ros2-installer/{distro}:latest"

        build_dir = Path.home() / ".ros2-installer" / "docker"
        build_dir.mkdir(parents=True, exist_ok=True)

        dockerfile_path = build_dir / "Dockerfile"
        dockerfile_path.write_text(self._generate_dockerfile())
        self.logger.info(f"📝 Dockerfile written to {dockerfile_path}")

        self.logger.info(f"🔨 Building Docker image '{image_tag}' — this may take a few minutes...")
        subprocess.run(
            f"docker build -t {image_tag} {build_dir}",
            shell=True, check=True, timeout=1800
        )
        self.logger.info(f"✅ Docker image '{image_tag}' built successfully")
        return image_tag

    def _create_docker_container(self, image_tag: str) -> str:
        """Create (or recreate) the persistent ROS2 Docker container."""
        distro = self.config['installation']['ros_distro']
        container_name = self.config.get('docker', {}).get(
            'container_name', f"ros2-{distro}"
        )
        workspace_dir = self.config.get('docker', {}).get(
            'workspace_dir', str(Path.home() / "ros2_ws")
        )

        # Ensure the host workspace directory exists
        Path(workspace_dir).mkdir(parents=True, exist_ok=True)

        # Remove existing container with the same name (if any)
        subprocess.run(
            f"docker rm -f {container_name} 2>/dev/null",
            shell=True, capture_output=True
        )

        self.logger.info(f"🐳 Creating container '{container_name}'...")

        docker_run_cmd = (
            f"docker create "
            f"--name {container_name} "
            f"-it "
            f"--network host "
            f"-v {workspace_dir}:/root/ros2_ws "
            f"-e DISPLAY=${{DISPLAY:-:0}} "
            f"-e ROS_DOMAIN_ID=0 "
            f"{image_tag} "
            f"bash"
        )

        subprocess.run(docker_run_cmd, shell=True, check=True, timeout=60)
        self.logger.info(f"✅ Container '{container_name}' created")
        self.logger.info(f"   Host workspace mounted at: {workspace_dir} → /root/ros2_ws")
        return container_name

    def _create_ros2_wrapper_script(self, container_name: str):
        """Install a host-side 'ros2' wrapper that forwards commands into the container."""
        distro = self.config['installation']['ros_distro']

        wrapper_content = f"""#!/usr/bin/env bash
# ROS2 Docker wrapper — generated by ROS2 CLI Installer v{__version__}
# Container: {container_name}
set -e

CONTAINER="{container_name}"

# Start the container if it isn't running
if [ "$(docker inspect -f '{{{{.State.Running}}}}' "$CONTAINER" 2>/dev/null)" != "true" ]; then
    docker start "$CONTAINER" > /dev/null
fi

if [ $# -eq 0 ]; then
    # No arguments — open an interactive shell inside the container
    exec docker exec -it "$CONTAINER" bash
else
    # Forward the command into the container
    exec docker exec -it "$CONTAINER" bash -ic "source /opt/ros/{distro}/setup.bash && ros2 $*"
fi
"""

        # Determine install location
        if self.system_info.is_macos:
            bin_dir = Path.home() / ".local" / "bin"
        else:
            bin_dir = Path("/usr/local/bin")

        bin_dir.mkdir(parents=True, exist_ok=True)
        wrapper_path = bin_dir / "ros2"
        wrapper_path.write_text(wrapper_content)
        wrapper_path.chmod(0o755)

        self.logger.info(f"✅ Wrapper script installed at {wrapper_path}")

        # Check if the directory is on PATH
        if str(bin_dir) not in os.environ.get("PATH", ""):
            shell_rc = self._get_shell_rc_path()
            if shell_rc:
                export_line = f'\nexport PATH="{bin_dir}:$PATH"  # Added by ROS2 CLI Installer\n'
                try:
                    existing = shell_rc.read_text() if shell_rc.exists() else ""
                    if str(bin_dir) not in existing:
                        with open(shell_rc, 'a') as f:
                            f.write(export_line)
                        self.logger.info(f"   Added {bin_dir} to PATH in {shell_rc}")
                except Exception as e:
                    self.logger.warning(f"   Could not update PATH in shell rc: {e}")
            self.logger.info(f"   ⚠️  Make sure {bin_dir} is in your PATH")

    def _get_shell_rc_path(self) -> Optional[Path]:
        """Return the appropriate shell rc file for the current user."""
        shell = os.environ.get("SHELL", "")
        home = Path.home()
        if "zsh" in shell:
            return home / ".zshrc"
        elif "bash" in shell:
            if self.system_info.is_macos:
                return home / ".bash_profile"
            return home / ".bashrc"
        return None

    def _verify_docker_installation(self, container_name: str):
        """Verify the Docker-based ROS2 installation."""
        self.logger.info("✅ Verifying Docker-based ROS2 installation...")
        distro = self.config['installation']['ros_distro']

        # Start container
        subprocess.run(
            f"docker start {container_name}",
            shell=True, check=True, capture_output=True, timeout=30
        )

        # Test ros2 command inside container
        result = subprocess.run(
            f"docker exec {container_name} bash -c 'source /opt/ros/{distro}/setup.bash && ros2 --help'",
            shell=True, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise InstallationError(
                f"ROS2 verification failed inside container: {result.stderr}"
            )

        self.logger.info("✅ ROS2 is working inside the Docker container")

    def install_ros2_docker(self, silent: bool = False) -> InstallationResult:
        """Install ROS2 via Docker for non-Ubuntu systems."""
        start_time = time.time()
        errors: List[str] = []
        warnings: List[str] = []

        try:
            # Validate
            if not self.validate_system():
                raise ValidationError("System validation failed")

            if not self.prompt_user_confirmation(silent):
                self.logger.info("Installation cancelled by user")
                return InstallationResult(False, 0, 0, ["Installation cancelled by user"], [], self.session_id)

            # Step 1: Ensure Docker is installed
            if not self._check_docker_installed():
                self._install_docker()

            # Step 2: Ensure Docker daemon is running
            if not self._check_docker_running():
                self._wait_for_docker_daemon()

            # Step 3: Build the Docker image
            image_tag = self._build_docker_image()

            # Step 4: Create the container
            container_name = self._create_docker_container(image_tag)

            # Step 5: Install the wrapper script
            self._create_ros2_wrapper_script(container_name)

            # Step 6: Verify
            self._verify_docker_installation(container_name)

            duration = time.time() - start_time
            distro = self.config['installation']['ros_distro']
            self.logger.info(f"🎉 Docker-based ROS2 {distro} installation completed in {duration:.2f}s")

            return InstallationResult(
                success=True,
                duration=duration,
                packages_installed=1,  # Docker image counts as 1 logical package
                errors=errors,
                warnings=warnings,
                session_id=self.session_id
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"💥 Docker installation failed after {duration:.2f}s: {e}")
            errors.append(str(e))
            return InstallationResult(
                success=False,
                duration=duration,
                packages_installed=0,
                errors=errors,
                warnings=warnings,
                session_id=self.session_id
            )

    # ─── Main install entry point ─────────────────────────────────────

    def install_ros2(self, silent: bool = False) -> InstallationResult:
        """Main installation method — routes to native or Docker based on OS."""
        if self._is_docker_mode():
            return self.install_ros2_docker(silent)
        return self._install_ros2_native(silent)

    def _install_ros2_native(self, silent: bool = False) -> InstallationResult:
        """Native Ubuntu installation with comprehensive error handling."""
        start_time = time.time()
        errors = []
        warnings = []
        packages_installed = 0
        
        try:
            # Validate system
            if not self.validate_system():
                raise ValidationError("System validation failed")
            
            # User confirmation
            if not self.prompt_user_confirmation(silent):
                self.logger.info("Installation cancelled by user")
                return InstallationResult(False, 0, 0, ["Installation cancelled by user"], [], self.session_id)
            
            with self._rollback_on_failure():
                # Update system
                self._update_system()
                
                # Handle existing installations
                if self.config.get('installation', {}).get('uninstall_existing', True):
                    self._uninstall_existing_ros()
                
                # Setup repositories
                self._setup_repositories()
                
                # Install packages
                packages_installed = self._install_packages()
                
                # Setup development tools
                self._setup_development_tools()
                
                # Configure environment
                self._configure_environment()
                
                # Verify installation
                self._verify_installation()
                
                duration = time.time() - start_time
                self.logger.info(f"🎉 Installation completed successfully in {duration:.2f} seconds")
                
                return InstallationResult(
                    success=True,
                    duration=duration,
                    packages_installed=packages_installed,
                    errors=errors,
                    warnings=warnings,
                    session_id=self.session_id
                )
        
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"💥 Installation failed after {duration:.2f} seconds: {e}")
            errors.append(str(e))
            
            return InstallationResult(
                success=False,
                duration=duration,
                packages_installed=packages_installed,
                errors=errors,
                warnings=warnings,
                session_id=self.session_id
            )
    
    def _update_system(self):
        """Update system packages."""
        if not self.config.get('system', {}).get('update_system', True):
            return
        
        self.logger.info("🔄 Updating system packages...")
        self._run_command("sudo apt-get update", "Updating package index")
        
        if self.config.get('system', {}).get('install_dependencies', True):
            essential_packages = [
                "software-properties-common", "curl", "wget", "gnupg2",
                "lsb-release", "apt-transport-https", "ca-certificates"
            ]
            packages_str = ' '.join(essential_packages)
            self._run_command(f"sudo apt-get install -y {packages_str}", "Installing essential packages")
    
    def _uninstall_existing_ros(self):
        """Uninstall existing ROS installations."""
        self.logger.info("🗑️ Checking for existing ROS installations...")
        
        # Check for ROS1 and ROS2 packages
        try:
            result = subprocess.run("dpkg -l | grep -E 'ros-(melodic|noetic|foxy|galactic|humble|iron|jazzy|kilted)'",
                                  shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                self.logger.info("Found existing ROS installations, removing...")
                self._run_command("sudo apt-get autoremove -y 'ros-*'", "Removing ROS packages")
                self._run_command("sudo apt-get autoremove -y", "Cleaning up dependencies")
            else:
                self.logger.info("No existing ROS installations found")
        except Exception as e:
            self.logger.warning(f"Could not check for existing ROS installations: {e}")
    
    def _setup_repositories(self):
        """Setup ROS2 repositories."""
        if not self.config.get('system', {}).get('install_dependencies', True):
            return
        
        self.logger.info("📁 Setting up ROS2 repositories...")
        
        # Add GPG key
        self._run_command(
            "sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg",
            "Adding ROS2 GPG key"
        )
        
        # Add repository
        distro = self.config['installation']['ros_distro']
        arch = subprocess.run("dpkg --print-architecture", shell=True, capture_output=True, text=True).stdout.strip()
        codename = subprocess.run("lsb_release -cs", shell=True, capture_output=True, text=True).stdout.strip()
        
        repo_line = f"deb [arch={arch} signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu {codename} main"
        self._run_command(f'echo "{repo_line}" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null', "Adding ROS2 repository")
        
        # Update package index
        self._run_command("sudo apt-get update", "Updating package index with ROS2 repository")
        
        self.installation_state['repositories_added'].append('/etc/apt/sources.list.d/ros2.list')
    
    def _install_packages(self) -> int:
        """Install ROS2 packages based on configuration."""
        package_set = self.config['installation'].get('package_set', 'desktop-full')
        distro = self.config['installation']['ros_distro']
        
        self.logger.info(f"📦 Installing ROS2 {distro} {package_set} packages...")
        
        # Main package installation
        if package_set == 'minimal':
            packages = [f"ros-{distro}-ros-core", f"ros-{distro}-ros2cli"]
        elif package_set == 'base':
            packages = [f"ros-{distro}-ros-base", f"ros-{distro}-ros2cli", f"ros-{distro}-demo-nodes-cpp", f"ros-{distro}-demo-nodes-py"]
        elif package_set == 'desktop':
            packages = [f"ros-{distro}-desktop", f"ros-{distro}-rviz2"]
        else:  # desktop-full
            packages = [f"ros-{distro}-desktop-full"]
        
        # Install main packages with appropriate timeout
        packages_str = ' '.join(packages)
        # Use longer timeout for desktop-full installation (20 minutes instead of 5)
        timeout = 1200 if package_set == 'desktop-full' else None
        self._run_command(f"sudo apt-get install -y {packages_str}", f"Installing {package_set} packages", timeout=timeout)
        self.installation_state['packages_installed'].extend(packages)
        
        # Install additional commonly used packages
        if package_set in ['desktop', 'desktop-full']:
            additional_packages = [
                f"ros-{distro}-gazebo-ros-pkgs",
                f"ros-{distro}-navigation2",
                f"ros-{distro}-moveit",
                f"ros-{distro}-slam-toolbox",
                f"ros-{distro}-robot-localization"
            ]
            
            for package in additional_packages:
                try:
                    self._run_command(f"sudo apt-get install -y {package}", f"Installing {package}")
                    self.installation_state['packages_installed'].append(package)
                except Exception as e:
                    self.logger.warning(f"Optional package {package} failed to install: {e}")
        
        return len(self.installation_state['packages_installed'])
    
    def _setup_development_tools(self):
        """Setup development tools."""
        self.logger.info("🛠️ Setting up development tools...")
        
        dev_packages = [
            "python3-rosdep", "python3-colcon-common-extensions", 
            "python3-vcstool", "python3-argcomplete",
            "python3-flake8", "python3-pytest"
        ]
        
        # Install development packages
        for package in dev_packages:
            try:
                self._run_command(f"sudo apt-get install -y {package}", f"Installing {package}")
                self.installation_state['packages_installed'].append(package)
            except Exception as e:
                self.logger.warning(f"Failed to install {package}: {e}")
        
        # Initialize rosdep
        if not os.path.exists('/etc/ros/rosdep/sources.list.d/20-default.list'):
            self._run_command("sudo rosdep init", "Initializing rosdep")
        
        # Update rosdep
        original_user = os.environ.get('SUDO_USER')
        if original_user:
            try:
                self._run_command(f"sudo -u {original_user} rosdep update", "Updating rosdep database")
            except Exception as e:
                self.logger.warning(f"Failed to update rosdep: {e}")
    
    def _configure_environment(self):
        """Configure ROS2 environment."""
        self.logger.info("🌍 Configuring environment...")
        
        original_user = os.environ.get('SUDO_USER')
        if not original_user:
            self.logger.warning("Could not determine original user for environment setup")
            return
        
        user_home = os.path.expanduser(f"~{original_user}")
        bashrc_path = os.path.join(user_home, ".bashrc")
        distro = self.config['installation']['ros_distro']
        
        # Backup existing bashrc
        if os.path.exists(bashrc_path) and self.config.get('system', {}).get('backup_configs', True):
            backup_path = f"{bashrc_path}.backup.{self.session_id}"
            self._run_command(f"cp {bashrc_path} {backup_path}", "Backing up .bashrc")
            self.installation_state['backup_files'].append(backup_path)
        
        # Add ROS2 setup to bashrc
        ros2_setup = f"""
# ROS2 {distro.title()} Setup - Added by CLI Installer
source /opt/ros/{distro}/setup.bash
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=0
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
"""
        
        # Check if already exists
        try:
            with open(bashrc_path, 'r') as f:
                content = f.read()
                if f"source /opt/ros/{distro}/setup.bash" in content:
                    self.logger.info("ROS2 setup already exists in .bashrc")
                    return
        except FileNotFoundError:
            pass
        
        # Append ROS2 setup
        with open(bashrc_path, 'a') as f:
            f.write(ros2_setup)
        
        # Set proper ownership
        self._run_command(f"chown {original_user}:{original_user} {bashrc_path}", "Setting .bashrc ownership")
        
        self.installation_state['files_modified'].append(bashrc_path)
    
    def _verify_installation(self):
        """Verify ROS2 installation."""
        self.logger.info("✅ Verifying installation...")
        
        distro = self.config['installation']['ros_distro']
        
        # Check directories
        ros_path = f"/opt/ros/{distro}"
        if not os.path.exists(ros_path):
            raise InstallationError(f"ROS2 directory not found: {ros_path}")
        
        # Test ROS2 command
        setup_script = f"{ros_path}/setup.bash"
        test_command = f"bash -c 'source {setup_script} && ros2 --help'"
        
        try:
            self._run_command(test_command, "Testing ROS2 command", timeout=30)
        except Exception as e:
            raise InstallationError(f"ROS2 command test failed: {e}")
        
        # Check key packages
        key_packages = [f"ros-{distro}-ros2cli", "python3-rosdep", "python3-colcon-common-extensions"]
        for package in key_packages:
            result = subprocess.run(f"dpkg -l | grep {package}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"✓ Package verified: {package}")
            else:
                self.logger.warning(f"⚠️ Package not found: {package}")
        
        self.logger.info("✅ Installation verification completed successfully")

def create_arg_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="ROS2 Kilted Kaiju CLI Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 ros2_installer_cli.py
  sudo python3 ros2_installer_cli.py --config custom_config.yaml
  sudo python3 ros2_installer_cli.py --package-set base
  sudo python3 ros2_installer_cli.py --silent --log-level ERROR
  sudo python3 ros2_installer_cli.py --validate-only
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'ROS2 CLI Installer v{__version__}'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config_cli.yaml',
        help='Configuration file path (default: config_cli.yaml)'
    )
    
    parser.add_argument(
        '--package-set', '-p',
        choices=['minimal', 'base', 'desktop', 'desktop-full'],
        help='Package set to install (overrides config)'
    )
    
    parser.add_argument(
        '--ros-distro', '-d',
        choices=['kilted', 'jazzy', 'iron', 'humble', 'rolling'],
        help='ROS distribution (overrides config)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (overrides config)'
    )
    
    parser.add_argument(
        '--silent', '-s',
        action='store_true',
        help='Silent installation (no user interaction)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate system requirements'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate installation without making changes'
    )
    
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Display current configuration and exit'
    )
    
    parser.add_argument(
        '--parallel-jobs', '-j',
        type=int,
        help='Number of parallel jobs for installation'
    )
    
    return parser

def main():
    """Main entry point for the CLI installer."""
    parser = create_arg_parser()
    args = parser.parse_args()
    
    try:
        # Initialize installer
        installer = CLIInstaller(args.config)
        
        # Override config with command line arguments
        if args.package_set:
            installer.config['installation']['package_set'] = args.package_set
        if args.ros_distro:
            installer.config['installation']['ros_distro'] = args.ros_distro
        if args.log_level:
            installer.config['logging']['level'] = args.log_level
            installer.logger.setLevel(getattr(logging, args.log_level))
        if args.parallel_jobs:
            installer.config['installation']['parallel_jobs'] = args.parallel_jobs
        
        # Handle special modes
        if args.show_config:
            print("Current Configuration:")
            print(yaml.dump(installer.config, default_flow_style=False))
            sys.exit(0)
        
        if args.validate_only:
            installer.display_system_info()
            is_valid = installer.validate_system()
            sys.exit(0 if is_valid else 1)
        
        if args.dry_run:
            installer.logger.info("🧪 DRY RUN MODE - No changes will be made")
            installer.logger.info("System validation and configuration check only")
            installer.display_system_info()
            is_valid = installer.validate_system()
            if is_valid:
                installer.logger.info("✅ Dry run completed successfully")
            sys.exit(0 if is_valid else 1)
        
        # Run installation
        installer.logger.info("📟 Running CLI Installer...")
        result = installer.install_ros2(silent=args.silent)
        
        if result.success:
            installer.logger.info("🎉 Installation completed successfully!")
            installer.logger.info(f"📊 Summary: {result.packages_installed} packages installed in {result.duration:.2f} seconds")
            installer.logger.info(f"🆔 Session ID: {result.session_id}")
            if installer._is_docker_mode():
                installer.logger.info("\n🚀 ROS2 is ready via Docker!")
                installer.logger.info("   Open a new terminal and run: ros2")
                installer.logger.info("   Or run a ROS2 command: ros2 topic list")
            else:
                installer.logger.info("\n🚀 You can now use ROS2 commands in a new terminal session!")
                installer.logger.info("   Try: source ~/.bashrc && ros2 topic list")
            sys.exit(0)
        else:
            installer.logger.error("💥 Installation failed!")
            for error in result.errors:
                installer.logger.error(f"   • {error}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
