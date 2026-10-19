#!/bin/sh
# Runs the power-sheet simulations with ngspice (brew install ngspice).
# Results go to results/*.dat and *.log; plot.py turns them into PNGs.
set -e
cd "$(dirname "$0")"
mkdir -p results
ngspice -b startup.cir > results/startup.log 2>&1
mv out.dat results/startup.dat
# QSOFT=1: board as built (slow Q2 turn-on); QSOFT=0: the earlier design
for q in 1 0; do
  printf '.param QSOFT=%s\n' "$q" > case.inc
  ngspice -b ovp.cir > results/ovp_soft$q.log 2>&1
  mv out.dat results/ovp_soft$q.dat
done
for q in 0 1; do
  printf '.param QSOFT=%s\n' "$q" > case.inc
  ngspice -b sw1.cir > results/sw1_soft$q.log 2>&1
  mv out.dat results/sw1_soft$q.dat
done
for v in 12.8 12.0 11.4; do
  printf '.param VB=%s QSOFT=1\n' "$v" > case.inc
  ngspice -b brownout.cir > results/brownout_$v.log 2>&1
  mv out.dat results/brownout_$v.dat
done
rm -f case.inc
grep -H -E '^[a-z0-9_]+ +=' results/*.log
grep -l -i -E 'too small|abort' results/*.log && echo "^^ check these logs" || true
