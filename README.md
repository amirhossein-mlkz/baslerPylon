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
## Infoes
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
## Parms
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
## Status
The `status` attribute is used to get the status of the camera like camera grabbing status or is camera open or not and also stuff like camera temperature
``` python
camera.Operations.open()
is_open = camera.Status.is_open()
print(f'camera is open:{is_open}')

camera.Operations.start_grabbing()
is_grabbing = camera.Status.is_grabbing()
print(f'camera is grabbing:{is_grabbing}')

trigg_status = camera.Status.is_trigger_on()
print(f'trigger:{trigg_status}')
```
results:
```
camera is open:True
camera is grabbing:True
```

# Grab Image
for grabbing images, you can easily use the `getPictures` method. if you need to change pixel type, for example when you using a mono camera, you can change pixel type by the `build_converter` function. see example

``` python
#define your ideal pixel_type, defualt is BGR8
camera.build_converter(pixel_type=dorsaPylon.PixelType.GRAY8)
#-----------------------------------------------------------------
img = camera.getPictures()
cv2.imshow('img', img)
cv2.waitKey(0)
```

# Camera Emulation
this library support camera emulation. To enable camera emulation you can use the `enable_camera_emulation` method in the `Collector` class. you should pass the number of cameras that you want into this method. after calling this method, camera emulation would be added to the list of devices

``` python 
collector = Collector()
#enable camera emulation and pass your ideal camera counts
collector.enable_camera_emulation(2)
#get avialble cameras in class of emlulation
cameras = collector.get_all_cameras(camera_class=dorsaPylon.CamersClass.emulation)
cam1 = cameras[0]
#-----------------------------------------------------------------
cam1.Parms.set_gain(50)
cam1.Operations.start_grabbing()
```

