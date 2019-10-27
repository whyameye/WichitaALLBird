# WichitaALLBird
## Overview
- all python code is python 3 and was tested in ipython3
- testing:
```
	ipython3
	run serialTest.py
	run tests.py
	choosePort() # getting deprecated
```
## Definitions & Data
`WichitaALLStrands.json` is a key:value setup

**ring**: the outer-most is 1 and the inner 3.
**group**: left-most (west) is 1 and right-most is 3
**left**: ID of any strands adjacent to the left
**right**: ID of any strand adjacent to the right (from the direction of the outside looking into the center on circle/groups 1 and 3, and from the inside looking out on circle/group 2).

-  keys are strands (not birds)
- strands 0 and 25 are the two centers
- Statuses of strands:
	- 'dark birds': 14
	- 'active': 113
	- 'pending': 5
	- 'no birds': 12
	- 'disabled': 4 # due to malfunction
	- 'broken': 5
	
## Main Code
- main.py is the main program
- each sequence is a class.
     - there is no threading (I think)?

## Files
- **birds_sample.dat**: sample JSON file of strand key:value pairs
- **databaseExamples**: directory exploring Amazon database solution for communication between sensors and main computer
- **dtr**: reset Arduino using dtr line executable. Usage: `dtr <port>`
- **dtr.c**: reset Arduino using dtr line source code
- **__init__.py**: empty file so python source code can be imported as module
- **lisa.py**: code for original prototype
- **loadAllCode.sh**: load arduino source code into all Arduinos
- **loadCode.sh**: load arduino source code into 1 Arduino?
- **main.py**: main python code
- **README.md**: um...this file. ;)
- **resources**: directory of images etc. for reference
- **rPI_Info.txt**: Wi-Fi/Ethernet/MAC address info for every sensor
- **serialTest.py**: tests focused on low-level communication with Arduinos
- **tests.py**: tests focused on higher-level logic of bird paths etc.
- **WichitaALLStrands.json**: JSON file with most current data of strands.

## TODO
- add necessary parameters for mode 0
- convert mode 0 to be a json file and code reads the file
- have mode 0 actually work
    - don't worry about switching modes yet
    
### Mode changes
- replace startLed with random generation based on constraints in moves

# Current Status
- just wrote getStartLed. Not tested
- by writing getStartLed we defined what the datatype of an LED is: an array of 2 elements
- need to review list vs. array vs. tuple vs. object

