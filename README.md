# Pico ARM
This project is a fun demo made to control a robot arm that was 3D printed, is driven by servos and controlled by a raspberry pi pico W.

![Cover image](images/Cover.jpeg)

## Components
All of the parts of the actual robot are 3D printed.
The gripper contains a 180 degree servo that can be given commands to set itself to a precise angle.

The rest of the arm is driven by continuous motion servos that can only be given a speed and a direction.
NOTE: Be very careful when building this for yourself, as these servos can end up getting the arm's wires tangled if you drive the servos past certain boundaries. 

![Components view](images/Components.jpeg)

![Demo of prototype](images/Demo.mp4)

## Wiring
It is important that there is an external power supply connected to the curcuit (and wired up to a common ground with the pico). This is because driving this many servos at once is very demasnding and may end up drawing too much current from the pico and burning it out.

The servos are connected to the 16-channel PWM driver as follows
 - Channel 0: Base
 - Channel 2: Arm
 - Channel 4: Elbow
 - Channel 6: Gripper (This one is not a continuous motion servo)

The PWM driver is connected to the Pico as follows:
 - Pin 0 <-> SDA
 - Pin 1 <-> SCL
 - GND <-> GND
 - 3v3 <-> VCC

## The driver
There is a file called pca9685.py. This file acts as a driver for the servo control board, which communicated via I2C.
This driver is based on an old driver for the same board supplied by ADAFRUIT. The micropython version has been archived since 2018 in favour of the CircuitPython version.

## The Web Page
The arm can be controlled via a web page that will be served by the Pico W. Once you have connected the Pico W to your wifi, it will print its IP address to the serial console.
You can visit that IP address from any browser that is on the same local network as the pico W.

Altering the contents of control_page.html will not have any effect on the page that is served. That file only exists as a tool for testing and debugging. If you wish to alter the actual page, change the string literal in the main.py file.