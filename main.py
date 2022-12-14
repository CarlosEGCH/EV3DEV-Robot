#!/usr/bin/env pybricks-micropython

"""
Example LEGO® MINDSTORMS® EV3 Robot Educator Driving Base Program
-----------------------------------------------------------------

This program requires LEGO® EV3 MicroPython v2.0.
Download: https://education.lego.com/en-us/support/mindstorms-ev3/python-for-ev3

Building instructions can be found at:
https://education.lego.com/en-us/support/mindstorms-ev3/building-instructions#robot
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import TouchSensor, Motor, ColorSensor, GyroSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
import time

# Initialize the EV3 Brick.
ev3 = EV3Brick()

#Constants
UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0
MAX_AXE = 6
MIN_AXE = 1
MAX_STEPS = 2
# 1 tile to the next: 300
NEXTTILE = 300

# The following are the right measures
# robot = DriveBase(left_motor, right_motor, wheel_diameter=38, axle_track=200)

# Initialize the motors.
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)
#claw_motor = Motor(Port.B)
#gun_motor = Motor(Port.C)

#distance_sensor = UltrasonicSensor(Port.S3)
color_sensor = ColorSensor(Port.S2)
gyro_sensor = GyroSensor(Port.S3)
button = TouchSensor(Port.S4)

# Initialize the drive base.
robot = DriveBase(left_motor, right_motor, wheel_diameter=38, axle_track=200)
gyro_sensor.reset_angle(0)

#Initial Setup
current_degree = RIGHT
#           [X, Y]
axesXandY = [1, 1]
#               [     X     ,      Y     ]
# In the initial goal it could be the position of a piece 
goalAxesXandY = ['undefined', 'undefined']
# The danger that the SB has
danger = False

def fixAngle():

    currentAngle = abs(gyro_sensor.angle())

    print("Current: " + str(currentAngle))

    if(gyro_sensor.angle() < 0):
        fixedAngle = currentAngle%90 * -1
    else:
        fixedAngle = currentAngle%90
    if fixedAngle > 50:
        fixedAngle = 90 - fixedAngle
    elif fixedAngle < -50:
        fixedAngle = 90 - abs(fixedAngle) 

    print("Fixed: " + str(fixedAngle))

    while(1):
        if(fixedAngle > 0):
            robot.turn(-1)
            fixedAngle -= 1
        elif(fixedAngle < 0):
            robot.turn(1)
            fixedAngle += 1
        else:
            break

def smallestAngleBetween(currentAngle, goalAngle):
    a = currentAngle - goalAngle
    b = 360 - abs(currentAngle - goalAngle)
    return a if abs(a) < abs(b) else b

def updateAxes(goalAngle):
    global axesXandY
    if(goalAngle == UP and axesXandY[1] != MIN_AXE): axesXandY[1] -= 1
    elif(goalAngle == DOWN and axesXandY[1] != MAX_AXE): axesXandY[1] += 1
    elif(goalAngle == RIGHT and axesXandY[0] != MAX_AXE): axesXandY[0] += 1
    elif(goalAngle == LEFT and axesXandY[0] != MIN_AXE): axesXandY[0] -= 1

def newPosition(goalAngle):
    global current_degree
    #SB's rotation and movement
    robot.turn(smallestAngleBetween(current_degree, goalAngle))
    time.sleep(1)
    fixAngle()
    robot.straight(NEXTTILE)
    time.sleep(1)
    fixAngle()
    #Update the SB's direction and Axes
    current_degree = goalAngle
    updateAxes(goalAngle)
    return

def defineGoalAngle():
    global goalAxesXandY, axesXandY
    goal = None
    if goalAxesXandY[0] > axesXandY[0]:
        goal = RIGHT
    elif goalAxesXandY[0] < axesXandY[0]:
        goal = LEFT
    elif goalAxesXandY[1] > axesXandY[1]:
        goal = DOWN
    elif goalAxesXandY[1] < axesXandY[1]:
        goal = UP
    else:
        print("I'm here")
    return goal

def checkGoal():
    if goalAxesXandY == axesXandY:
        print("I'm here")
        return True
    return False

def movement():
    goal = 'siu'
    steps = 0
    while danger == False and steps < 2: 
        goal = defineGoalAngle()
        if goal is None:
            return False
        else:
            newPosition(goal)
            if checkGoal() == True:
                return False
        steps += 1
    return True

# while(1):

#     robot.straight(NEXTTILE)
#     #fixAngle()
#     robot.turn(-90)
#     #gyro_sensor.reset_angle(0)


goalAxesXandY = [6,6]
boolean = True
i = 0
gyro_sensor.reset_angle(0)
print("Initial Angle: " + str(gyro_sensor.angle()))

while(boolean):

    if(button.pressed()):
        time.sleep(2)
        print("Iteration: " + str(i))
        print("Initial Position: " + str(axesXandY))
        boolean = movement()
        print("Final Position: " + str(axesXandY))
        i += 1