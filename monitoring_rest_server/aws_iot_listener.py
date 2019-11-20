import json
from time import sleep
import sys
import os
import atexit
from aws_iot_utils import *
from aws_iot_client import getCurrentShadow

def terminate(event, payload, status, token):
    print('Terminating Update Workflow')
    # printState(payload, status, token)
    event.event.set()

def getNumLightsOn():
    fileName = 'smd0'
    filePath = '../raw/{}'.format(fileName)
    if not os.path.exists(filePath):
        filePath = 'raw/{}'.format(fileName)

    numOn = 0
    with open(filePath) as f:
        val = f.read()
        if int(val, 16) > 0:
            numOn += 1
        f.close()

    return numOn

def getCurrentLdrReading():
    fileName = 'ldr0'
    filePath = '../raw/{}'.format(fileName)
    if not os.path.exists(filePath):
        filePath = 'raw/{}'.format(fileName)

    ldrVal = 0.
    with open(filePath) as f:
        ldrVal = float(f.read())
        f.close()

    return ldrVal

def updateShadow(deviceShadow, currentShadow, newMode):
    if not newMode:
        newMode = currentShadow.opMode

    newReported = {}
    newReported['opMode'] = newMode
    newReported['numLightsOn'] = str(getNumLightsOn())
    newReported['currentLdrReading'] = '{:.2f}'.format(getCurrentLdrReading())

    newState = {}
    newState['desired'] = None
    newState['reported'] = newReported

    newShadow = {}
    newShadow['state'] = newState

    print('Updating Device Shadow. New Payload: {}'.format(json.dumps(newShadow)))
    callback = AsyncToSync(terminate)
    deviceShadow.shadowUpdate(json.dumps(newShadow), callback.getCallback(), 10)
    return callback.getResult()

def updateState(newState):
    if newState == None:
        return

    fileName = 'opMode'
    filePath = '../raw/{}'.format(fileName)
    if not os.path.exists(filePath):
        filePath = 'raw/{}'.format(fileName)

    with open(filePath, 'w') as f:
        f.write(newState)
        f.close()

# Callback function
def deltaHandler(asyncToSync, deviceShadow, payload, status, token):
    print('New Delta Found')
    # printState(payload, status, token)
    request = json.loads(payload)
    state = request['state']
    newMode = None
    invalidReq = False
    validStates = ['auto', 'manual', 'off', 'on']
    if 'numLightsOn' in state:
        print('Invalid Requested value for numLightsOn: {}'.format(state['numLightsOn']))
        invalidReq = True

    newModeNum = None
    if 'opMode' in state:
        print('Requested value for opMode: {}'.format(state['opMode']))
        newMode = state['opMode'].lower()
        if not newMode in validStates:
            invalidReq = True
            print('Invalid request for state: {}, States should be one of {}'.format(newMode, validStates))
            newMode = None
        else:
            newModeNum = str(validStates.index(newMode))

    if 'currentLdrReading' in state:
        print('Invalid Requested value for currentLdrReading: {}'.format(state['currentLdrReading']))
        invalidReq = True

    if invalidReq:
        print('Some/all requested changes are Invalid. Will retain only valid changes')

    # Open file for state, write state
    updateState(newModeNum)

    # Update device shadow
    curState = getCurrentShadow(deviceShadow)
    res = updateShadow(deviceShadow, curState, newMode)
    print('Updated Device Shadow with result: {}'.format(res))
    asyncToSync.event.set()

clientId = 'raspberryPi_Server'
if __name__ == '__main__':
    timeout = 10 # secs
    shadowClient = getShadowClient(clientId=clientId)
    if not shadowClient:
        print('Failed to connect AWS IOT device')
        exit(1)

    shadow = shadowClient.createShadowHandlerWithName(device, False)
    atexit.register(shutdown, shadowClient)

    while True:
        callback = AsyncToSync(deltaHandler)
        callback.addArgument(shadow)
        shadow.shadowRegisterDeltaCallback(callback.getCallback())
        print('Registered for callbacks, waiting...')
        callback.getResult()
