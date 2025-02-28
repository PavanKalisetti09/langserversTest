#!/bin/bash

set -e  # Exit on any error

# Directory to store language server binaries
INSTALL_DIR=~/language_servers/bin
mkdir -p "$INSTALL_DIR"

# Helper function to run commands and check success
run_command() {
    echo "Running: $1"
    if ! $1; then
        echo "Error executing: $1"
        exit 1
    fi
}

# Function to update PATH in ~/.bashrc if not already present
update_path() {
    if ! grep -q "$INSTALL_DIR" ~/.bashrc; then
        echo "Updating PATH in ~/.bashrc..."
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.bashrc
        source ~/.bashrc
    fi
}

# Install Python Language Server (pylsp)
install_python_ls() {
    echo "Installing Python Language Server (pylsp)..."
    run_command "sudo apt update"
    if ! command -v python3 > /dev/null 2>&1 || ! command -v pip3 > /dev/null 2>&1; then
        run_command "sudo apt install python3 python3-pip -y"
    fi
    # Update pip to ensure we have a recent version
    run_command "python3 -m pip install --upgrade pip"
    if apt-cache show python3-lsp-server > /dev/null 2>&1; then
        run_command "sudo apt install python3-lsp-server -y"
    else
        echo "python3-lsp-server not found in apt; installing via pip..."
        if pip3 install --help | grep -q "break-system-packages"; then
            run_command "pip3 install python-lsp-server --break-system-packages"
        else
            echo "--break-system-packages not supported; installing as user..."
            run_command "pip3 install python-lsp-server --user"
        fi
    fi
    PYLS_BIN=$(which pylsp)
    if [ -z "$PYLS_BIN" ]; then
        # If installed as user, look in ~/.local/bin
        PYLS_BIN="$HOME/.local/bin/pylsp"
    fi
    if [ -f "$PYLS_BIN" ]; then
        cp "$PYLS_BIN" "$INSTALL_DIR/pylsp"
        chmod +x "$INSTALL_DIR/pylsp"
        echo "Python Language Server installed at $INSTALL_DIR/pylsp"
    else
        echo "Error: pylsp binary not found after installation"
        exit 1
    fi
}

# Install Java Language Server (JDT LS)
install_java_ls() {
    echo "Installing Java Language Server (JDT LS)..."
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | grep "openjdk version \"21" || echo "")
    if [ -z "$JAVA_VERSION" ]; then
        echo "Java 21 not found; installing OpenJDK 21..."
        run_command "sudo apt update"
        run_command "sudo apt install software-properties-common -y"
        run_command "sudo add-apt-repository ppa:openjdk-r/ppa -y"
        run_command "sudo apt update"
        run_command "sudo apt install openjdk-21-jdk -y"
        JAVA_VERSION=$(java -version 2>&1 | head -n 1 | grep "openjdk version \"21" || echo "")
        if [ -z "$JAVA_VERSION" ]; then
            echo "Error: OpenJDK 21 not installed correctly after PPA addition"
            java -version 2>&1
            exit 1
        fi
    fi
    JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
    if [ ! -d "$JAVA_HOME" ] || [ ! -f "$JAVA_HOME/bin/java" ]; then
        JAVA_HOME=$(find /usr/lib/jvm -maxdepth 1 -type d -name "*java-21-openjdk*" | head -n 1)
        if [ -z "$JAVA_HOME" ] || [ ! -f "$JAVA_HOME/bin/java" ]; then
            echo "Error: Could not find valid JAVA_HOME for OpenJDK 21"
            exit 1
        fi
    fi
    echo "Using JAVA_HOME: $JAVA_HOME"
    JDTLS_DIR=~/language_servers/jdtls
    if [ ! -d "$JDTLS_DIR" ]; then
        mkdir -p "$JDTLS_DIR"
        if ! command -v wget > /dev/null 2>&1; then
            run_command "sudo apt install wget -y"
        fi
        echo "Downloading JDT LS archive..."
        run_command "wget -O /tmp/jdtls.tar.gz http://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz"
        if ! command -v tar > /dev/null 2>&1; then
            run_command "sudo apt install tar -y"
        fi
        echo "Extracting JDT LS archive..."
        run_command "tar -xvzf /tmp/jdtls.tar.gz -C $JDTLS_DIR"
        echo "Extraction completed."
        rm -f /tmp/jdtls.tar.gz
    else
        echo "JDT LS directory already exists, skipping download and extraction."
    fi
    echo "Creating jdtls.sh script..."
    cat > "$INSTALL_DIR/jdtls.sh" << EOF
#!/bin/bash
JAVA_HOME=$JAVA_HOME
JDTLS_HOME=~/language_servers/jdtls
\$JAVA_HOME/bin/java \\
  -Declipse.application=org.eclipse.jdt.ls.core.id1 \\
  -Dosgi.bundles.defaultStartLevel=4 \\
  -Declipse.product=org.eclipse.jdt.ls.core.product \\
  -Dlog.protocol=true \\
  -Dlog.level=ALL \\
  -Xms1g \\
  -Xmx2G \\
  -jar \$JDTLS_HOME/plugins/org.eclipse.equinox.launcher_*.jar \\
  -configuration \$JDTLS_HOME/config_linux \\
  -data "\$1"
EOF
    echo "Setting executable permissions..."
    chmod +x "$INSTALL_DIR/jdtls.sh"
    # Skipping test as requested
    # echo "Testing jdtls.sh..."
    # if ! timeout 30 "$INSTALL_DIR/jdtls.sh" /tmp > /tmp/jdtls_test.log 2>&1; then
    #     echo "Error: jdtls.sh failed to start or timed out after 30 seconds"
    #     cat /tmp/jdtls_test.log
    #     exit 1
    # fi
    echo "Java Language Server installed at $INSTALL_DIR/jdtls.sh"
}

# Install PHP Language Server (PHPActor)
install_php_ls() {
    echo "Installing PHP Language Server (PHPActor)..."
    if ! command -v php > /dev/null 2>&1; then
        run_command "sudo apt install php php-cli php-mbstring php-xml php-zip php-curl -y"
    fi
    if ! command -v composer > /dev/null 2>&1; then
        run_command "sudo apt install composer -y"
    fi
    TEMP_DIR=/tmp/phpactor
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    cat > composer.json << EOF
{
    "require": {
        "phpactor/phpactor": "^2024.0"
    },
    "minimum-stability": "dev",
    "prefer-stable": true
}
EOF
    run_command "composer install"
    cp vendor/bin/phpactor "$INSTALL_DIR/phpactor"
    cd -
    rm -rf "$TEMP_DIR"
    if [ ! -f "$INSTALL_DIR/phpactor" ]; then
        echo "Error: phpactor binary not found after installation"
        exit 1
    fi
    echo "PHP Language Server installed at $INSTALL_DIR/phpactor"
}

# Install JavaScript and TypeScript Language Server
install_js_ts_ls() {
    echo "Installing JavaScript and TypeScript Language Server..."
    NODE_VERSION=$(node -v 2>/dev/null | cut -d'v' -f2 || echo "0")
    NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d'.' -f1)
    if [ "$NODE_MAJOR" -lt 18 ]; then
        echo "Node.js version $NODE_VERSION is too old or not installed; installing Node.js 18..."
        run_command "sudo apt update"
        if command -v node > /dev/null 2>&1; then
            run_command "sudo apt remove nodejs npm -y"
        fi
        if ! command -v curl > /dev/null 2>&1; then
            run_command "sudo apt install curl -y"
        fi
        run_command "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
        run_command "sudo apt install nodejs -y"
    fi
    run_command "sudo npm install -g typescript-language-server typescript"
    # Use `which` or common paths to find the binary
    TSLS_BIN=$(which typescript-language-server)
    if [ -z "$TSLS_BIN" ]; then
        # Fallback to common locations
        TSLS_BIN="/usr/local/bin/typescript-language-server"
        if [ ! -f "$TSLS_BIN" ]; then
            TSLS_BIN="/usr/bin/typescript-language-server"
        fi
    fi
    if [ -f "$TSLS_BIN" ]; then
        cp "$TSLS_BIN" "$INSTALL_DIR/typescript-language-server"
        chmod +x "$INSTALL_DIR/typescript-language-server"
        echo "JavaScript and TypeScript Language Server installed at $INSTALL_DIR/typescript-language-server"
    else
        echo "Error: typescript-language-server binary not found in expected locations"
        echo "Attempted paths: $(npm root -g)/typescript-language-server/bin/typescript-language-server, /usr/local/bin/, /usr/bin/"
        exit 1
    fi
}

# Main installation function
install_all_language_servers() {
    install_python_ls
    install_java_ls
    install_php_ls
    install_js_ts_ls
    update_path
    echo "All language servers installed successfully!"
    echo "You can use them from anywhere by running: pylsp, jdtls.sh, phpactor, typescript-language-server"
}

# Run the installation
install_all_language_servers