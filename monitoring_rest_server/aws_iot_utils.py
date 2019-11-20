from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import threading
import functools
from collections import namedtuple
import json

ShadowState = namedtuple('ShadowState', 'numLightsOn currentLdrReading opMode')

host = '<AWS IOT Thing Host Name>'
certPath = "certs"
device = '<Device Name>'
clientId = 'raspberry-pi_1'

class AsyncToSync:
    def __init__(self, callback):
        '''
            Callback must be of the signature:
                callbackfn(AsyncToSyncObj, payload, status, token)
            Callback should set any results in to AsyncToSyncObj.result
            Once all is done, don't forget to call AsyncToSyncObj.event.set() in the callback
        '''
        self.event = threading.Event()
        self.callback = callback
        self.result = None
        self.args = []

    def addArgument(self, arg):
        self.args.append(arg)

    def getCallback(self):
        if len(self.args) == 0:
            return functools.partial(self.callback, self)
        return functools.partial(self.callback, self, self.args[0])

    def getResult(self):
        self.event.wait()
        return self.result

def getShadowClient(host=host, port=8883, device=device,
                    clientId=clientId,
                    rootCa='{}/AmazonRootCA1.pem'.format(certPath),
                    private_key='{}/thing_private_key.pem.key'.format(certPath),
                    certificate='{}/thing_cert.pem.crt'.format(certPath)):
    # Init AWSIoTMQTTClient
    myAWSIoTMQTTClient = None
    myAWSIoTMQTTClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCa, private_key, certificate)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    if not myAWSIoTMQTTClient.connect():
        return None

    return myAWSIoTMQTTClient

def shutdown(shadowClient):
    print('Disconnecting from Shadow Client')
    shadowClient.disconnect()

# Callback function
def printState(payload, status, token):
    res = json.dumps(json.loads(payload), indent=4, sort_keys=True)
    print('Request completed with status: {}\nResponse: {}'.format(status, res))
