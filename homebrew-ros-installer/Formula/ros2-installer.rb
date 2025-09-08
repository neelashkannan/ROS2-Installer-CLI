class Ros2Installer < Formula
  desc "ROS2 Kilted Kaiju CLI Installer - Production-grade ROS2 installation tool"
  homepage "https://github.com/neelashkannan/ROS2-Installer-CLI"
  url "https://github.com/neelashkannan/ROS2-Installer-CLI/releases/download/v2.1.0/release-v2.1.0.tar.gz"
  sha256 "ca648748b4162d86e6f0549efe439021d5dc644e46fff76a40bb4be7ae795f8b"
  license "MIT"
  version "2.1.0"

  depends_on "python@3.11"

  def install
    # Install the main script
    bin.install "ros2_installer_cli.py" => "ros2-installer"
    
    # Install the configuration file
    etc.install "config_cli.yaml" => "ros2-installer-config.yaml"
    
    # Make the script executable
    chmod 0755, bin/"ros2-installer"
    
    # Install Python dependencies
    system Formula["python@3.11"].opt_bin/"pip3", "install", 
           "--target=#{libexec}", "psutil", "PyYAML"
    
    # Create a wrapper script that sets up the Python path
    (bin/"ros2-installer").write <<~EOS
      #!/bin/bash
      export PYTHONPATH="#{libexec}:$PYTHONPATH"
      exec "#{Formula["python@3.11"].opt_bin}/python3" "#{prefix}/ros2_installer_cli.py" "$@"
    EOS
    
    # Install the actual Python script to prefix
    prefix.install "ros2_installer_cli.py"
  end

  test do
    # Test that the script can be executed and shows help
    system "#{bin}/ros2-installer", "--help"
    
    # Test version flag
    assert_match "v2.1.0", shell_output("#{bin}/ros2-installer --version")
    
    # Test config validation
    system "#{bin}/ros2-installer", "--show-config"
  end

  def caveats
    <<~EOS
      🤖 ROS2 Installer has been installed!
      
      Configuration file installed to: #{etc}/ros2-installer-config.yaml
      
      Usage:
        # Show help
        ros2-installer --help
        
        # Validate system requirements only
        sudo ros2-installer --validate-only
        
        # Install ROS2 with custom config
        sudo ros2-installer --config #{etc}/ros2-installer-config.yaml
        
        # Silent installation
        sudo ros2-installer --silent
      
      Note: This installer requires sudo privileges to install ROS2 packages.
      
      For more information, visit: https://github.com/neelashkannan/ROS2-Installer-CLI
    EOS
  end
end
