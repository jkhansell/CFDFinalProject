#!/bin/bash

rm -rv ../meshsweep2
mkdir ../meshsweep2

for iMesh in `ls ./meshcontrols`
do
    sbatch msweepbash.slurm $iMesh
done