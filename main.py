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
import threading


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
CORNER_LEFT_DOWN = 225
CORNER_RIGHT_DOWN = 315

MAX_AXE = 6
MIN_AXE = 1
MAX_STEPS = 2
MIN_STEPS = 1
# 1 tile to the next: 300
NEXTTILE = 290
# Necessary movement to read the next tile
READTILE = 140
# Stun distance
STUNZOMBIE = 120


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
# Win condition
axesWin = [6,6]
#               [     X     ,      Y     ]
# It is an array of goals where the first element has the bigger priority
goalAxesXandY = [{"Type": "Zombie", "Axes": []}, {"Type": "Ammo", "Axes": []}, {"Type": "Mota", "Axes": []}, {"Type": "Item", "Axes": []}]
# The danger that the SB has. Possible values are "0", "1", "2"
danger = 0
# Variable to know if the SB has ammo or not
ammo = False
# Variable to know if the SB has an item or not
item = False
# Current steps that the SB can take
current_steps = MIN_STEPS
# If the SB has already recognized in the round
recognized_round = False
#Number of items picked
num_item = 0
#alarm 
alarm = False
# The 4 last movements that the SB has given are stored in this array
lastMovement = []

"""
 ========================================
    Add a new goal in the first position
 ========================================
"""

def addGoal(goal, type_name):
    global goalAxesXandY
    #Creates the dictionary to be inserted in the goalAxesXandY array
    dicti = {"Type": type_name,
             "Axes": goal}
    #Insert the dictionary in the specific type 
    for index, item in enumerate(goalAxesXandY):
        if item["Type"] == type_name:
            if dicti not in goalAxesXandY[index]["Axes"]:
                goalAxesXandY[index]["Axes"].insert(0,dicti)
                break

"""
 ========================================
    Deletes a goal when achieved
 ========================================
"""

def goalAchieved(goal):
    try:
        global goalAxesXandY

        #Search for the goal and remove it from the array
        for index in range(len(goalAxesXandY)):
            if goalAxesXandY[index]["Axes"]:
                for i, item in enumerate(goalAxesXandY[index]["Axes"]):
                    if goalAxesXandY[index]["Axes"][i]["Axes"] == goal:
                        goalAxesXandY[index]["Axes"].pop(i)
        return True
    except ValueError:
        return False

"""
 ========================================
    Get the highest priority goal 
 ========================================
"""

def getFirstGoal():
    global goalAxesXandY

    #Returns the first occurrence
    for index in range(len(goalAxesXandY)):
        if goalAxesXandY[index]["Axes"]:
            return goalAxesXandY[index]["Axes"][0]
    return []

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
    Pick the item and update the state 
 ========================================
"""

def pickItem():
    global item, alarm
    item = True
    addGoal([6,6], "Mota")
    alarm = True 

"""
 ========================================
    Leave the item and update the state 
 ========================================
"""

def leaveItem():
    global item, alarm
    
    item = False  
    alarm = False
    openClaw()


"""
 ========================================
    Play the alarm sound 
 ========================================
"""

def playAlarm():
    global alarm

    while True: 
        if alarm:
            ev3.speaker.play_file(SoundFile.SONAR)

"""
 ========================================
    Stun 
 ========================================
"""

def stun():
    closeClaw()
    robot.straight(-STUNZOMBIE)
    robot.straight(STUNZOMBIE + 80)
    robot.straight(-80)


"""
 ========================================
    Fixes the angle
 ========================================
"""

def fixAngle():

    currentAngle = abs(gyro_sensor.angle())

    print("Current: " + str(currentAngle))

    if(gyro_sensor.angle() < 0):
        fixedAngle = currentAngle%45 * -1
    else:
        fixedAngle = currentAngle%45
    if fixedAngle > 22:
        fixedAngle = fixedAngle - 45
    elif fixedAngle < -22:
        fixedAngle = 45 - abs(fixedAngle) 

    print("Fixed: " + str(fixedAngle))

    while(1):
        if(fixedAngle > 0):
            robot.turn(-1)
            fixedAngle -= 1
        elif(fixedAngle < 0):
            robot.turn(1)
            fixedAngle += 1
        else:
            if abs(gyro_sensor.angle() % 360) == 0 or abs(gyro_sensor.angle()) == 3228: 
                gyro_sensor.reset_angle(0)
            break

"""
 ========================================
    Return the smallest angle to see if the SB turns left or right
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
    time.sleep(2)
    fixAngle()
    robot.straight(NEXTTILE)
    time.sleep(2)
    fixAngle()
    #Update the SB's direction and Axes
    current_degree = goalAngle
    updateAxes(goalAngle)
    return

"""
 ========================================
    Save the current tile in the lastMovements array and delete the least recent
 ========================================
"""

def mov():
    global lastMovement

    add = axesXandY
    lastMovement.append([add[0], add[1]])

    print("Last Movements: " + str(lastMovement))

    if len(lastMovement) == 4:
        lastMovement.pop(0)

"""
 ========================================
    Delete the lastMovements to where the SB cant go back 
 ========================================
"""

def deleteMovement():
    global lastMovement, axesXandY

    removeMovement = []

    if [axesXandY[0] + 1, axesXandY[1]] in lastMovement:
        removeMovement.append(RIGHT)

    if [axesXandY[0] - 1, axesXandY[1]] in lastMovement:
        removeMovement.append(LEFT)

    if [axesXandY[0], axesXandY[1] + 1] in lastMovement:
        removeMovement.append(DOWN)
    
    if [axesXandY[0], axesXandY[1] - 1] in lastMovement:
        removeMovement.append(UP)

    print("Deleted movements of previous rounds" + str(removeMovement))

    return removeMovement

"""
 ========================================
    Returns the opposite Movement to the one received as argument 
 ========================================
"""

def oppositeMovement(lastMovement):
    global axesXandY

    if lastMovement == [axesXandY[0] - 1, axesXandY[1]]:
            return LEFT
    elif lastMovement == [axesXandY[0] + 1, axesXandY[1]]:
            return RIGHT
    elif lastMovement == [axesXandY[0], axesXandY[1] + 1]:
            return DOWN
    elif lastMovement == [axesXandY[0], axesXandY[1] - 1]:
            return UP

"""
 ========================================
 Remove the options where the SB exits the game board
 ========================================
"""

def test(removeGoal):
    goal = [RIGHT, LEFT, DOWN, UP]
    if removeGoal:
        for t in removeGoal:
            goal.remove(t)
    if axesXandY[0] + 1 > MAX_AXE and RIGHT in goal:
        goal.remove(RIGHT)
    if axesXandY[0] - 1 < MIN_AXE and LEFT in goal:
        goal.remove(LEFT)
    if axesXandY[1] + 1 > MAX_AXE and DOWN in goal:
        goal.remove(DOWN)
    if axesXandY[1] - 1 < MIN_AXE and UP in goal:
        goal.remove(UP)
    return goal

"""
 ========================================
 Defines the path to be taken by the SB
 ========================================
"""

def defineGoalAngle():
    global axesXandY, lastMovement
    goalAxes = getFirstGoal()
    goal = []
    decision = None

    #If the SB does not have an objective, he takes the path he wants
    if not goalAxes:
        removeGoal = None
        if lastMovement:
            removeGoal = deleteMovement()
        goal = test(removeGoal)

    #Otherwise he moves to the objective
    elif goalAxes["Axes"][0] > axesXandY[0]:
        goal.append(RIGHT)
    elif goalAxes["Axes"][0] < axesXandY[0]:
        goal.append(LEFT)
    elif goalAxes["Axes"][1] > axesXandY[1]:
        goal.append(DOWN)
    elif goalAxes["Axes"][1] < axesXandY[1]:
        goal.append(UP)

    #If there is more than one option the SB takes a random option
    if goal != []:
        decision = random.choice(goal)
        print("My move is: " + str(decision))
        return decision

    return None

"""
 ========================================
 Checks if the goal is the achieved 
 ========================================
"""

def checkGoal():
    goalAxes = getFirstGoal()

    if goalAxes:
        if goalAxes["Axes"] == axesXandY:
            print("I'm here")
            goalAchieved(goalAxes["Axes"])
            return True
    return False

"""
 ========================================
 Move the SB to the goal previously defined 
 ========================================
"""

def move():
    goal = defineGoalAngle()
    if goal is None:
        return False
    else:
        newPosition(goal)
        if checkGoal():
            return False

"""
 ========================================
 Aim to the zombie next to him
 ========================================
"""

def aimToZombie():
    global axesXandY, current_degree

    goalAxes = getFirstGoal()
    axes = []

    if goalAxes["Type"] == "Zombie":
        axes = goalAxes["Axes"]

    #Determine which tile the zombie is on
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
    time.sleep(2)
    fixAngle()
    time.sleep(2)
    # Update the SB's direction
    current_degree = angle
    # Delete that have just died from the goalAxesXandY array
    goalAchieved(axes)

"""
 ========================================
 Shoot to the zombie he is aiming to
 ========================================
"""

def shootToZombie():
    aimToZombie()
    shootCannon()
    leaveAmmo()

"""
 ========================================
 Check if the SB won the game
 ========================================
"""
def checkFinale():
    global axesXandY, item, num_item, axesWin

    flagWin = True

    if axesXandY == axesWin:
        # If the SB still do not have the two items, continue the game
        if item and num_item < 2:
            leaveItem()
            num_item += 1
            # Remove from the goalAxesXandY the Mota objective
            goalAchieved(axesWin)

    # If the SB have the two items, wins the game
    if num_item == 2:
        flagWin = False

    return flagWin
        

"""
 ========================================
 Movement of the SB each round and logical decision making
 ========================================
"""

def movement():
    global danger, current_steps, recognized_round, lastMovement
    goal = ''
    steps = 0
    boolean = True
    
    while steps < current_steps:
        mov()
        print("Looking for items in this box")
        searchColors()
        print("Sensing Danger")
        time.sleep(2)
        danger = senseSmell()
        time.sleep(5)

        # The most important thing to make a decision is the smell
        # Danger could take values from 0 to 2 where 2 is the most dangerous situation

        if danger == 1:
            if steps == 1:
                if not recognized_round and ammo:
                    move()
                    danger = senseSmell()
                    time.sleep(5)
                    if danger == 2:
                        recognize()
                        shootToZombie()
                        time.sleep(5)
                    break
                break
            if steps == 0:
                move()
                steps += 1
                boolean = checkFinale()
                if not boolean: 
                    break
                continue
        elif danger == 2:
            if steps == 1:
                if not recognized_round:
                    recognize()
                    if ammo:
                        shootToZombie()
                        time.sleep(5)
                    else:
                        move()
                        searchColors()
                    break
                newPosition(oppositeMovement(lastMovement[len(lastMovement) - 2]))
                break
            if steps == 0:
                steps += 1              
                recognize()
                if ammo:
                    shootToZombie()
                    time.sleep(5)
                    break
                move() #Move to Stunn the Zombie
                searchColors()
                break

        # The SB has a 50% chance of doing the recognizement in each movement, except when there is a specific action 
        # for a specific situation (The ones shown above)
        if not recognized_round:
            test = random.randint(1,2)
            if(test == 1):
                recognize()
                if steps == 1:
                    break

        move()
        boolean = checkFinale()
        if not boolean: 
            break
        
        checkGoal()
        steps += 1

        if steps == 2 and not recognized_round:
            recognize()

    # Check after the movement to see if there is something in the current tile and if there is a zombie close to him
    print("Looking for items in this box 2")
    searchColors()
    if steps == 1:
        time.sleep(5)
        danger = senseSmell()
        if danger == 2:
            if not recognized_round:
                recognize()
                if ammo:
                    shootToZombie()
                    time.sleep(5)
                else:    
                    move()
                    searchColors()
            else:
                newPosition(oppositeMovement(lastMovement[len(lastMovement) - 1]))
        
    recognized_round = False
    return boolean


"""
 ========================================
 Recognizement of items and ammunition
 ========================================
"""

def searchColors():

    # Detect which color the current tile is
    color = detectColor()
    print(color)

    if color == Color.GREEN and not item:
        # An item was found in the current tile
        print("I have found an item")
        pickupItem()
        pickItem()
        time.sleep(8)
    elif color == Color.RED:
        # An ammo was found in the current tile
        print("I have found an ammo")
        pickupItem()
        pickAmmo()
        time.sleep(8)
    elif color == Color.BLUE:
        # A Zombie was found in the current tile
        stun()
        time.sleep(8)

"""
 ========================================
 Detect the color in the current tile
 ========================================
"""          

def detectColor():
    return color_sensor.color()

"""
 ========================================
 Update the angle where the SB is currently watching to
 ========================================
""" 

def recognizeGoal(goal):
    global current_degree
    
    current_degree = goal

"""
 ========================================
 Calculates the axes where the SB has to move depending on the current_degree (Current Angle)
 ========================================
""" 
    
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

"""
 ========================================
 Removes out of game board moves to do logical adjacent tile recognizement 
 ========================================
""" 

def checkCorners():
    global axesXandY

    chances = [RIGHT, UP, LEFT, DOWN]

    if axesXandY[1] == 1:
        chances.remove(UP)
    if axesXandY[1] == 6:
        chances.remove(DOWN)
    if axesXandY[0] == 1:
        chances.remove(LEFT)
    if axesXandY[0] == 6:
        chances.remove(RIGHT)

    return chances 

"""
 ========================================
 Sorts the list of possible recognition moves to look natural
 ========================================
""" 

def sortDirections(list_of_directions):
    global current_degree

    listed = []
    for x in list_of_directions:
        sort =  abs(smallestAngleBetween(current_degree, x))
        i = None
        if listed:
            for index, option in enumerate(listed):
                if sort <= abs(smallestAngleBetween(current_degree, option)):
                    i = index
                    break
            if i != None:
                listed.insert(i , x)
            else:
                listed.append(x)
        else:
            listed.append(x)
            
    return listed

"""
 ========================================
 Recognizes what is in its 4 adjacent tiles
 ========================================
""" 

def recognize():
    global recognized_round, current_degree

    # The robot must move enough to read the color on the next tile
    # and return to the original place.

    # Then turn 90 degrees and read the next adjacent tile.
    directions = sortDirections(checkCorners())
    # List of tiles where the SB found something
    objectives = []

    for index in range(len(directions)):

        # Move towards the tile to read it and correct the angle error
        robot.turn(smallestAngleBetween(current_degree, directions[index]))
        fixAngle()
        time.sleep(2)

        recognizeGoal(directions[index])
        robot.straight(READTILE)
        time.sleep(2)

        # Correct the angle error
        fixAngle()
        time.sleep(2)

        # Detect which color the next tile is
        color = detectColor()

        print("Color: " + str(color))

        if color == Color.GREEN:
            # An item was found and saved in the array
            goal = calculateGoal()
            if goal != None:
                objectives.append({"Type": "Item", "Axes": goal})
        
        elif color == Color.RED:
            # A piece of ammo was found and saved in the array
            goal = calculateGoal()
            if goal != None:
                objectives.append({"Type": "Ammo", "Axes": goal})
            
        elif color == Color.BLUE:
            # A Zombie was found and saved in the array
            goal = calculateGoal()
            if goal != None:
                objectives.append({"Type": "Zombie", "Axes": goal})
            
        
        robot.straight(-READTILE)

        fixAngle()

    #Add the objectives to the goal array
    if len(objectives) != 0:
        
        for index in range(len(objectives)):
            addGoal(objectives[index]["Axes"], objectives[index]["Type"])
            
    
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
    robot.turn(-30)
    closeClaw()
    robot.turn(30)


"""
 ========================================
 Update the current degree (Current Angle) while the SB is doing the scent recognition
 ========================================
"""

def recognizeSmell():
    global current_degree
    if current_degree == RIGHT:
        current_degree = CORNER_RIGHT_DOWN
    elif current_degree == CORNER_RIGHT_DOWN:
        current_degree = DOWN
    elif current_degree == DOWN:
        current_degree = CORNER_LEFT_DOWN
    elif current_degree == CORNER_LEFT_DOWN:
        current_degree = LEFT
    elif current_degree == LEFT:
        current_degree = CORNER_LEFT
    elif current_degree == CORNER_LEFT:
        current_degree = UP
    elif current_degree == UP:
        current_degree = CORNER_RIGHT
    elif current_degree == CORNER_RIGHT:
        current_degree = RIGHT

"""
 ========================================
 Check if the SB is doing the scent recognition diagonally to verify if the danger is "1"
 ========================================
"""

def checkDistance():
    global current_degree
    flag = False

    if current_degree == CORNER_RIGHT or current_degree == CORNER_LEFT or current_degree == CORNER_RIGHT_DOWN or current_degree == CORNER_LEFT_DOWN:
        flag = True

    return flag

"""
 ========================================
 Zombie recognize the smell both diagonally, vertically and horiontally and return the danger that the SB has to die
 ========================================
"""

def senseSmell():

    danger = 0

    for index in range(8):

        distance = distance_sensor.distance()

        if ( 150 < distance < 340 and danger <= 2 ):
            if checkDistance():
                danger = 1
            else:
                danger = 2
            
        elif ( 520 < distance < 660 and danger <= 1 ):
            if not checkDistance():
                danger = 1

        robot.turn(45)
        time.sleep(2)
        recognizeSmell()
        fixAngle()

    print("Danger Sensed: " + str(danger))
    return danger

"""
 ========================================
 Main Function
 ========================================
"""

def moveToGoal():

    moving = True
    i = 0
    print("Initial Angle: " + str(gyro_sensor.angle()))

    while(moving):

        if(button.pressed()):
            time.sleep(2)
            print("Iteration: " + str(i))
            print("Initial Position: " + str(axesXandY))
            moving = movement()
            print("Final Position: " + str(axesXandY))
            i += 1

"""
 ========================================
 Main Execution
 ========================================
"""

def main():
   
    t1 = threading.Thread(target=playAlarm)
    t1.start()

    moveToGoal()


# Execute:

main()
