#!/bin/bash

exp_num=1

# Varying density from 0.1 to 1.0 (step 0.1), magnitude=10, extent=20, correlation=3

# for density in $(seq 0.1 0.1 1.0); do
    python3 main.py --size="medium" --density="$density" --magnitude=10 --extent=20 --correlation=3 -i=50 -o "exp$exp_num"
    ((exp_num++))
    echo "Density" $density "completed"
# done

# Varying magnitude from 2 to 20 (step 1), density=0.7, extent=20, correlation=3
for magnitude in $(seq 2 2 20); do
    python3 main.py --size="medium" --density=0.7 --magnitude="$magnitude" --extent=20 --correlation=3 -i=50 -o "exp$exp_num"
    ((exp_num++))
    echo "Magnitude" $magnitude "completed"
# done

# Varying extent from 5 to 50 (step 5), density=0.7, magnitude=10, correlation=3
for extent in $(seq 5 5 50); do
    python3 main.py --size="medium" --density=0.7 --magnitude=10 --extent="$extent" --correlation=3 -i=50 -o "exp$exp_num"
    ((exp_num++))
    echo "Extent" $extent "completed"
done

# Varying correlation from 2 to 10 (step 1), density=0.7, magnitude=10, extent=10
for correlation in $(seq 2 1 10); do
    python3 main.py --size="medium" --density=0.7 --magnitude=10 --extent=10 --correlation="$correlation" -i=50 -o "exp$exp_num"
    ((exp_num++))
    echo "Correlation" $correlation "completed"
done