#!/bin/bash

experiment_name="experiments-2"
exp_num=1
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
results_dir="../$script_dir/results/$experiment_name"

mkdir -p "$results_dir/density" \
         "$results_dir/magnitude" \
         "$results_dir/extent" \
         "$results_dir/seperation"

mkdir -p "$results_dir/density/data" \
         "$results_dir/magnitude/data" \
         "$results_dir/extent/data" \
         "$results_dir/seperation/data"

mkdir -p "$results_dir/density/descriptions" \
         "$results_dir/magnitude/descriptions" \
         "$results_dir/extent/descriptions" \
         "$results_dir/seperation/descriptions"

# Varying density from 0.1 to 1.0 (step 0.1), magnitude=10, extent=20, seperation=3

for density in $(seq 0.1 0.1 1.0); do
    (cd "../$script_dir/src" && python3 main.py --size="medium" --density="$density" --magnitude=10 --extent=20 --seperation=3 -i=100 -o "$experiment_name/density/data/exp$exp_num" -de="$experiment_name/density/descriptions/exp$exp_num")
    ((exp_num++))
    echo "Density" $density "completed"
done

# Varying magnitude from 2 to 20 (step 1), density=0.7, extent=20, seperation=3
for magnitude in $(seq 2 2 20); do
    (cd "../$script_dir/src" && python3 main.py --size="medium" --density=0.7 --magnitude="$magnitude" --extent=20 --seperation=3 -i=100 -o "$experiment_name/magnitude/data/exp$exp_num" -de="$experiment_name/magnitude/descriptions/exp$exp_num")
    ((exp_num++))
    echo "Magnitude" $magnitude "completed"
done

# Varying extent from 5 to 50 (step 5), density=0.7, magnitude=10, seperation=3
for extent in $(seq 5 5 50); do
    (cd "../$script_dir/src" && python3 main.py --size="medium" --density=0.7 --magnitude=10 --extent="$extent" --seperation=3 -i=100 -o "$experiment_name/extent/data/exp$exp_num" -de="$experiment_name/extent/descriptions/exp$exp_num")
    ((exp_num++))
    echo "Extent" $extent "completed"
done

# Varying seperation from 2 to 10 (step 1), density=0.7, magnitude=10, extent=10
for seperation in $(seq 2 1 10); do
    (cd "../$script_dir/src" && python3 main.py --size="medium" --density=0.7 --magnitude=10 --extent=10 --seperation="$seperation" -i=100 -o "$experiment_name/seperation/exp$exp_num" -de="$experiment_name/seperation/descriptions/exp$exp_num")
    ((exp_num++))
    echo "seperation" $seperation "completed"
done
