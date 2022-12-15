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
import random

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
# It is an array of goals where the first element has the bigger priority
goalAxesXandY = []
# The danger that the SB has. Possible values are "0", "1", "2"
danger = 0

"""
 ========================================
    Add a new goal in the first position
 ========================================
"""

def addGoal(goal):
    global goalAxesXandY
    goalAxesXandY.insert(0,goal)

"""
 ========================================
    Deletes a goal when achieved
 ========================================
"""

def goalAchieved(goal):
    try:
        global goalAxesXandY
        goalAxesXandY.remove(goal)
        return True
    except ValueError:
        return False

"""
 ========================================
    Fixes teh angle
 ========================================
"""

def fixAngle():

    currentAngle = abs(gyro_sensor.angle())

    print("Current: " + str(currentAngle))

    if(gyro_sensor.angle() < 0):
        fixedAngle = currentAngle%90 * -1
    else:
        fixedAngle = currentAngle%90
    if fixedAngle > 50:
        fixedAngle = fixedAngle - 90
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

"""
 ========================================
    Return the smallest angle to see if the SB moves left or right
 ========================================
"""

def smallestAngleBetween(currentAngle, goalAngle):
    a = currentAngle - goalAngle
    b = 360 - abs(currentAngle - goalAngle)
    return a if abs(a) < abs(b) else b

"""
 ========================================
    Update the SB's axes
 ========================================
"""

def updateAxes(goalAngle):
    global axesXandY
    if(goalAngle == UP and axesXandY[1] != MIN_AXE): axesXandY[1] -= 1
    elif(goalAngle == DOWN and axesXandY[1] != MAX_AXE): axesXandY[1] += 1
    elif(goalAngle == RIGHT and axesXandY[0] != MAX_AXE): axesXandY[0] += 1
    elif(goalAngle == LEFT and axesXandY[0] != MIN_AXE): axesXandY[0] -= 1

"""
 ========================================
    Move the bot in the respective direction and spin
 ========================================
"""

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

"""
 ========================================
 Defines the path to be taken by the SB
 ========================================
"""

def defineGoalAngle():
    global goalAxesXandY, axesXandY, lastMovement
    goal = []
    decision = None
    if goalAxesXandY == []:
        removeGoal = None
        if lastMovement == RIGHT:
            removeGoal = LEFT
        elif lastMovement == LEFT:
            removeGoal = RIGHT
        elif lastMovement == UP:
            removeGoal = DOWN
        elif lastMovement == DOWN:
            removeGoal = UP
        goal.append(RIGHT, LEFT, DOWN, UP)
        goal.remove(removeGoal)
    if goalAxesXandY[0][0] > axesXandY[0]:
        goal.append(RIGHT)
    if goalAxesXandY[0][0] < axesXandY[0]:
        goal.append(LEFT)
    if goalAxesXandY[0][1] > axesXandY[1]:
        goal.append(DOWN)
    if goalAxesXandY[0][1] < axesXandY[1]:
        goal.append(UP)
    # else:
    #     print("I'm here")
    if goal != []:
        # while (1):
        #     if len(goal) == 1:
        #         return goal[0]
        decision = random.choice(goal)
        lastMovement = decision
            # if checkDecision == True:
            #     return decision
            # goal.remove(decision)
        return decision
    return None

"""
 ========================================
 Checks if the goal is the achieved 
 ========================================
"""

def checkGoal():
    if goalAxesXandY[0] == axesXandY:
        print("I'm here")
        goalAchieved(goalAxesXandY[0])
        return True
    return False

"""
 ========================================
 Movement of the SB each round
 ========================================
"""

def movement():
    goal = ''
    steps = 0
    while steps < 2:
        if danger == 0:
            goal = defineGoalAngle()
            if goal is None:
                return False
            else:
                newPosition(goal)
                if checkGoal() == True:
                    return False
        elif danger == 1:
            if steps == 1:
                break
            goal = defineGoalAngle()
            if goal is None:
                return False
            else:
                newPosition(goal)
                if checkGoal() == True:
                    return False
        elif danger == 2:
            if steps == 1:
                newPosition(lastMovement)
                break
            #if steps == 0:
            #   Reconocimiento
        
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

def moveToGoal(goal):

    global goalAxesXandY
    goalAxesXandY = goal

    moving = True
    i = 0
    print("Initial Angle: " + str(gyro_sensor.angle()))

    while(moving):

        if(True):
            time.sleep(2)
            print("Iteration: " + str(i))
            print("Initial Position: " + str(axesXandY))
            moving = movement()
            print("Final Position: " + str(axesXandY))
            i += 1

def main():

    moveToGoal([2, 2])


# Execute:

main()