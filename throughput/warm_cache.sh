#!/bin/bash
# S6863 warm_cache.sh
# warm_cache.sh: restore (default) or save the cloud build cache so a fresh container skips the JDK and NeoForge downloads.
# restore: source /mnt/project-files/tools/warm_cache.sh      (JDK 25 + ~/.gradle caches from a tarball on the shared folder; falls back to get_jdk25.sh)
# save:    bash warm_cache.sh save                             (run once after a successful moddev build; keeps one tarball per kind)
C=/mnt/project-files/cache; J=/tmp/claude-0/jdk25
if [ "$1" = save ]; then
  mkdir -p $C
  [ -x $J/bin/java ] && tar czf $C/jdk25.tgz.tmp -C $J . && mv $C/jdk25.tgz.tmp $C/jdk25.tgz
  [ -d ~/.gradle/caches ] && tar czf $C/gradle-home.tgz.tmp -C ~ .gradle/caches .gradle/wrapper && mv $C/gradle-home.tgz.tmp $C/gradle-home.tgz
  ls -la $C; exit 0
fi
[ -x $J/bin/java ] || { mkdir -p $J; [ -f $C/jdk25.tgz ] && tar xzf $C/jdk25.tgz -C $J; }
[ -d ~/.gradle/caches ] || { [ -f $C/gradle-home.tgz ] && tar xzf $C/gradle-home.tgz -C ~; }
[ -x $J/bin/java ] || source /mnt/project-files/tools/get_jdk25.sh
export JAVA_HOME=$J PATH=$J/bin:$PATH
