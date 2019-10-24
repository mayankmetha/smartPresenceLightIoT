# Smart Lit Classrooms - Presence Detector

The project is in multiple parts. Check the README files under each folder for relevant documentation <br>

## Setup
Common requirements: <br>
* Raspberry Pi 3b+
* PIR sensor, LEDs, LDR sensor
* Laptop (Ubuntu 18.04+)
* Python 3.6+
<br>

## Function

The Raspberry Pi runs the motion detector (PIR) and the light detector (LDR). Readings from both sensors are used to control the lighting in the room. <br>
If the PIR sensor triggers due to absence of motion, the Pi will make a REST call to a server to check the number of people in the room, and if the number returned is 0, then it will turn off the lights automatically. <br>
<br>
The user can monitor and controll the operation of the system from a web application run through a second server. The Raspberry Pi can return current status, such as number of lights switched on, current LDR reading etc. <br>
