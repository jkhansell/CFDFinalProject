#!/bin/bash

for i in {1..4}
do
    echo $i
    python3 angleplotsNREL.py ../aoasweepNREL"$i"e5 "$i"00k
    python3 angleplotsNREL_reduced.py ../aoasweepNREL"$i"e5 "$i"00k
done