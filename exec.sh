#!/bin/bash



# Run MPI executions for each input file
for i in {0..49}
do
    echo "Running simulation $i..."
    mpiexec -n 5 python ./main.py "./inputs/randomInput$i.txt" "./outputs/randomOutput$i.txt"
done

echo "All simulations completed!"