import cv2
import cv2.dnn as dnn
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask

def get_output_layers(net):    
    layer_names = net.getLayerNames()    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

# function to draw bounding box on the detected object with class name
def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h, classes=[]):
    label = ''
    if len(classes) > 0:
        label = str(classes[class_id])
    
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), 1, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 4)

def loadModel(conf, weights):
    return dnn.readNet(conf, weights)

def loadClassNames(filename):
    classes = []
    with open(filename) as f:
        classes = list(map(lambda x: x.strip(), f.readlines()))
        f.close()
    return classes

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

def classifyImage(net, image):
    blob = dnn.blobFromImage(image, 1/255, (416,416), (0,0,0), True, crop=False)
    net.setInput(blob)
    return net.forward(get_output_layers(net))

def getBoundingBoxes(outs, width, height, conf_threshold = 0.8, nms_threshold=0.45):
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = (center_x - w/2.0)
                y = (center_y - h/2.0)
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    return class_ids, confidences, boxes

def drawBoundingBoxesToImage(test, boxes, confidences, classes, class_ids, conf_threshold, nms_threshold):
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    bboxes = []

    for i in indices:
        i = i[0]
        box = boxes[i]
        x = round(box[0])
        y = round(box[1])
        w = box[2]
        h = box[3]

        print(classes[class_ids[i]])
        draw_bounding_box(test, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h), classes)
        bboxes.append(image[y:y+h, x:w+x])
    plt.imshow(test)

def countPeople(net, image, classes, person_class):
    width = image.shape[1]
    height = image.shape[0]
    conf_threshold = 0.1
    nms_threshold=0.45
    outs = classifyImage(net, image)
    class_ids,confidences,boxes = getBoundingBoxes(outs, width, height, conf_threshold=conf_threshold, nms_threshold=nms_threshold)
    drawBoundingBoxesToImage(image, boxes, confidences, classes, class_ids, conf_threshold=conf_threshold, nms_threshold=nms_threshold)
    
    return len(list(filter(lambda x: x == person_class, class_ids)))


net = loadModel('cfg/yolov3.cfg', 'yolov3.weights')
classes = loadClassNames('data/coco.names')
CAMERA_IP='192.168.1.2:8080'
# net = loadModel('cfg/darknet19.cfg', 'darknet19.weights')
# classes = loadClassNames('imagenet.shortnames.list')

app = Flask(__name__)

if __name__ == '__main__':
    image = readImage(ip=CAMERA_IP)

    numPersons = countPeople(net, image, classes, 0)
    print('Found {} people in the image!'.format(numPersons))
    

@app.route('/countPeople')
def getPersonCount():
    image = readImage(ip=CAMERA_IP)

    numPersons = countPeople(net, image, classes, 0)
    print('Found {} people in the image!'.format(numPersons))
    # plt.show()
    return { 'numPersons': numPersons }

