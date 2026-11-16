#!/bin/sh
# Runs the battery-input simulations with ngspice (brew install ngspice).
# Results go to results/*.dat and *.log; plot.py turns them into PNGs.
set -e
cd "$(dirname "$0")"
mkdir -p results
# RF1: F1 cold resistance (4.5 mOhm) or 1e9 for an open F1.
for c in "470u 40m" "47u 100m" "1p 1"; do
  set -- $c
  printf '.param CRC=%s ESRRC=%s RF1=4.5m\n' "$1" "$2" > case.inc
  ngspice -b hotplug.cir > results/hotplug_$1.log 2>&1
  mv out.dat results/hotplug_$1.dat
done
for c in "5 4.5m" "10 4.5m" "5 1e9 _f1open" "10 1e9 _f1open"; do
  set -- $c
  printf '.param IREG=%s RF1=%s\n' "$1" "$2" > case.inc
  ngspice -b regen.cir > results/regen_$1A$3.log 2>&1
  mv out.dat results/regen_$1A$3.dat
done
for c in "0 4.5m" "1 4.5m" "1 1e9 _f1open"; do
  set -- $c
  printf '.param QSHORT=%s RF1=%s\n' "$1" "$2" > case.inc
  ngspice -b reverse.cir > results/reverse_q1short$1$3.log 2>&1
  mv out.dat results/reverse_q1short$1$3.dat
done
rm -f case.inc
grep -H -E '^[a-z0-9_]+ +=' results/*.log
