class Ros2Installer < Formula
  desc "ROS2 CLI Installer - Install ROS2 on any system"
  homepage "https://github.com/neelashkannan/ROS2-Installer-CLI"
  url "https://github.com/neelashkannan/ROS2-Installer-CLI/releases/download/v2.1.0/release-v2.1.0.tar.gz"
  sha256 "ca648748b4162d86e6f0549efe439021d5dc644e46fff76a40bb4be7ae795f8b"
  license "MIT"
  version "2.1.0"

  depends_on "python@3"

  def install
    # Install the configuration file
    etc.install "config_cli.yaml" => "ros2-installer-config.yaml"

    # Install the actual Python script to prefix
    prefix.install "ros2_installer_cli.py"

    # Install Python dependencies into libexec
    python3 = "python3"
    system python3, "-m", "pip", "install",
           "--target=#{libexec}", "psutil", "PyYAML"

    # Create a wrapper script that sets up the Python path
    (bin/"ros2-installer").write <<~EOS
      #!/bin/bash
      export PYTHONPATH="#{libexec}:$PYTHONPATH"
      exec python3 "#{prefix}/ros2_installer_cli.py" "$@"
    EOS
    chmod 0755, bin/"ros2-installer"
  end

  test do
    system "#{bin}/ros2-installer", "--help"
    assert_match "v2.1.0", shell_output("#{bin}/ros2-installer --version")
    system "#{bin}/ros2-installer", "--show-config"
  end

  def caveats
    <<~EOS
      ROS2 Installer has been installed!

      Config: #{etc}/ros2-installer-config.yaml

      Usage:
        ros2-installer --help
        ros2-installer --validate-only
        ros2-installer --silent --ros-distro humble --package-set desktop

      On Ubuntu, use sudo. On macOS and other systems, Docker is used automatically.

      More info: https://github.com/neelashkannan/ROS2-Installer-CLI
    EOS
  end
end
