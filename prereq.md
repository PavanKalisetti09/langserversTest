pip install python-lsp-server

sudo apt update && sudo apt install jdtls -y

#installation of java lsp

Step 1: Install Java
Ensure you have Java installed on your system. You can install OpenJDK using the following command:
-- sudo apt update
-- sudo apt install openjdk-21-jdk -y

Step 2: Download JDT LS
You need to download the JDT LS package from the Eclipse website. You can do this using wget:
-- wget http://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz

Step 3: Extract the Package
Extract the downloaded package to a directory of your choice:
-- tar -xvzf jdt-language-server-latest.tar.gz -C ~/jdtls


Step 4: Configure JDT LS
You need to set up a script to run the JDT LS. Create a script file, for example, jdtls.sh, and add the following content:
-- nano ~/jdtls.sh
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

step 5 : test the installation
~/jdtls.sh /home/pavan/Documents/electrovolt/HackBench/web_exploitation/EV-05/application
