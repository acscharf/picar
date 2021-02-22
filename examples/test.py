from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from threading import Thread

from picamera import PiCamera
from picamera.array import PiRGBArray

import picar_4wd as fc
import time
import numpy as np
import sys
import math
from PIL import Image
import heapq

import argparse
import io
import re
import time
import cv2


from annotation import Annotator

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter



speed = 5
safe_distance = 15


def main():

    forward_cnt = 0

    distance1 = 15
    direction1 = 'turnaround'
    distance2 = 15
    direction2 = 'turnaround'
    distance3 = 15
    direction3 = 'turnaround'
    distance4 = 15
    direction4 = 'turnaround'

    current_distance = distance1
    current_direction = direction1
    step = 1

    print("yolo2")

    vs = PiVideoStream().start()
    time.sleep(2)     

    while True:
        result = vs.see_sign()
        if result is True:
            fc.stop()
            time.sleep(5)
            print("Stopped for a stop sign after detecting object")
            vs.reset_stop()

    while True:

        scan_list = fc.scan_step(35)
        if not scan_list:
            continue

        tmp = scan_list[3:7]

        if tmp != [2,2,2,2]:
            print("Saw something!!")

            fc.stop()

            move = read_angles()

            result = vs.see_sign()
            print(result)
            if result is True:
                fc.stop()
                time.sleep(5)
                print("Stopped for a stop sign after detecting object")
                vs.reset_stop()

            # should go left
            if move == 0 and result is False:
                print("Moving left")
                forward_cnt = forward_cnt + 3
                turn_left_s(speed)
                forward_s(speed)
                turn_right_s(speed)
                turn_right_s(speed)
                forward_s(speed)
                turn_left_s(speed)

                
            #go right
            if move == 1 and result is False:
                print("Moving right")
                forward_cnt = forward_cnt + 3
                turn_right_s(speed)
                forward_s(speed)
                turn_left_s(speed)
                turn_left_s(speed)
                forward_s(speed)
                turn_right_s(speed)

        else:
            fc.forward(speed)
            forward_cnt = forward_cnt + 1
            result = vs.see_sign()
            print(result)
            if result is True:
                fc.stop()
                time.sleep(5)
                print("Stopped for a stop sign while moving")
                vs.reset_stop()
            print("total forward: ")

            print(forward_cnt)
            if forward_cnt > current_distance:
                if step == 2:
                    print("moving to step 2")
                    current_distance = distance2
                    current_direction = direction2
                if step == 3:
                    print("moving to step 3")
                    current_distance = distance3
                    current_direction = direction3
                if step == 4:
                    print("moving to step 4")
                    current_distance = distance4
                    current_direction = direction4

                step = step + 1
                
                if current_direction == 'left':
                    print("making a left turn")
                    fc.turn_left(speed)
                    time.sleep(1)
                    fc.stop()
          
                if current_direction == 'right':
                    print("making a right turn")
                    fc.turn_right(speed)
                    time.sleep(1)
                    fc.stop()

                if current_direction == 'turnaround':
                    print("turning around")
                    fc.turn_right(speed)
                    time.sleep(1.75)
                    fc.stop()
                
                forward_cnt = 0

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

'''
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

'''

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

    array = np.zeros((40,81))

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
            #make it bigger
            x = x
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
        ## object is off to one side
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


def load_labels(path):
  """Loads the labels file. Supports files with or without index numbers."""
  with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labels = {}
    for row_number, content in enumerate(lines):
      pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
      if len(pair) == 2 and pair[0].strip().isdigit():
        labels[int(pair[0])] = pair[1].strip()
      else:
        labels[row_number] = pair[0].strip()
  return labels


def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor


def detect_objects(interpreter, image, threshold):
  """Returns a list of detection results, each a dictionary of object info."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()

  # Get all output details
  classes = get_output_tensor(interpreter, 1)
  scores = get_output_tensor(interpreter, 2)
  count = int(get_output_tensor(interpreter, 3))

  results = False
  for i in range(count):
    if scores[i] >= threshold:
        if classes[i] == 12:
            results = True
  return results


def annotate_objects(annotator, results, labels):
  """Draws the bounding box and label for each object in the results."""
  for obj in results:
    # Convert the bounding box figures from relative coordinates
    # to absolute coordinates based on the original resolution
    ymin, xmin, ymax, xmax = obj['bounding_box']
    xmin = int(xmin * CAMERA_WIDTH)
    xmax = int(xmax * CAMERA_WIDTH)
    ymin = int(ymin * CAMERA_HEIGHT)
    ymax = int(ymax * CAMERA_HEIGHT)

    # Overlay the box, label, and score on the camera preview
    annotator.bounding_box([xmin, ymin, xmax, ymax])
    annotator.text([xmin, ymin],
                   '%s\n%.2f' % (labels[obj['class_id']], obj['score']))

class PiVideoStream:
    def __init__(self, resolution=(640, 480), framerate=30, **kwargs):
        # initialize the camera
        self.camera = PiCamera()

        # set camera parameters
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.saw_sign = False

        self.labels = load_labels('coco_labels.txt')
        self.interpreter = Interpreter('detect.tflite')

        self.interpreter.allocate_tensors()
        _, self.input_height, self.input_width, _ = self.interpreter.get_input_details()[0]['shape']

        # set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in kwargs.items():
            setattr(self.camera, arg, value)

        # initialize the stream
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
    
        for f in self.stream:
        # grab the frame from the stream and clear the stream in
        # preparation for the next frame
            self.frame = f.array

            cv2.imwrite('color_img.jpg', self.frame)

            image = Image.fromarray(self.frame).convert('RGB').resize(
                (self.input_width, self.input_height), Image.ANTIALIAS)

            self.results = detect_objects(self.interpreter, image, 0.4)
            if self.results is True:
                self.saw_sign = True
                print("saw a stop sign and updated to true!!")
            #stop sign

            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
    # return the frame most recently read
        return self.frame

    def see_sign(self):
        return self.saw_sign

    def reset_stop(self):
    # return the frame most recently read
        self.saw_sign = False

    def stop(self):
    # indicate that the thread should be stopped
        self.stopped = True


if __name__ == "__main__":
    try: 
        main()
    finally: 
        print("yolo")
        fc.stop()