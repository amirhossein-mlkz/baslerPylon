import sys
import os
sys.path.append( os.getcwd())


import dorsaPylon
from dorsaPylon import Collector, Camera
import numpy as np
import cv2


collector = Collector()
#enable camera emulation and pass your ideal camera counts
collector.enable_camera_emulation(1)
#get avialble cameras in class of emlulation
camera = collector.get_all_cameras(camera_class=None)[0]
#-----------------------------------------------------------------
#define your ideal pixel_type, defualt is BGR8
camera.build_converter(pixel_type=dorsaPylon.PixelType.GRAY8)

#Optional if you want custom error image
#camera.set_error_image(np.zeros((100,100), dtype=np.uint8))
#-----------------------------------------------------------------
camera.Operations.start_grabbing()
for i in range(100):
    ret,img,status = camera.getPictures()
    print('success fps:', camera.Status.get_success_fps())
    print('running fps:', camera.Status.get_running_fps())
    print('camera fps:', camera.Status.get_camera_fps())
    print('-----------------------------------------')
    cv2.imshow('img', img)
    cv2.waitKey(100)
    
