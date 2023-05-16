# Steup
◌Instructions:<br />
  &emsp;1-pip install pypylon <br />
  &emsp;2-connect your basler camera <br />
  &emsp;3-open final_pypylon.py <br />
  &emsp;4-set your serial number and details <br />
  &emsp;5-Enjoy it! <br />

# Step1: Get Devices And Camera
you can get cameras in two ways, by the `get_all_cameras` function or `get_camera_by_serial` .
the `get_all_cameras` function, return list of available cameras in your ideal camera class like GigE, USB and etc. If pass `camera_class` argument None, it returns all cameras in different classes
``` python
import dorsaPylon
from dorsaPylon import Collector, Camera

collector = Collector()

#get avialble cameras That Are GigE
gige_cameras = collector.get_all_cameras(camera_class=dorsaPylon.CamersClass.gige)

#-----------------------------------------------------------------
#get all avialble cameras 
all_cameras = collector.get_all_cameras(camera_class=None)

#-----------------------------------------------------------------
#get specific camera
cam = collector.get_camera_by_serial('123456')
```
# Camera Functions
`Infoes` attribute is used for showing all camera information like serial number and model
``` python
model = camera.Infos.get_model()
print(f'model: {model}')

serial = camera.Infos.get_serialnumber()
print(f'serial: {serial}')

is_gige = camera.Infos.is_GigE()
print(f'is camera GigE: {is_gige}')
```
results:
```
model: Emulation
serial: 0815-0000
is camera GigE: False
```

The `Parms` attribute is used to set all camera parameters like gain and exposure. you can also use this attribute to read parameters from the camera
``` python
#-----------------------------------------------------------------
#Parms is useing for set camera options
camera.Parms.set_gain(50)
gain = camera.Parms.get_gain()
print(f'gain is {gain}')

camera.Parms.set_trigger_on()
trigger = camera.Parms.get_trigger_mode()
print(f'trgigger is {trigger}')
#----------------------------------------------------------------
```
results:
```
GainRaw should be in range 192 up to 1023  in this device
gain is 192
trgigger is On
```

