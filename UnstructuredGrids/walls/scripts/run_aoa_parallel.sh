#!/bin/bash

rm -rv ../aoasweep
mkdir ../aoasweep

for aoa in {-10..20..2}
do
    sbatch runcase.slurm $aoa
done