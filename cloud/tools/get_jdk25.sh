#!/bin/bash
# S0310 Installs Temurin JDK 25 in the cloud container and sets JAVA_HOME (needed to compile NeoForge 26.1.2 mods)
# Installs Temurin JDK 25 into /tmp/claude-0/jdk25 (cloud container, via the proxy) and prints how to use it.
# Usage: source /mnt/project-files/tools/get_jdk25.sh   (sets JAVA_HOME and PATH)
# Gradle (NeoForge moddev, languageVersion 25): ./gradlew compileJava --no-daemon -q -Porg.gradle.java.installations.paths=$JAVA_HOME
# First moddev build downloads Minecraft/NeoForge (~3 min); later builds are fast. Run modules one at a time or 3 in parallel.
D=/tmp/claude-0/jdk25
if [ ! -x $D/bin/java ]; then
  mkdir -p $D && curl -sL "https://api.adoptium.net/v3/binary/latest/25/ga/linux/x64/jdk/hotspot/normal/eclipse" | tar xz -C $D --strip-components=1
fi
export JAVA_HOME=$D PATH=$D/bin:$PATH
java -version 2>&1 | grep -v Picked | head -1
