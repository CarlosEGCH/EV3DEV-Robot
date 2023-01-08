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
from pybricks.media.ev3dev import SoundFile
import operator
import time
import random


# Initialize the EV3 Brick.
ev3 = EV3Brick()

# Initialize the Voice chat.
sound = SoundFile()

#Constants
UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0
CORNER_RIGHT = 45
CORNER_LEFT = 135
CORNER_RIGHT_DOWN = 225
CORNER_LEFT_DOWN = 225

MAX_AXE = 6
MIN_AXE = 1
MAX_STEPS = 2
MIN_STEPS = 1
# 1 tile to the next: 300
NEXTTILE = 300
# Necessary movement to read the next tile
READTILE = 140
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
# Variable to know if the SB has ammo or not
ammo = False
# Current steps that the SB can take
current_steps = MIN_STEPS
# If the SB has already recognized in the round
recognized_round = False
#Number of items
num_item = 0
#Number of ammos
num_ammo = 0
lastMovement = None

"""
 ========================================
    Add a new goal in the first position
 ========================================
"""

def addGoal(goal, type_name):
    global goalAxesXandY
    dicti = {"Type": type_name,
             "Axes": goal}
    goalAxesXandY.insert(0,dicti)

"""
 ========================================
    Deletes a goal when achieved
 ========================================
"""

def goalAchieved(goal):
    try:
        global goalAxesXandY
        for index in range(len(goalAxesXandY)):
            if goalAxesXandY[index]["Axes"] == goal:
                goalAxesXandY.remove(goalAxesXandY[index])
            return True
    except ValueError:
        return False

"""
 ========================================
    Pick the ammo and update the state 
 ========================================
"""

def pickAmmo():
    global ammo, current_steps
    current_steps = MAX_STEPS
    ammo = True

"""
 ========================================
    Leave the ammo and update the state 
 ========================================
"""

def leaveAmmo():
    global ammo, current_steps
    current_steps = MIN_STEPS
    ammo = False
    

"""
 ========================================
    Fixes the angle
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

    if(currentAngle - goalAngle > 0):
        b = currentAngle - goalAngle - 360
    else:
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
    test = smallestAngleBetween(current_degree, goalAngle)
    print("Smallest Angle Between " + str(test))
    print("Current Before Turn: " + str(gyro_sensor.angle()))
    robot.turn(test)
    print("Current After Turn: " + str(gyro_sensor.angle()))
    time.sleep(1)
    fixAngle()
    robot.straight(NEXTTILE)
    time.sleep(1)
    fixAngle()
    #Update the SB's direction and Axes
    current_degree = goalAngle
    updateAxes(goalAngle)
    return

def oppositeMovement(lastMovement):

    if lastMovement == RIGHT:
            return LEFT
    elif lastMovement == LEFT:
            return RIGHT
    elif lastMovement == UP:
            return DOWN
    elif lastMovement == DOWN:
            return UP

"""
 ========================================
 Defines the path to be taken by the SB
 ========================================
"""

def test(removeGoal):
    goal = [RIGHT, LEFT, DOWN, UP]
    if removeGoal != None:
        goal.remove(removeGoal)
    if axesXandY[0] + 1 > MAX_AXE:
        goal.remove(RIGHT)
    if axesXandY[0] - 1 < MIN_AXE:
        goal.remove(LEFT)
    if axesXandY[1] + 1 > MAX_AXE:
        goal.remove(DOWN)
    if axesXandY[1] - 1 < MIN_AXE:
        goal.remove(UP)
    return goal
    

def defineGoalAngle():
    global goalAxesXandY, axesXandY, lastMovement
    goal = []
    decision = None
    if goalAxesXandY == []:
        removeGoal = None
        if lastMovement != None:
            removeGoal = oppositeMovement(lastMovement)
        goal = test(removeGoal)
    
    elif goalAxesXandY[0]["Axes"][0] > axesXandY[0]:
        goal.append(RIGHT)
    elif goalAxesXandY[0]["Axes"][0] < axesXandY[0]:
        goal.append(LEFT)
    elif goalAxesXandY[0]["Axes"][1] > axesXandY[1]:
        goal.append(DOWN)
    elif goalAxesXandY[0]["Axes"][1] < axesXandY[1]:
        goal.append(UP)

    if goal != []:
        decision = random.choice(goal)
        lastMovement = decision
        print("My move is: " + str(decision))
        return decision

    return None

"""
 ========================================
 Checks if the goal is the achieved 
 ========================================
"""

def checkGoal():
    if goalAxesXandY != []:
        if goalAxesXandY[0]["Axes"] == axesXandY:
            print("I'm here")
            goalAchieved(goalAxesXandY[0]["Axes"])
            return True
    return False


def move():
    goal = defineGoalAngle()
    if goal is None:
        return False
    else:
        newPosition(goal)
        if checkGoal() == True:
            return False

def aimToZombie():
    global goalAxesXandY, axesXandY, current_degree
    axes = []
    for index in range(len(goalAxesXandY)):
        if goalAxesXandY[index]["Type"] == "Zombie":
            axes = goalAxesXandY[index]["Axes"]
            break
    axesX = axesXandY[0] - axes[0]
    axesY = axesXandY[1] - axes[1]

    if axesX < 0:
        angle = RIGHT
    elif axesX > 0:
        angle = LEFT
    elif axesY < 0:
        angle = DOWN
    elif axesY > 0:
        angle = UP
    print("Angle " + str(angle) + " Current degree " + str(current_degree))
    test = smallestAngleBetween(current_degree, angle)
    print("Smallest Angle Between " + str(test))
    print("Current Before Turn: " + str(gyro_sensor.angle()))
    robot.turn(test)
    print("Current After Turn: " + str(gyro_sensor.angle()))
    time.sleep(1)
    fixAngle()
    time.sleep(1)
    #Update the SB's direction and Axes
    current_degree = angle

    goalAchieved(axes)

def shootToZombie():
    aimToZombie()
    shootCannon()


"""
 ========================================
 Movement of the SB each round
 ========================================
"""

def movement():
    global danger
    goal = ''
    steps = 0
    
    while steps < current_steps:
        print("Looking for items in this box")
        searchColors()
        print("Sensing Danger")
        time.sleep(2)
        danger = senseSmell()
        if danger == 1:
            if steps == 1:
                if recognized_round == False and ammo == True:
                    move()
                    danger = senseSmell()
                    if danger == 2:
                        recognize()
                        shootToZombie()
                    break
                break
        elif danger == 2:
            if steps == 1:
                if recognized_round == False:
                    recognize()
                    if ammo == True:
                        shootToZombie()
                    else:
                        sound.speak('Voy a por ti crack')
                    break
                newPosition(oppositeMovement(lastMovement))
                break
            if steps == 0:              
                recognize()
                ammo = True
                if ammo == True:
                    shootToZombie()
                    break
                move() #Stunn
                break

        test = random.randint(1,3)
        if(test == 1):
            recognize()

        move()
        steps += 1
    recognized_round = False
    return True


"""
 ========================================
 Recognizement of items and ammunition
 ========================================
"""

def searchColors():
    global num_item, num_ammo

    # Detect which color the next tile is
    color = detectColor()
    print(color)

    if color == Color.BLUE:
        # An item was found in the current box
        num_item += 1
        print("I have found an item")
        pickupItem()
    elif color == Color.RED:
        # An ammo was found in the current box
        num_ammo += 1
        print("I have found an ammo")
        pickupItem()
        pickAmmo()
    elif color == Color.YELLOW:
        # A Zombie was found in the current box
        sound.speak('Voy a por ti crack')
        


def detectColor():
    return color_sensor.color()

def recognizeGoal():
    global current_degree
    if current_degree == RIGHT:
        current_degree = DOWN
    elif current_degree == DOWN:
        current_degree = LEFT
    elif current_degree == LEFT:
        current_degree = UP
    elif current_degree == UP:
        current_degree = RIGHT
    
def calculateGoal():
    global axesXandY
    if current_degree == RIGHT:
        if axesXandY[0] + 1 <= MAX_AXE:
            return [axesXandY[0] + 1, axesXandY[1]]
    elif current_degree == DOWN:
        if axesXandY[1] + 1 <= MAX_AXE:
            return [axesXandY[0], axesXandY[1] + 1]
    elif current_degree == LEFT:
        if axesXandY[0] - 1 >= MIN_AXE:
            return [axesXandY[0] - 1, axesXandY[1]]
    elif current_degree == UP:
        if axesXandY[1] - 1 >= MIN_AXE:
            return [axesXandY[0], axesXandY[1] - 1]
    return None

def recognize():
    global recognized_round

    # The robot must move enough to read the color on the next tile
    # and return to the original place.

    # Then turn 90 degrees and read the next adjacent tile.
    adjacent_tiles = ["nothing", "nothing", "nothing", "nothing"]

    objectives = []

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
            adjacent_tiles[index] = "Item"
            goal = calculateGoal()
            if goal != None:
                objectives.append({"Type": "Item", "Axes": goal})
        
        elif color == Color.RED:
            # A piece of ammo was found and saved in the array
            adjacent_tiles[index] = "Ammo"
            goal = calculateGoal()
            if goal != None:
                objectives.append({"Type": "Ammo", "Axes": goal})
            
        elif color == Color.YELLOW:
            # A piece of ammo was found and saved in the array
            adjacent_tiles[index] = "Zombie"
            goal = calculateGoal()
            if goal != None:
                objectives.append({"Type": "Zombie", "Axes": goal})
            
        
        robot.straight(-READTILE)
        robot.turn(90)
        recognizeGoal()
        fixAngle()

    #Add the objectives to the goal array order by priority
    if len(objectives) != 0:
        #newlist = sorted(objectives, key=operator.itemgetter('Type'))

        #Test
        newlist = objectives
        
        for index in range(len(newlist)):
            addGoal(newlist[index]["Axes"], newlist[index]["Type"])
            
    
    # Update the variable per round 
    recognized_round = True

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
 Pickup Item Method
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
 Zombie recognizement
 ========================================
"""

def senseSmell():

    danger = 0

    for index in range(4):

        distance = distance_sensor.distance()

        if ( 140 < distance < 420 and danger <= 2 ):
            danger = 2
            
        elif ( 490 < distance < 710 and danger <= 1 ):
            danger = 1

        robot.turn(90)
        fixAngle()

    print("Danger Sensed: " + str(danger))
    return danger

"""
 ========================================
 Main Execution
 ========================================
"""

def moveToGoal(goal):

    #addGoal(goal, "Objective")

    moving = True
    i = 0
    print("Initial Angle: " + str(gyro_sensor.angle()))

    while(moving):

        if(True):
            time.sleep(1)
            print("Iteration: " + str(i))
            print("Initial Position: " + str(axesXandY))
            moving = movement()
            print("Final Position: " + str(axesXandY))
            i += 1

def main():

    moveToGoal([3, 3])


# Execute:

main()
