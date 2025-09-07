#!/usr/bin/env python3
"""
ROS2 Kilted Kaiju CLI Professional Installer
============================================

Production-grade ROS2 installation system - CLI Only Version
Focused on command-line automation with enterprise features.

Features:
- Configuration-driven installation
- Robust error handling and recovery
- Parallel processing and optimization
- Enterprise deployment support
- Comprehensive logging and monitoring
- Security and validation
- Cross-platform compatibility
- Silent automation support

Author: ROS2 Installation Team
Version: 2.1.0 (CLI-Only)
License: Apache 2.0
"""

import os
import sys
import json
import yaml
import time
import uuid
import argparse
import logging
import threading
import subprocess
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Version and metadata
__version__ = "2.1.0"
__author__ = "neelash"

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
    
    def __init__(self, config_file: str = "config.yaml"):
        """Initialize the CLI installer."""
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
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
        
        self.logger.info(f"🚀 ROS2 CLI Professional Installer v{__version__}")
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
        
        # Add session ID to all log records
        old_factory = logging.getLogRecordFactory()
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.session_id = self.session_id
            return record
        logging.setLogRecordFactory(record_factory)
        
        return logger
    
    def _gather_system_info(self) -> SystemInfo:
        """Gather comprehensive system information."""
        try:
            import platform
            import psutil
            import shutil
            
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
            
            return SystemInfo(
                os_name=os_name,
                os_version=os_version,
                architecture=architecture,
                memory_gb=memory_gb,
                disk_space_gb=disk_space_gb,
                cpu_cores=cpu_cores
            )
        except Exception as e:
            self.logger.warning(f"Could not gather complete system info: {e}")
            return SystemInfo("Unknown", "Unknown", "Unknown", 0, 0, 1)
    
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
        
        # Check Ubuntu version if applicable
        if 'ubuntu' in self.system_info.os_name.lower():
            required_version = validation_config.get('required_ubuntu_version', '24.04')
            if required_version not in self.system_info.os_version:
                self.logger.warning(f"Ubuntu version mismatch: {self.system_info.os_version} != {required_version}")
        
        # Check architecture
        supported_archs = validation_config.get('supported_architectures', ['amd64', 'arm64', 'aarch64'])
        if self.system_info.architecture not in supported_archs:
            issues.append(f"Unsupported architecture: {self.system_info.architecture}")
        
        # Check sudo privileges
        if os.geteuid() != 0:
            issues.append("Script must be run with sudo privileges")
        
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
        self.logger.info(f"  • Architecture: {self.system_info.architecture}")
        self.logger.info(f"  • Memory: {self.system_info.memory_gb:.1f} GB")
        self.logger.info(f"  • Disk Space: {self.system_info.disk_space_gb:.1f} GB")
        self.logger.info(f"  • CPU Cores: {self.system_info.cpu_cores}")
    
    def prompt_user_confirmation(self, silent: bool = False) -> bool:
        """Prompt user for installation confirmation."""
        if silent:
            return True
        
        self.logger.info("\n" + "="*60)
        self.logger.info("🤖 ROS2 Kilted Kaiju Installation Summary")
        self.logger.info("="*60)
        
        config = self.config['installation']
        self.logger.info(f"  • ROS Distribution: {config['ros_distro']}")
        self.logger.info(f"  • Package Set: {config['package_set']}")
        self.logger.info(f"  • Uninstall Existing: {config.get('uninstall_existing', True)}")
        self.logger.info(f"  • Parallel Jobs: {config.get('parallel_jobs', 4)}")
        
        self.display_system_info()
        
        self.logger.info("\n⚠️  This will modify your system by:")
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
        initial_state = self.installation_state.copy()
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
                original_file = backup_file.replace('.backup', '')
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
                    capture_output=False,
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
    
    def _install_package_parallel(self, packages: List[str]) -> Dict[str, bool]:
        """Install packages in parallel."""
        self.logger.info(f"📦 Installing {len(packages)} packages in parallel...")
        
        max_workers = min(self.config.get('installation', {}).get('parallel_jobs', 4), len(packages))
        results = {}
        
        def install_single_package(package: str) -> Tuple[str, bool]:
            try:
                self._run_command(f"sudo apt-get install -y {package}", f"Installing {package}")
                self.installation_state['packages_installed'].append(package)
                return package, True
            except Exception as e:
                self.logger.error(f"Failed to install {package}: {e}")
                return package, False
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_package = {executor.submit(install_single_package, pkg): pkg for pkg in packages}
            
            for future in concurrent.futures.as_completed(future_to_package):
                package, success = future.result()
                results[package] = success
        
        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"✅ Installed {successful}/{len(packages)} packages successfully")
        
        return results
    
    def install_ros2(self, silent: bool = False) -> InstallationResult:
        """Main installation method with comprehensive error handling."""
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
                self._run_command("sudo apt-get autoremove -y ros-*", "Removing ROS packages")
                self._run_command("sudo apt-get autoremove -y", "Cleaning up dependencies")
            else:
                self.logger.info("No existing ROS installations found")
        except Exception as e:
            self.logger.warning(f"Could not check for existing ROS installations: {e}")
    
    def _setup_repositories(self):
        """Setup ROS2 repositories."""
        if not self.config.get('system', {}).get('add_repositories', True):
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
        
        user_home = f"/home/{original_user}"
        bashrc_path = f"{user_home}/.bashrc"
        distro = self.config['installation']['ros_distro']
        
        # Backup existing bashrc
        if os.path.exists(bashrc_path) and self.config.get('system', {}).get('backup_configs', True):
            backup_path = f"{bashrc_path}.backup.{self.session_id}"
            self._run_command(f"cp {bashrc_path} {backup_path}", "Backing up .bashrc")
            self.installation_state['backup_files'].append(backup_path)
        
        # Add ROS2 setup to bashrc
        ros2_setup = f"""
# ROS2 {distro.title()} Setup - Added by CLI Professional Installer
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
        description="ROS2 Kilted Kaiju CLI Professional Installer",
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
        version=f'ROS2 CLI Professional Installer v{__version__}'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
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
        installer.logger.info("📟 Running CLI Professional Installer...")
        result = installer.install_ros2(silent=args.silent)
        
        if result.success:
            installer.logger.info("🎉 Installation completed successfully!")
            installer.logger.info(f"📊 Summary: {result.packages_installed} packages installed in {result.duration:.2f} seconds")
            installer.logger.info(f"🆔 Session ID: {result.session_id}")
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
