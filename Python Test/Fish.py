import numpy as np
import cv2
import argparse
import math
from pythonosc import udp_client


# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

# https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
##eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

fish_cascade = cv2.CascadeClassifier('green2.xml')

# Parameter Generation Sructs
FRAME_DATA_LIST_SIZE = 30    # How much frame data to remember at once
frameDataList = []           # List containing remembered frame data
frameDataListString = ""     # String for printing the frame data for testing
frameInformationString = ""  # String for printing all the information below

DeltaX = -1
DeltaY = -1
slope = -1
angle = -1
quadrant = -1
magnitude = -1
stopped = -1
STOPPED_TRESHOLD = 4         # threshold for determining if the fish is stopped in place or is actively moving

# class describing Fish Frame Data
class FishData:
    x = -1  # x coordinate
    y = -1  # y coordinate

    # constructor override
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # toString override
    def __str__(self):
        return "[ x = " + str(self.x) + " , y = " + str(self.y) + " ]"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
                        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

cap = cv2.VideoCapture('justadot.mp4')

# initializes temp objects in the frameDataList
for x in range(0, FRAME_DATA_LIST_SIZE):
    frameDataList.append(FishData(-1,-1))

while 1:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ##faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    fishs = fish_cascade.detectMultiScale(gray,40,40)


    for (x, y, w, h) in fishs:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]

        cx = int(x+(w/2))
        cy = int(y+(h/2))
        cyConverted = int( (cy-50)/50 + 1)
        if( not(cyConverted < 0) and not(cyConverted > 10) ):
            print("(%d,%d)" % (cx, cyConverted))

            # pushes all values in the Frame List down by one, and adds the new value pair into the List
            for x in range(FRAME_DATA_LIST_SIZE-2, -1, -1):
                frameDataList[x + 1] = frameDataList[x]
            frameDataList[0] = FishData(cx, cy)
            # If the list has collected a full list of data, print the Data out, and send it
            if(frameDataList[FRAME_DATA_LIST_SIZE-1].x > 0):
                frameDataListString = ""
                for x in frameDataList:
                    frameDataListString += " " + str(x)
                print(frameDataListString)

                # generates the parameters from x and y
                DeltaX = frameDataList[FRAME_DATA_LIST_SIZE-1].x - cx  # Change in X
                DeltaY = frameDataList[FRAME_DATA_LIST_SIZE-1].y - cy  # Change in Y
                # slope
                if(DeltaX == 0):
                    # no slope, avoid divide by 0
                    slope = 999
                else:
                    slope = DeltaY / DeltaX
                # angle
                angle = math.atan(slope)
                # quadrant
                if(DeltaX > 0 and DeltaY > 0):
                    quadrant = 1
                elif(DeltaX <= 0 and DeltaY > 0):
                    quadrant = 2
                elif(DeltaX <= 0 and DeltaY <= 0):
                    quadrant = 3
                else:
                    quadrant = 4
                # magnitude
                    magnitude = math.sqrt( math.pow(DeltaX, 2) + math.pow(DeltaY, 2) )
                # stopped
                if(magnitude >= STOPPED_TRESHOLD):
                    stopped = -1  # fish is moving
                else:
                    stopped = 1   # fish is still

                frameInformationString = "Slope: " + str(slope) + " Angle: " + str(angle) + " Quadrant: " + str(quadrant) + " Magnitude: " + str(magnitude) + " Stopped?: " + str(stopped)
                print(frameInformationString)

                client.send_message("/x", cx)
                client.send_message("/y", cyConverted)
                # Draws a line to show the difference of the two points
                cv2.line(img, (frameDataList[FRAME_DATA_LIST_SIZE - 1].x, frameDataList[FRAME_DATA_LIST_SIZE - 1].y),  (cx, cy),
                           (255, 255, 0), thickness=2)
                # Draws a circle to show the last remembered point
                cv2.circle(img, (frameDataList[FRAME_DATA_LIST_SIZE - 1].x, frameDataList[FRAME_DATA_LIST_SIZE - 1].y), 5,
                           (0, 255, 255), thickness=5, lineType=0)
            else:
                # if the list still has temp values, skip sending, and collect more
                print("Collecting Initial Values... ")
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), thickness=5, lineType=0)



        ##eyes = eye_cascade.detectMultiScale(roi_gray)
        ##  for (ex, ey, ew, eh) in eyes:
          ##  cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    cv2.imshow('img', img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()