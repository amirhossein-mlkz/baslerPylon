"""
########################################
---------------------------------------

Made with Malek & Milad

Features:

    ● Create Unlimite Object of Cameras and Live Preview By serial number
    ● Set Bandwitdh Of each Cameras
    ● Set gain,exposure,width,height,offet_x,offset_y
    ● Get tempreture of Cmeras
    ● Set Trigger Mode on
    ● There are Some diffrents between ace2(pro) and ace

---------------------------------------
########################################
"""
from pypylon import pylon
from PylonFlags import CamersClass, Trigger, PixelType
import cv2
import time
import numpy as np
import threading

from pypylon import genicam
'''
                         !تذکر
از قرار دادن هرگونه اسد و پرینت اروووررررر جدا خودداری فرمایید
            حتی شما مدیر پروژه عزیز اکسین
'''
# 



'''
bandwidth manager
USB camera
offset_x , offset_y
'''

DEBUG = False
show_eror = False


class ErrorAndWarnings:
    def no_devices():
        return "ERROR: No Devices founded"
    def not_grabbing():
        return "ERROR: Camera is not Grabbing"

    def not_in_range(name, min_v, max_v):
        return f"{name} should be in range {min_v} up to {max_v}"
    
    def grab_error(error_code, error_description):
        return 'ERROR: error {error_code} happend! {error_description}'
    
    def error_code(error_code):
        return 'ERROR: error {error_code} happend!'
        
        





class Collector:
    def __init__(
        self,
        camera_class,
    ):
        self.camera_class = camera_class

        self.__tl_factory = pylon.TlFactory.GetInstance()
        # ----------------------------------------------------------
        self.devices = self.get_available_devices(self.camera_class)
        self.cameras = None
        assert self.devices, ErrorAndWarnings.no_devices()
        # ----------------------------------------------------------

    def get_available_devices(self, camera_class=None):
        founded_devices = []
        for device in self.__tl_factory.EnumerateDevices():
            if device.GetDeviceClass() == camera_class or camera_class is None:
                founded_devices.append(device)
        return founded_devices
    
    def listDevices(self):
        cameras = self.get_all_cameras()
        for i, camera in enumerate(cameras):
            device_info = camera.GetDeviceInfo()
            print(
                "Camera #%d %s @ %s (%s) @ %s"
                % (
                    i,
                    device_info.GetModelName(),
                    device_info.GetIpAddress(),
                    device_info.GetMacAddress(),
                    device_info.GetSerialNumber(),
                )
            )


    def get_camera_by_serial(self, serial_number):
        for device in self.devices:
            camera = pylon.InstantCamera(self.__tl_factory.CreateDevice(device))
            if camera.GetDeviceInfo().GetSerialNumber() == serial_number:
                return Camera(camera)
        return None

    def get_all_cameras(self, camera_class=None):
        cameras = []
        for device in self.devices:
            if camera_class is None or device.GetDeviceClass() == camera_class:
                cameras.append(
                    Camera(pylon.InstantCamera(self.__tl_factory.CreateDevice(device)))
                )

        return cameras
    

    def get_all_serials(self,):
        cameras = self.get_all_cameras()
        serial_list = []
        for cam in cameras:
            device_info = cam.GetDeviceInfo()
            serial_list.append(device_info.GetSerialNumber())
        return serial_list









class CameraInfo:
    def __init__(self, camera_device):
        self.camera_device = camera_device

    def get_model(
        self,
    ):
        return self.camera_device.GetDeviceInfo().GetModelName()

    def is_PRO(self):
        return "PRO" in self.get_model()


# class CameraOption:
#     def __init__(self, camera_device):
#         self.camera_device = camera_device







class Camera:
    def __init__(self, camera_device: pylon.InstantCamera):
        self.camera_device = camera_device
        #self.info = CameraInfo(self.camera_device)
        self.model = self.camera_device.GetDeviceInfo().GetModelName()
        self.image_event_handler = CameraImageEventHandler(self)
        self.converter = self.build_converter(PixelType.BGR8)
        self.timeout = 5000


    def set_all_parms(
        self,
        gain=None,
        exposure=None,
        width=None,
        height=None,
        offset_x=None,
        offset_y=None,
        trigger=None,
        trigge_source=None,
        trigge_selector = None
        #max_buffer=20,
        #delay_packet=100,
        #packet_size=1500,
        #frame_transmission_delay=0,
        
    ):
        self.set_gain(gain)
        self.set_exposureTime(exposure)
        self.set_trigger_option(trigge_source, trigge_selector)
        self.set_roi(height, width, offset_x, offset_y )
        if trigger:
            self.set_trigger_on()
        else:
            self.set_trigger_off()
        #self.max_buffer = max_buffer
        #self.cont_eror = 0
        #self.trigger = trigger
        #self.dp = delay_packet
        #self.ps = packet_size
        #self.ftd = frame_transmission_delay
        #self.exitCode = 0

    def __set_value__(self, value, parameter):
        if not self.is_open():
            self.open()
        
        if value is not None:
            if type(value) == int or type(value) == float:
                max_v = parameter.Max
                min_v = parameter.Min
                if not(min_v <= value <= max_v):
                    value = min(max(value, min_v), max_v)
                    ErrorAndWarnings.not_in_range(parameter.Node.Name, min_v, max_v)
            parameter.SetValue(value)

    
    def __get_value__(self, parameter):
        return parameter.GetValue()
    


    def is_open(self):
        return self.camera_device.IsOpen()
    
    def is_grabbing(self):
        return self.camera_device.IsGrabbing()
    
    def open(self):
        if not self.is_open():
            self.camera_device.Open()

    def start_grabbing(self, strategy = pylon.GrabStrategy_LatestImageOnly ):
        self.open()
        if self.is_grabbing():
            self.camera_device.StartGrabbing(strategy)
    
    def stop_grabbing(self):
        if self.is_grabbing():
            self.camera_device.StopGrabbing()

    def is_PRO(self,):
         model = self.camera.GetDeviceInfo().GetModelName()
         return 'pro' in model.lower()

    
    
    def set_gain(self, gain):
        if self.is_PRO():
            self.__set_value__(gain, self.camera_device.Gain)
        else:
            self.__set_value__(gain, self.camera_device.GainRaw)
    
    def get_gain(self):
        if self.is_PRO():
            return self.__get_value__( self.camera_device.Gain)
        else:
            return self.__get_value__( self.camera_device.GainRaw)



    def set_exposureTime(self, exposure):
        if self.is_PRO():
            self.__set_value__(exposure, self.camera_device.ExposureTime)
        else:
            self.__set_value__(exposure, self.camera_device.ExposureTimeAbs)
    
    def get_exposureTime(self):
        if self.is_PRO():
            return self.__get_value__( self.camera_device.ExposureTime)
        else:
            return self.__get_value__(self.camera_device.ExposureTimeAbs)


    def set_roi(self, height, width, offset_x, offset_y):
        grabbing = False
        if self.is_grabbing():
            self.stop_grabbing()
            grabbing = True
        self.__set_value__(width, self.camera_device.Width)
        self.__set_value__(height, self.camera_device.Height)
        self.__set_value__(offset_x, self.camera_device.offset_x)
        self.__set_value__(offset_y, self.camera_device.offset_y)

        if grabbing:
            self.start_grabbing()

    
    def get_roi(self,):
        self.stop_grabbing()

        w = self.__get_value__( self.camera_device.Width)
        h = self.__get_value__( self.camera_device.Height)
        offset_x = self.__get_value__( self.camera_device.offset_x)
        offset_y = self.__get_value__( self.camera_device.offset_y)
        return offset_x, offset_y, h, w

    
    def set_trigger_option(self, source, selector = Trigger.selector.frame_start):
        self.set_trigger_on()
        self.__set_value__(source, self.camera_device.TriggerSource)
        self.__set_value__(selector, self.camera_device.TriggerSelector)

    def get_trigger_option(self):
        source = self.__get_value__(self.camera_device.TriggerSource)
        selector = self.__get_value__(self.camera_device.TriggerSelector)
        return source, selector


    def set_trigger_on(self):
        self.__set_value__('On', self.camera_device.TriggerMode)
        

    def set_trigger_off(self):
        self.__set_value__('Off', self.camera_device.TriggerMode)

    def is_trigger_on(self,):
        return self.__get_value__(self.camera_device.TriggerMode).lower() == 'on'


    def set_bandwith(self,):
        #fps = bandwidth / payload_size
        pass

    def set_transportlayer(self,packet_delay, packet_size = None):
        self.__set_value__(packet_size, self.camera_device.GevSCPSPacketSize)
        self.__set_value__(packet_delay, self.camera_device.GevSCPD)

    
    def set_timeout(self, timeout):
        self.timeout = timeout
    

    def build_converter(self, pixel_type):
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pixel_type
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.converter = converter
        return converter

    def get_tempreture(self):
        if self.is_PRO():
            return self.camera_device.DeviceTemperature.GetValue()
        else:
            return self.camera_device.TemperatureAbs.GetValue()


    def set_image_event(self, func):
        self.camera_device.GrabCameraEvents = True #enable event handler
        self.image_event_handler.set_func(func)
        self.camera_device.RegisterImageEventHandler(self.image_event_handler, pylon.RegistrationMode_Append, pylon.Cleanup_Delete)


    def software_trige_exec(self):
        self.camera_device.TriggerSoftware()
    

    def build_zero_image(self):
        _,_,h,w = self.get_roi()
        img = np.zeros((h, w, 3), dtype=np.uint8)
        return img

    

    def getPictures(self, grabResult = None, img_when_error='zero'):
        res_img = None
        #-------------------------------------------------------------
        if grabResult is None:
            if self.is_grabbing():
                grabResult = self.camera_device.RetrieveResult(self.timeout, pylon.TimeoutHandling_ThrowException)
            else:
                print(ErrorAndWarnings.not_grabbing())
        #-------------------------------------------------------------
        if grabResult is not None and grabResult.GrabSucceeded():
            image = self.converter.Convert(grabResult)
            res_img = image.Array
        else:
            print( ErrorAndWarnings.grab_error(grabResult.ErrorCode, grabResult.ErrorDescription))
        #-------------------------------------------------------------
        if res_img is None:
            if img_when_error == 'zero':
                res_img = self.build_zero_image()

        return res_img
    
    

class CameraImageEventHandler(pylon.ImageEventHandler):
    def __init__(self,camera : Camera, *args):
        super().__init__(*args)
        self.event_func = None
        self.camera = camera

    def set_func(self, func):
        self.event_func = func

    def OnImageGrabbed(self, camera, grabResult):
        print("CameraImageEventHandler.OnImageGrabbed called.")
        img = self.camera.getPictures(grabResult)
        if self.event_func is not None:
            self.event_func(img)



def get_threading(cameras):
    def thread_func():
        for cam in cameras:
            cam.trigg_exec()
        for cam in cameras:
            img = cam.getPictures()
            cv2.imshow("img", cv2.resize(img, None, fx=0.5, fy=0.5))
            cv2.waitKey(10)

        t = threading.Timer(0.330, thread_func)
        t.start()

    return thread_func


if __name__ == "__main__":
    #collector = Collector(CamersClass.gige)
    #cameras = collector.get_all_cameras()

    a = pylon.InstantCamera()
    x = pylon.InstantCamera()
