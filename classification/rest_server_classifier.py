import cv2
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask
from object_detection import ObjectDetector

# function to draw bounding box on the detected object with class name
def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h, classes=[]):
    label = ''
    if len(classes) > 0:
        label = str(classes[class_id])
    
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), 1, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 4)

def readImage(filename='', ip=''):
    if len(filename) > 0:
        image = cv2.imread(filename)
    else:
        cap = cv2.VideoCapture('http://' + ip + '/video')
        ret, image = cap.read()
        cap.release()
        cv2.destroyAllWindows()
        if not ret:
            print('Error reading frame: {}'.format(ret))
            image = None
    return image

def loadClasses(file):
    classNames = {}
    with open(file) as f:
        classNames = { int(line.split(',')[0]) : line.split(',')[1].strip() for line in f.readlines() }
        f.close()
    return classNames

def countPeople(image):
    result = det.getBoundingBoxes(image)
    print(result)
    numPeople = 0
    for res in result:
        name = classes[res.classid].lower()
        if name == 'person' or name == 'man' or name == 'woman' or  \
                name == 'boy' or name == 'girl' or 'human' in name:
            numPeople += 1
    return numPeople


CAMERA_IP = '<CAMERA IP>:<PORT>'
print('Loading Model...')
det = ObjectDetector('ssd/saved_model')
det.loadModel()
print('Model Load completed...')
print('Warming up Model...')
det.getBoundingBoxes(readImage(ip=CAMERA_IP))
det.getBoundingBoxes(readImage(ip=CAMERA_IP))

classes = loadClasses('ssd/label_mapping.csv')

app = Flask(__name__)

if __name__ == '__main__':
    image = readImage(ip=CAMERA_IP)
    numPersons = countPeople(image)
    print('Found {} people in the image!'.format(numPersons))

@app.route('/countPeople')
def getPersonCount():
    image = readImage(ip=CAMERA_IP)
    numPersons = countPeople(image)
    del image
    print('Found {} people in the image!'.format(numPersons))
    return str(numPersons)

