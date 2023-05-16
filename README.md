# Steup
◌Instructions:<br />
  &emsp;1-pip install pypylon <br />
  &emsp;2-connect your basler camera <br />
  &emsp;3-open final_pypylon.py <br />
  &emsp;4-set your serial number and details <br />
  &emsp;5-Enjoy it! <br />

# Step1: Get Devices And Camera
you can get cameras in two ways, by the `get_all_cameras` function or `get_camera_by_serial` .
the `get_all_cameras` function, get your ideal camera class like GigE, USB and etc. If pass `camera_class` argument None, it returns all cameras in different classes
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
