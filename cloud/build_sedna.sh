#!/usr/bin/env bash
# Builds Ceres and Sedna (both MIT) from source with plain javac, because their Gradle builds need GitHub Packages auth.
# Usage: JAVA_HOME=<jdk 17+> tools/build_sedna.sh <work dir> <out dir>
set -euo pipefail
W=${1:?work dir}; O=${2:?out dir}; M=https://maven-central.storage-download.googleapis.com/maven2
mkdir -p "$W/libs" "$O"; cd "$W"
[ -d ceres ] || git clone -q https://github.com/fnuecke/ceres.git
[ -d sedna ] || git clone -q https://github.com/North-Western-Development/sedna.git
(cd ceres && git checkout -q e883ffe); (cd sedna && git checkout -q 8450eed)
# compile classpath only (the NeoForge game provides log4j; do not bundle it, 2.15.0 has known CVEs)
for a in org/ow2/asm/asm/9.1/asm-9.1 org/ow2/asm/asm-commons/9.1/asm-commons-9.1 org/ow2/asm/asm-tree/9.1/asm-tree-9.1 org/ow2/asm/asm-analysis/9.1/asm-analysis-9.1 com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2 org/jetbrains/annotations/24.1.0/annotations-24.1.0 commons-io/commons-io/2.11.0/commons-io-2.11.0 it/unimi/dsi/fastutil/8.5.6/fastutil-8.5.6 org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0 org/apache/logging/log4j/log4j-api/2.15.0/log4j-api-2.15.0 org/apache/logging/log4j/log4j-core/2.15.0/log4j-core-2.15.0; do
  curl -sfO --output-dir libs "$M/$a.jar"; done
CP=$(ls libs/*.jar | tr '\n' ':')
rm -rf out; mkdir -p out/ceres out/sedna
javac -nowarn --release 17 -cp "$CP" -d out/ceres $(find ceres/src/main/java -name '*.java')
jar cf "$O/ceres-0.0.4.jar" -C out/ceres .
javac -nowarn --release 17 -proc:none -cp "$CP:$O/ceres-0.0.4.jar" -d out/sedna $(find sedna/src/main/java -name '*.java')
cp -r sedna/src/main/resources/* out/sedna/
jar cf "$O/sedna-0.0.0.jar" -C out/sedna .
