import os
import subprocess
import shutil
import urllib.request
import tarfile
import json

# Helper function to run shell commands
def run_command(command, use_sudo=False):
    """Execute a shell command, optionally with sudo privileges."""
    if use_sudo:
        command = f"sudo {command}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing: {command}\n{result.stderr}")
        return False
    return True

# Helper function to check if a command exists
def command_exists(command):
    """Check if a command is available in the system's PATH."""
    return shutil.which(command) is not None

# Function to install Python Language Server
def install_python_ls():
    """Install the Python Language Server (pylsp)."""
    print("Installing Python Language Server...")
    if not command_exists("pylsp"):
        if run_command("pip install python-lsp-server"):
            print("Python Language Server installed successfully.")
        else:
            print("Failed to install Python Language Server.")
    else:
        print("Python Language Server is already installed.")

# Function to install Java Language Server (JDT LS)
def install_java_ls():
    """Install and configure the Java Language Server (JDT LS)."""
    print("Installing Java Language Server (JDT LS)...")
    # Step 1: Install Java
    if not command_exists("java"):
        run_command("apt update", use_sudo=True)
        run_command("apt install openjdk-21-jdk -y", use_sudo=True)
    # Step 2: Download JDT LS
    jdtls_url = "http://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz"
    jdtls_tar = "/tmp/jdt-language-server-latest.tar.gz"
    jdtls_dir = os.path.expanduser("~/jdtls")
    if not os.path.exists(jdtls_dir):
        os.makedirs(jdtls_dir, exist_ok=True)
    if not os.path.exists(jdtls_tar):
        print("Downloading JDT LS...")
        urllib.request.urlretrieve(jdtls_url, jdtls_tar)
    # Step 3: Extract the package
    with tarfile.open(jdtls_tar, "r:gz") as tar:
        tar.extractall(path=jdtls_dir)
    # Step 4: Configure JDT LS script
    jdtls_script = os.path.expanduser("~/jdtls.sh")
    with open(jdtls_script, "w") as f:
        f.write("""#!/bin/bash

JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
JDTLS_HOME=~/jdtls

$JAVA_HOME/bin/java \\
  -Declipse.application=org.eclipse.jdt.ls.core.id1 \\
  -Dosgi.bundles.defaultStartLevel=4 \\
  -Declipse.product=org.eclipse.jdt.ls.core.product \\
  -Dlog.protocol=true \\
  -Dlog.level=ALL \\
  -Xms1g \\
  -Xmx2G \\
  -jar $JDTLS_HOME/plugins/org.eclipse.equinox.launcher_*.jar \\
  -configuration $JDTLS_HOME/config_linux \\
  -data $1
""")
    run_command(f"chmod +x {jdtls_script}")
    print("Java Language Server installed successfully.")

# Function to install PHP Language Server
def install_php_ls():
    """Install and configure the PHP Language Server (PHPActor)."""
    print("Installing PHP Language Server...")
    # Step 1: Install PHP and dependencies
    if not command_exists("php"):
        run_command("apt update", use_sudo=True)
        run_command("apt install php -y", use_sudo=True)
        run_command("apt install php-cli php-mbstring php-xml php-zip php-curl -y", use_sudo=True)
    # Step 2: Install Composer
    if not command_exists("composer"):
        run_command("apt install composer -y", use_sudo=True)
    # Step 3: Configure Composer for PHPActor
    composer_json_path = os.path.expanduser("~/.config/composer/composer.json")
    os.makedirs(os.path.dirname(composer_json_path), exist_ok=True)
    with open(composer_json_path, "w") as f:
        json.dump({
            "require": {
                "phpactor/phpactor": "^2024.0"
            },
            "minimum-stability": "dev",
            "prefer-stable": True
        }, f, indent=4)
    run_command("composer global update")
    # Step 4: Update PATH in ~/.bashrc
    bashrc_path = os.path.expanduser("~/.bashrc")
    with open(bashrc_path, "a") as f:
        f.write('\nexport PATH="$HOME/.config/composer/vendor/bin:$PATH"\n')
    run_command("source ~/.bashrc")
    print("PHP Language Server installed successfully.")

# Function to install JavaScript and TypeScript Language Server
def install_js_ts_ls():
    """Install the TypeScript Language Server for JavaScript and TypeScript."""
    print("Installing JavaScript and TypeScript Language Server...")
    # Step 1: Install Node.js and npm
    if not command_exists("node"):
        run_command("apt update", use_sudo=True)
        run_command("apt install nodejs npm -y", use_sudo=True)
    # Step 2: Install TypeScript Language Server
    if not command_exists("typescript-language-server"):
        run_command("npm install -g typescript-language-server typescript", use_sudo=True)
    print("JavaScript and TypeScript Language Server installed successfully.")

# Main function to install all language servers
def install_all_language_servers():
    """Install all specified language servers sequentially."""
    install_python_ls()
    install_java_ls()
    install_php_ls()
    install_js_ts_ls()
    print("\nAll language servers have been installed successfully.")

# Run the installation
if __name__ == "__main__":
    install_all_language_servers()