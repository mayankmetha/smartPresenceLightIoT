import cv2
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask
from object_detection import ObjectDetector
from aws_iot_client import getCurrentShadow, updateShadow
import aws_iot_utils
from aws_iot_utils import *
import json

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
                name == 'clothing' or name == 'boy' or name == 'girl' or 'human' in name:
            numPeople += 1
    return numPeople

clientId = 'raspberryPi_Rest_Server'
certPath = '../certs'

rootCa='{}/AmazonRootCA1.pem'.format(certPath)
private_key='{}/thing_private_key.pem.key'.format(certPath)
certificate='{}/thing_cert.pem.crt'.format(certPath)

shadowClient = getShadowClient(clientId=clientId, rootCa=rootCa, private_key=private_key, certificate=certificate)
if not shadowClient:
    print('Failed to connect to AWS IOT device')
    exit(1)

deviceShadow = shadowClient.createShadowHandlerWithName(device, False)

CAMERA_IP = '<CAMERA IP>:<PORT>'
print('Loading Model...')
det = ObjectDetector('ssd/saved_model')
det.loadModel()
print('Model Load completed...')
print('Warming up Model...')
det.getBoundingBoxes(readImage(ip=CAMERA_IP))
det.getBoundingBoxes(readImage(ip=CAMERA_IP))

classes = loadClasses('ssd/label_mapping.csv')

app = Flask(__name__,static_url_path='')

if __name__ == '__main__':
    image = readImage(ip=CAMERA_IP)
    numPersons = countPeople(image)
    print('Found {} people in the image!'.format(numPersons))

@app.route('/')
def loadUi():
    return app.send_static_file('index.html')

@app.route('/countPeople')
def getPersonCount():
    image = readImage(ip=CAMERA_IP)
    numPersons = countPeople(image)
    del image
    print('Found {} people in the image!'.format(numPersons))
    return str(numPersons)

@app.route('/getShadow')
def getShadow():
    shadow = getCurrentShadow(deviceShadow)
    return shadow._asdict()

@app.route('/updateOpMode/<newMode>')
def updateMode(newMode):
    res = updateShadow(deviceShadow, newMode)
    if res:
        print('Failed to update shadow: {}'.format(res))
    return str(res)
