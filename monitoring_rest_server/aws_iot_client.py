import json
from time import sleep
import sys
import atexit
from aws_iot_utils import *

def getCurrentShadowCallback(asyncToSync, payload, status, token):
    # printState(payload, status, token)
    result = json.loads(payload)
    reportedState = result['state']['reported']
    asyncToSync.result = ShadowState(reportedState['numLightsOn'], reportedState['currentLdrReading'], reportedState['opMode'])
    asyncToSync.event.set()

def getCurrentShadow(deviceShadow):
    callback = AsyncToSync(getCurrentShadowCallback)
    deviceShadow.shadowGet(callback.getCallback(), 10)
    return callback.getResult()

def updateShadowCallback(asyncToSync, payload, status, token):
    printState(payload, status, token)
    if not status == 'accepted':
        asyncToSync.result = 'Failed'
    asyncToSync.event.set()

def updateShadow(shadow, newState):
    updatePayload = { 'state': {
        'desired' : {
            'opMode' : newState
            }
        }
    }

    callback = AsyncToSync(updateShadowCallback)
    print('Calling update with payload: {}'.format(json.dumps(updatePayload)))
    shadow.shadowUpdate(json.dumps(updatePayload), callback.getCallback(), 10)
    return callback.getResult()

clientId = 'raspberryPi_Client'
if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('Syntax: {} get-state|update-mode [auto|manual|on|off]'.format(args[0]))
        exit(1)

    shadowClient = getShadowClient(clientId=clientId)
    if not shadowClient:
        print('Failed to connect to AWS IOS device')
        exit(1)

    shadow = shadowClient.createShadowHandlerWithName(device, False)
    atexit.register(shutdown, shadowClient)
    if args[1] == 'get-state':
        print(getCurrentShadow(shadow))
    elif args[1] == 'update-state':
        if not len(args) == 3:
            print('Invalid arguments. New mode required. Only One of manual|auto|on|off must be specified')
            exit(1)
        print('Attempting to set operation mode to {}'.format(args[2]))
        updateShadow(shadow, args[2])
    else:
        print('Invalid arguments. One of <get-state|update-state> need to be specified')
        exit(1)
