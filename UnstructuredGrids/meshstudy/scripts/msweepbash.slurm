#!/bin/sh

#SBATCH --job-name=OFmeshsweep
#SBATCH --partition=nu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH --time=15:00:00
#SBATCH --output=output_%j.out
#SBATCH --error=output_%j.err
#SBATCH --mail-user=jovillalobos@cenat.ac.cr
#SBATCH --mail-type=END,FAIL

rm -r ../meshsweep
mkdir ../meshsweep

for file in `ls ./meshcontrols`
do
    echo Building $file directory file.
    echo 
    echo
    python3 runcase_unstructured.py --scheme "steady"\
                                    --Reynolds 1e5\
                                    --Tu 0.94\
                                    --nu 1.1516e-5\
                                    --nuratio .1\
                                    --aoa 0.0\
                                    --c 1\
                                    --s 0.001\
                                    --rho 1.18\
                                    --nsteps 4000\
                                    --airfoil  "../../../airfoils/NRELs826.txt"\
                                    --savepath "../meshsweep/"\
                                    --meshcontrols ./meshcontrols/$file    
    echo ------------------------------------------
done
