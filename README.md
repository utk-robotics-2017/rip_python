#UTK IEEE General Robot Platform

Welcome to the general robot platform for the University of Tennessee IEEE Robotics Team. This will provide a framework for small (typically < 1 cubic foot) autonomous robots based primarily off of standard off the shelf parts. The framework will be organized, extendable, flexible, and well documented. 

The goal is to provide a stable platform for future robots developed by the UTK IEEE Robotics Team and others. 

##Getting Started

First, you should clone this repository and obtain the submodules. To get all of the submodules, run  ```git pull && git submodule init && git submodule update``` from the root of the repository.

Next, you will want to determine the peripherals and microcontroller(s) being used. With this information, you can prepare a configuration file for ArduinoGen to generate the microcontroller code. This configuration also provides the necessary information for the Python interface in torso.

##Basic Structure
- **Docs** - Documentation and basic research information about robotics. The goal is to provide a knowledge base of relevant information.
- **Head** - Code running on the Raspberry Pi (or compariable) board. This is the higher level Python code which coordinates everything and performs any intensive processing tasks. 
- **Torso** - Code running on microcontrollers (Arduino/Teensy). This code handles the actual reading of sensors and control of motors, servos, etc. 
- **Utils** - Utilities to aid in the calibration and testing of code and components. 

##Included Packages
- TBD

##Standard Supported Hardware
###Microprocessor and Microcontroller Boards
- Raspberry Pi 3 B+
- BeagleBone Black
- Arduino Uno R3
- Arduino Mega 2560

###Sensors
- GPIO Encoders
- I2C Encoders
- Analog Line Sensors (Individual & Array)
- Digital Line Sensors (Individual & Array)
- Ultrasonic Rangefinders
- navX IMU (Accelerometer, Gyroscope, Magnetometer)

###Motor Controllers
- SparkFun Monster Moto Shield

###Misc Hardware
- Servos
- Lynxmotion AL5D Arm

###Drivetrain Configurations
- Mecanum
- Tank Drive

Related Repos:
|       Repo       |
____________________
|[ArduinoGen](https://github.com/utk-robotics-2016/ArduinoGen)|
|[ArduinoGen Web GUI](https://github.com/utk-robotics-2016/utk-robotics-2016.github.io)|
|[Pathfinder](https://github.com/utk-robotics-2016/Pathfinder)|
|[NAVX](https://github.com/utk-robotics-2016/navxmxp)|
|[2016 Robot Code](https://github.com/utk-robotics-2016/utk-robotics-2016)|
