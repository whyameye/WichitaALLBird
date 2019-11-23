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
## Definitions
`WichitaALLStrands.json` is a key:value setup

- **ring**: the outer-most is 1 and the inner 3.
- **group**: left-most (west) is 1 and right-most is 3
- **left**: ID of any strands adjacent to the left
- **right**: ID of any strand adjacent to the right (from the direction of the outside looking into the center on circle/groups 1 and 3, and from the inside looking out on circle/group 2).

- keys are strands (not birds)
- strands 0 and 25 are the two centers
- Statuses of strands:
	- 'dark birds': 14
	- 'active': 113
	- 'pending': 5
	- 'no birds': 12
	- 'disabled': 4 # due to malfunction
	- 'broken': 5

## Hardware
- 10 Arduinos (aka Servers) numbered 0 through 9
- up to 18 strands on an Arduino numbered 0 through 17

## Data
### Variables
 - active LED is a list of 3: [strand #, index of Y element in strand, T/F active]
  - LEDs in sequence include time: [[strand #, index of Y element in strand, T/F active], abs time]
 - serverLedLists is an array of arrays with each index to the parent array representing a server ID
    - The child arrays are lists of LEDs to change of the form [<strand #>, <numOnStrand>, <color>, <amplitude>]
    - strand #: uint8
    - numOnStrand: uint8
    - color: uint8
    - amplitude: uint8
### Sending colors to LEDS
- open serial ports in main thread
- spin off threads, one for each port, and send LEDs
- join threads, rinse and repeat
- this would require the LEDs to be sorted by Arduino in the main thread

## Main Code
- main.py is the main program
- each sequence is an instance of a class.
  - there is no threading in the class or instances

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

# Incomplete
- no code currently to return to default mode after specified amount of time (commented out in code)

# Current Status



## 16-Nov-2019
- TODO: test if colors of LEDs are really changing
- TODO: try mode change
- TODO: add code mapping Arduino IDs to Serial ports

## 14-Nov-2019
- sequence *appears* to generate but is not fully verified
- deleting LEDs doesn't seem to be working correctly
- sequences are never deleted/regenerated
- currently digging in at the `update()` code where the try/except clause is
