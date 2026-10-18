#!/bin/sh
# Runs the 5 V buck simulations with ngspice (brew install ngspice).
# Results go to results/*.dat and *.log; plot.py turns them into PNGs.
set -e
cd "$(dirname "$0")"
mkdir -p results
ngspice -b startup.cir > results/startup.log 2>&1
mv out.dat results/startup.dat
# 2.5 A and 1 A steps as built (C46, C55 not fitted); 2.5 A with C46 470 pF fitted
for c in "2.5A_built 2.5 1f" "1A_built 1 1f" "2.5A_c46 2.5 470p"; do
  set -- $c
  printf '.param IST=%s C46=%s C55=1f\n' "$2" "$3" > case.inc
  ngspice -b loadstep.cir > results/loadstep_$1.log 2>&1
  mv out.dat results/loadstep_$1.dat
done
for c in "0.5A_built 10.3 1f" "3A_built 1.72 1f" "3A_c46 1.72 470p"; do
  set -- $c
  printf '.param RL=%s C46=%s C55=1f\n' "$2" "$3" > case.inc
  ngspice -b loop.cir > results/loop_$1.log 2>&1
  mv out.dat results/loop_$1.dat
done
for v in 10 12.6 17; do
  printf '.param VIN=%s\n' "$v" > case.inc
  ngspice -b ripple.cir > results/ripple_$v.log 2>&1
  mv out.dat results/ripple_$v.dat
done
rm -f case.inc
grep -H -E '^[a-z0-9_]+ +=' results/*.log
grep -l -i -E 'too small|abort' results/*.log && echo "^^ check these logs" || true
