## MCNozzleWork
This repository has everything you need to modify nozzle geometry, run a a simulation with the new geometry, and analyze the data.

The work flow is as followed:

# Geometry
* Head into geometries/MuColl_10TeV_v0A_Modded_Nozzle
* Find a Nozzle.xml file and either copy and edit a new one, or edit an existing one
    * make sure to name it something that makes sense, preferably in line with the versions ahead of it
* Copy or edit a MuCol_T0TeV.xml file
    * add the new nozel.xml file to it
* now run the geoConverter command in terminal to render the geometry as a .root file for veiwing purpose
    * $ geoConverter -compact2tgeo -input "MuCol_xyz.xml" -output "file/name.root"
    * if you're using VSCode, I recommend the "Root Veiwer" extension.

# Simulation
* Head into steeringFiles
* Copy and edit a new steer_sim_Hbb.py
* Change the input.xml file to 
* Run the simulaiton with 
    * $ ddsim --steeringFile "steer_sim_Hbb_x.py" > sim.log 2>&1
* This will generate a sim.log text file that provides information simulation time information at the end of the file

# Analysis
* There are multiple python scripts to run with
    * $ python path/to/file
* These will produce some graphs of some valuable information