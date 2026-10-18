#!/bin/sh
# Runs the battery-input simulations with ngspice (brew install ngspice).
# Results go to results/*.dat and *.log; plot.py turns them into PNGs.
set -e
cd "$(dirname "$0")"
mkdir -p results
for c in "470u 40m" "47u 100m" "1p 1"; do
  set -- $c
  printf '.param CRC=%s ESRRC=%s\n' "$1" "$2" > case.inc
  ngspice -b hotplug.cir > results/hotplug_$1.log 2>&1
  mv out.dat results/hotplug_$1.dat
done
for i in 5 10; do
  printf '.param IREG=%s\n' "$i" > case.inc
  ngspice -b regen.cir > results/regen_${i}A.log 2>&1
  mv out.dat results/regen_${i}A.dat
done
for q in 0 1; do
  printf '.param QSHORT=%s\n' "$q" > case.inc
  ngspice -b reverse.cir > results/reverse_q1short$q.log 2>&1
  mv out.dat results/reverse_q1short$q.dat
done
rm -f case.inc
grep -H -E '^[a-z0-9_]+ +=' results/*.log
