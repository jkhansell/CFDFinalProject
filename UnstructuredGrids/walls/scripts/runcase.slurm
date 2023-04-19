#!/bin/sh

#SBATCH --job-name=OFaoasweep
#SBATCH --partition=nu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=20
#SBATCH --time=24:00:00
#SBATCH --output=./outputs/output_%j.out
#SBATCH --error=./outputs/output_%j.err
#SBATCH --mail-user=jovillalobos@cenat.ac.cr
#SBATCH --mail-type=END,FAIL

cd $SLURM_SUBMIT_DIR 

source /home/jovillalobos/.bashrc
conda activate OFgmsh

python3 runcase_unstructured.py --scheme                                "steady"    \
                                --Reynolds                              4e5         \
                                --Tu                                    0.31        \
                                --nu                                    1.516e-5    \
                                --nuratio                               0.1         \
                                --aoa                                   $1          \
                                --c                                     0.45        \
                                --s                                     0.001       \
                                --rho                                   1.18        \
                                --nsteps                                5000        \
                                --airfoil  "../../../airfoils/NRELs826.txt"         \
                                --savepath "../aoasweep/"                           \
                                --meshcontrols "meshcontrols/Mesh8.json"            \