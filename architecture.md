Adjust alpacaClass.py to a single loop which processes setting and getting properties from alpaca.
The loop is a worker thread which is started with startCommunications and stopped with stopCommunications
there should be only one worker thread left
no timer should be used ans the polling time should be reflected in the cycle time of the loop
the loop also handles a command queue queue.Queue() which is used to send commands to the device. The loop will process the commands in the queue and execute them accordingly. 
Inside the loop the following task shoud be covered:
- try to connect the selected device
- when the device is connected getInitialConfig once
- check continiously if the device is still connected and emit signal deviceConnected deviceDisconnected
- call the polling routine to get the necessary data for the connected device.
- the polling routine is empty as it will be overloaded from the underlying devices classes.
- commands calling from the queue.
- the setDeviceProp getDeviceProp callDeviceMethod will stay and should be used as an interface to alpyca lib
- as the loop handles device connected, we can omit the self.deviceConnected guard in each call.
the createAlpacaDevice should be called and handled outside the loop from startCommunications.
the new class should be an edited version of alpacaClass.py
self.propertyExceptions are not needed anymore, we keep polling also not implemented interfaces
