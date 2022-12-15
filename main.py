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
from pybricks.parameters import Port, Color
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
# Necessary movement to read the next tile
READTILE = 100
# Pickup item distance
PICKUPITEM = 160


# Initialize the motors.
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)
claw_motor = Motor(Port.C)
cannon_motor = Motor(Port.B)

distance_sensor = UltrasonicSensor(Port.S1)
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
            if gyro_sensor.angle() == 360 or gyro_sensor.angle() == -360:
                gyro_sensor.reset_angle(0)
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


"""
 ========================================
 Recognizement of items and ammunition
 ========================================
"""

def detectColor():
    return color_sensor.color()

def recognize():
    # The robot must move enough to read the color on the next tile
    # and return to the original place.

    # Then turn 90 degrees and read the next adjacent tile.
    adjacent_tiles = ["nothing", "nothing", "nothing", "nothing"]

    for index in range(len(adjacent_tiles)):
        # Move towards the tile to read it
        robot.straight(READTILE)
        time.sleep(1)

        # Correct the angle error
        fixAngle()
        time.sleep(1)

        # Detect which color the next tile is
        color = detectColor()

        print("Color: " + str(color))

        if color == Color.BLUE:
            # An item was found and saved in the array
            adjacent_tiles[index] = "item"
        elif color == Color.RED:
            # A piece of ammo was found and saved in the array
            adjacent_tiles[index] = "ammo"
        
        robot.straight(-READTILE)
        robot.turn(90)
        fixAngle()

    print(adjacent_tiles)



"""
 ========================================
 Claw Arm Movement
 ========================================
"""

def openClaw():
    claw_motor.run_until_stalled(200)

def closeClaw():
    claw_motor.run_until_stalled(-200)




"""
 ========================================
 Cannon Use and Movement
 ========================================
"""


def shootCannon():
    cannon_motor.run_target(90, 40)
    cannon_motor.run_target(90, 0)




"""
 ========================================
 Cannon Use and Movement
 ========================================
"""

def pickupItem():

    openClaw()
    robot.straight(PICKUPITEM)
    robot.turn(-30)
    closeClaw()
    robot.turn(30)
    robot.straight(NEXTTILE - PICKUPITEM)


"""
 ========================================
 Main Execution
 ========================================
"""

def main():

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

def test():

    pickupItem()
    

# Execute:

test()
