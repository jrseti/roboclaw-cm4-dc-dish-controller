#!/bin/sh
# Runs the USB port-power simulations with ngspice (brew install ngspice).
# Uses the 5 V buck model from ../power-5v. Results go to results/*.dat
# and *.log; plot.py turns them into PNGs.
set -e
cd "$(dirname "$0")"
mkdir -p results
# device input capacitance and U4 on-resistance (typ 65 m, max 135 m)
for c in "10u_typ 10u 65m" "47u_typ 47u 65m" "47u_max 47u 135m"; do
  set -- $c
  printf '.param CDEV=%s RDS=%s\n' "$2" "$3" > case.inc
  ngspice -b hotplug.cir < /dev/null > results/hotplug_$1.log 2>&1
  mv out.dat results/hotplug_$1.dat
done
printf '.param RDS=65m\n' > case.inc
ngspice -b short.cir < /dev/null > results/short.log 2>&1
mv out.dat results/short.dat
for c in "typ 65m" "max 135m"; do
  set -- $c
  printf '.param RDS=%s\n' "$2" > case.inc
  ngspice -b dcload.cir < /dev/null > results/dcload_$1.log 2>&1
  mv out.dat results/dcload_$1.dat
done
rm -f case.inc
grep -H -E '^[a-z0-9_]+ +=|^droop' results/*.log
grep -l -i -E 'too small|abort' results/*.log && echo "^^ check these logs" || true
