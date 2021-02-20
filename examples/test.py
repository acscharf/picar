import picar_4wd as fc
import time
import numpy as np
import sys
import math
from PIL import Image
import heapq

speed = 10
safe_distance = 15


def main():


    while True:
        scan_list = fc.scan_step(35)
        if not scan_list:
            continue

        tmp = scan_list[3:7]

        if tmp != [2,2,2,2]:
            print("Saw something!!")
            fc.stop()
            move = read_angles()
            print(tmp)
            # should go left
            if move == 0:
                print("Moving left")
                turn_left_s(speed)
                forward_s(speed)
                turn_right_s(speed)
                turn_right_s(speed)
                forward_s(speed)
                turn_left_s(speed)

                
            #go right
            if move == 1:
                print("Moving right")
                turn_right_s(speed)
                forward_s(speed)
                turn_left_s(speed)
                turn_left_s(speed)
                forward_s(speed)
                turn_right_s(speed)

        else:
            fc.forward(speed)


def turn_left_s(speed):
    fc.turn_left(speed)
    time.sleep(.3)
    fc.stop()

def turn_right_s(speed):
    fc.turn_right(speed)
    time.sleep(.35)
    fc.stop()

def forward_s(speed):
    fc.forward(speed)
    time.sleep(1.5)
    fc.stop()

def get_direction(lefts, rights):
    choice1 = fc.get_status_at(30, 35, 10)
    choice2 = fc.get_status_at(-30, 35, 10)

    if (lefts >= rights) and (choice1 == 2):
        #fc.turn_right(speed)
        rights = rights + 1
        time.sleep(.25)
        return True, lefts, rights
    elif (lefts < rights) and (choice2 == 2):
        #fc.turn_left(speed)
        lefts = lefts + 1
        time.sleep(.25)
        return True, lefts, rights
    elif choice1 == 2:
        #fc.turn_right(speed)
        rights = rights + 1
        time.sleep(.25)
        return True, lefts, rights
    elif choice2 == 2:
        #fc.turn_left(speed)
        lefts = lefts + 1
        time.sleep(.25)
        return True, lefts, rights
    else:
        return False, lefts, rights

def read_angles():
    angle_range = 180
    step = 10
    max_angle = angle_range/2
    min_angle = -angle_range/2
    angle = max_angle

    new_object = False
    continue_object = False
    x_prev = 0
    x_prev = 0
    x = 0
    y = 0

    array = np.zeros((40,80))

    while angle >= -90:
        #print("Angle is")
        #print(angle)
        distance = fc.get_distance_at(angle)

        if (distance > 0) and (distance < 40):

            # Continuing existing object
            if (new_object is True) and (continue_object is False):
                #print("Continuing object!")
                continue_object = True

            # New object encountered
            if (new_object is False) and (continue_object is False):
                #print("New object encountered!")
                new_object = True      
                
            if continue_object is True:
                x_prev = x
                y_prev = y

            #print("Distance is")
            #print(distance)

            x = int(round((math.cos(math.radians(angle))) * distance))
            y = int(round((math.sin(math.radians(angle))) * distance))
            #print("X is")
            #print(x)
            #print("Y is")
            #print(y)
            y = y + 40
            array[x,y] = 1

            # Update slope for existing object
            if continue_object is True:
                array = get_line(x, y, x_prev, y_prev, array)

        else:
            #print("Out of range")
            new_object = False
            continue_object = False
        angle = angle - step
        time.sleep(0.1)

    start = (0,39)
    goal = (39,39)
    route = astar(array, start, goal)
    route = route + [start]
    route = route[::-1]

    ytotal = 0

    for i in (range(0,len(route))):
        x = route[i][0]
        y = route[i][1]
        ytotal = y + ytotal
        array[x,y] = 2
        
    ytotal = int(round(ytotal / len(route)))

    print(ytotal)

    np.savetxt("test.out", array, fmt='%i')

    if ytotal == 39:
        print("Straight")
        return 2
    if ytotal > 39:
        print("Left")
        return 0
    if ytotal < 39:
        print("Right")
        return 1

def heuristic(a, b):
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def astar(array, start, goal):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:                
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
    return False

# code from https://stackoverflow.com/questions/25837544/get-all-points-of-a-straight-line-in-python
def get_line(x1, y1, x2, y2, array):
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            array[y,x] = 1
        else:
            array[x,y] = 1
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax

    return array

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
