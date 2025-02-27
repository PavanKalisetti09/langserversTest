# Python Language Server Installation
To install the Python Language Server (pylsp), run the following command:

```sh
pip install python-lsp-server
```

---

# Java Language Server Installation (JDT LS)

## Step 1: Install Java
Ensure you have Java installed on your system. You can install OpenJDK using the following commands:

```sh
sudo apt update
sudo apt install openjdk-21-jdk -y
```

## Step 2: Download JDT LS
Download the latest JDT LS package from the Eclipse website using `wget`:

```sh
wget http://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz
```

## Step 3: Extract the Package
Extract the downloaded package to a directory of your choice:

```sh
tar -xvzf jdt-language-server-latest.tar.gz -C ~/jdtls
```

## Step 4: Configure JDT LS
Set up a script to run JDT LS. Create a script file (`jdtls.sh`) and add the following content:

```sh
nano ~/jdtls.sh
```

Paste the following script into the file:

```sh
#!/bin/bash

JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
JDTLS_HOME=~/jdtls

$JAVA_HOME/bin/java \
  -Declipse.application=org.eclipse.jdt.ls.core.id1 \
  -Dosgi.bundles.defaultStartLevel=4 \
  -Declipse.product=org.eclipse.jdt.ls.core.product \
  -Dlog.protocol=true \
  -Dlog.level=ALL \
  -Xms1g \
  -Xmx2G \
  -jar $JDTLS_HOME/plugins/org.eclipse.equinox.launcher_*.jar \
  -configuration $JDTLS_HOME/config_linux \
  -data $1
```

Save and exit (`CTRL + X`, then `Y`, then `ENTER`).

Make the script executable:

```sh
chmod +x ~/jdtls.sh
```

## Step 5: Test the Installation
Run the script with your workspace directory:

```sh
~/jdtls.sh /home/pavan/Documents/electrovolt/HackBench/web_exploitation/EV-05/application
```

If everything is set up correctly, the Java Language Server should start successfully.

---

# PHP Language Server Installation

## Step 1: Install PHP
Ensure you have PHP installed on your system:

```sh
sudo apt update
sudo apt install php -y
sudo apt install php-cli php-mbstring php-xml php-zip php-curl -y
```

## Step 2: Install Composer and PHPActor
Install Composer and the PHPActor language server:

```sh
sudo apt install composer -y
composer global require phpactor/phpactor:^2024.0
```

## Step 3: Configure Composer
Edit the Composer configuration file:

```sh
nano ~/.config/composer/composer.json
```

Add the following content:

```json
{
    "require": {
        "phpactor/phpactor": "^2024.0"
    },
    "minimum-stability": "dev",
    "prefer-stable": true
}
```

Update Composer:

```sh
composer global update
```

## Step 4: Set Up PATH
Check your `PATH`:

```sh
echo $PATH
```

If the path is not found, add the following to `~/.bashrc`:

```sh
nano ~/.bashrc
```

Append this line to the end of the file:

```sh
export PATH="$HOME/.config/composer/vendor/bin:$PATH"
```

Reload the bash configuration:

```sh
source ~/.bashrc
```

## Step 5: Test the Installation
Check if PHPActor is installed:

```sh
phpactor --version
```

Check if the PHP language server is working:

```sh
phpactor language-server --version
```

