#!/bin/bash

# Navigate to the variant directory if not already there
cd /home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/nozzle_variants_v3

echo "Submitting all Condor jobs for nozzle variants..."

# Use find with null separation to handle spaces and avoid prefix duplication
find . -type f -name "nozzle_sim.submit" -print0 | while IFS= read -r -d '' submit_file; do
  echo "Submitting: $submit_file"
  if ! condor_submit "$submit_file"; then
    echo "Failed to submit: $submit_file"
  fi
done

echo "All available jobs have been submitted."