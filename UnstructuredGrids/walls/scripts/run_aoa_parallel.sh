#!/bin/bash

rm -rv ../aoasweepNREL1e5m10
mkdir ../aoasweepNREL1e5m10
for aoa in {-10..20..2}
do
    sbatch runcase.slurm $aoa
done