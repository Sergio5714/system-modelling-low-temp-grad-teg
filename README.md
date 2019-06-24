# Simulation of low temperature gradient thermoelectric generator.
This repository contains the script and an example for system modelling of the low temperature gradient thermoelectric generator (TEG). 

**Capabilities:**
The provided SW allows to calculate the output power of the generator, taking into account thermal design, thermoelectric phenomena and power conversion processes. 

**Who needs it:**
The script and numerical model can be directly used by the researchers and system engineers to evaluate the performance of the devices based on thermoelectric energy harvesting technology.

For the full system simulation the SW uses:
* Original theoretical model of thermal and thermoelectric processes in the TEG,
* A numerical model of [LTC3108 boost converter from Linear Technologies](https://www.analog.com/ru/products/ltc3108.html).

The examples provided in jupyter notebook [test.ipynb](https://github.com/Sergio5714/system-modelling-low-temp-grad-teg/blob/master/test.ipynb) demostrate the usage of the SW.

**Technical requirements to run the notebook:**
* python 3.6
* numpy 1.15.4
* scipy 1.2.1
* pickle
* matplotlib 3.0.2 (for visualization)
* [LaTeX](https://matplotlib.org/users/usetex.html) for text rendering (for visualization, optional)

**Visualization of the body heat energy harvesting simulation:**
![alt text](https://github.com/Sergio5714/system-modelling-low-temp-grad-teg/blob/master/simulation_body_heat_eh.svg)

