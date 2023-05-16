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
import os
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
        return f"{name} should be in range {min_v} up to {max_v}  in this device"
    
    def grab_error(error_code, error_description):
        return 'ERROR: error {error_code} happend! {error_description}'
    
    def error_code(error_code):
        return 'ERROR: error {error_code} happend!'
        
    def value_not_available(name, availbles):
        return f"ERROR: only {availbles} could set for {name} in this device"












# class CameraOption:
#     def __init__(self, camera_device):
#         self.camera_device = camera_device







class Camera:
    def __init__(self, camera_device: pylon.InstantCamera):
        self.camera_device = camera_device
        
        self.Infos = CameraInfo(self)
        self.Parms = CameraParms(self)
        self.Status = CameraStatus(self)
        self.Operations = CameraOperations(self)
        self.image_event_handler = CameraImageEventHandler(self)

        
        self.converter = self.build_converter(PixelType.BGR8)
        self.timeout = 5000

    
    
    

    def build_converter(self, pixel_type):
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pixel_type
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.converter = converter
        return converter

    


    def set_image_event(self, func):
        self.camera_device.GrabCameraEvents = True #enable event handler
        self.image_event_handler.set_func(func)
        self.camera_device.RegisterImageEventHandler(self.image_event_handler, pylon.RegistrationMode_Append, pylon.Cleanup_Delete)


    def software_trige_exec(self):
        self.camera_device.TriggerSoftware()
    

    def build_zero_image(self):
        _,_,h,w = self.Parms.get_roi()
        img = np.zeros((h, w, 3), dtype=np.uint8)
        return img

    

    def getPictures(self, grabResult = None, img_when_error='zero'):
        res_img = None
        #-------------------------------------------------------------
        if grabResult is None:
            if self.Status.is_grabbing():
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
    

class CameraInfo:
    def __init__(self, camera_object: Camera):
        self.camera_object = camera_object

    def get_model(self) -> str:
        return self.camera_object.camera_device.GetDeviceInfo().GetModelName()
    
    def get_serialnumber(self) -> str:
        return self.camera_object.camera_device.DeviceInfo.GetSerialNumber()
    
    def get_class(self) -> str:
        return self.camera_object.camera_device.DeviceInfo.GetDeviceClass()

    def is_PRO(self,) -> bool:
         return 'pro' in self.get_model().lower()
    
    def is_USB(self,) -> bool:
         return self.camera_object.camera_device.IsUsb()
    
    def is_GigE(self,) -> bool :
         return self.camera_object.camera_device.IsGigE()




class CameraStatus:
    def __init__(self, camera_object: Camera):
        self.camera_object = camera_object

    def is_open(self) -> bool:
        return self.camera_object.camera_device.IsOpen()
    
    def is_grabbing(self) -> bool:
        return self.camera_object.camera_device.IsGrabbing()
    
    def is_trigger_on(self,) -> bool:
        return self.camera_object.Parms.__get_value__(self.camera_object.camera_device.TriggerMode).lower() == 'on'
    
    def get_tempreture(self) -> float:
        if self.camera_object.Infos.is_PRO():
            return self.camera_object.camera_device.DeviceTemperature.GetValue()
        else:
            return self.camera_object.camera_device.TemperatureAbs.GetValue()


class CameraOperations:
    def __init__(self, camera_object: Camera):
        self.camera_object = camera_object

    def open(self):
        if not self.camera_object.Status.is_open():
            self.camera_object.camera_device.Open()
    
    def close(self):
        if self.camera_object.Status.is_open():
            self.camera_object.camera_device.Close()

    def start_grabbing(self, strategy = pylon.GrabStrategy_LatestImageOnly ):
        self.open()
        if not self.camera_object.Status.is_grabbing():
            self.camera_object.camera_device.StartGrabbing(strategy)
    
    def stop_grabbing(self):
        if self.camera_object.Status.is_grabbing():
            self.camera_object.camera_device.StopGrabbing()



class CameraParms:
    def __init__(self, camera_object: Camera):
        self.camera_object = camera_object

    def __set_value__(self, value, parameter):
        if not self.camera_object.Status.is_open():
            self.camera_object.Operations.open()
        
        if value is not None:
            if type(value) == int or type(value) == float:
                max_v = parameter.Max
                min_v = parameter.Min
                if not(min_v <= value <= max_v):
                    value = min(max(value, min_v), max_v)
                    print(ErrorAndWarnings.not_in_range(parameter.Node.Name, min_v, max_v))
            elif type(value) == str:
                if value not in self.__get_available_value__(parameter):
                    print(ErrorAndWarnings.value_not_available(parameter.Node.Name , self.__get_available_value__(parameter)))
                    return

            parameter.SetValue(value)

    
    def __get_value__(self, parameter):
        if not self.camera_object.Status.is_open():
            self.camera_object.Operations.open()
        return parameter.Value
    
    def __get_available_value__(self, parameter):
        return parameter.Symbolics
    
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


    def set_gain(self, gain: int) -> None:
        if self.camera_object.Infos.is_PRO():
            self.__set_value__(gain, self.camera_object.camera_device.Gain)
        else:
            self.__set_value__(gain, self.camera_object.camera_device.GainRaw)
    
    def get_gain(self) -> int:
        if self.camera_object.Infos.is_PRO():
            return self.__get_value__( self.camera_object.camera_device.Gain)
        else:
            return self.__get_value__( self.camera_object.camera_device.GainRaw)



    def set_exposureTime(self, exposure: int) -> None:
        if self.camera_object.Infos.is_PRO():
            self.__set_value__(exposure, self.camera_object.camera_device.ExposureTime)
        else:
            self.__set_value__(exposure, self.camera_object.camera_device.ExposureTimeAbs)
    
    def get_exposureTime(self) -> None:
        if self.camera_object.Infos.is_PRO():
            return self.__get_value__( self.camera_object.camera_device.ExposureTime)
        else:
            return self.__get_value__(self.camera_object.camera_device.ExposureTimeAbs)


    def set_roi(self, height: int, width: int, offset_x: int, offset_y: int) -> None:
        grabbing = False
        if self.camera_object.Status.is_grabbing():
            self.camera_object.Operations.stop_grabbing()
            grabbing = True
        self.__set_value__(width, self.camera_object.camera_device.Width)
        self.__set_value__(height, self.camera_object.camera_device.Height)
        self.__set_value__(offset_x, self.camera_object.camera_device.OffsetX)
        self.__set_value__(offset_y, self.camera_object.camera_device.OffsetY)

        if grabbing:
            self.camera_object.Operations.start_grabbing()

    
    def get_roi(self,) -> tuple[ int, int, int, int]:
        w = self.__get_value__( self.camera_object.camera_device.Width)
        h = self.__get_value__( self.camera_object.camera_device.Height)
        offset_x = self.__get_value__( self.camera_object.camera_device.OffsetX)
        offset_y = self.__get_value__( self.camera_object.camera_device.OffsetY)
        return offset_x, offset_y, h, w

    
    def set_trigger_option(self, source: str, selector = Trigger.selector.frame_start) -> None:
        self.set_trigger_on()
        self.__set_value__(source, self.camera_object.camera_device.TriggerSource)
        self.__set_value__(selector, self.camera_object.camera_device.TriggerSelector)

    def get_trigger_option(self) -> tuple[str, str]:
        source = self.__get_value__(self.camera_object.camera_device.TriggerSource)
        selector = self.__get_value__(self.camera_object.camera_device.TriggerSelector)
        return source, selector
    
    def availble_triggersource_values(self):
        return self.__get_available_value__(self.camera_object.camera_device.TriggerSelector)
    
    def availble_triggerselector_values(self):
        return self.__get_available_value__(self.camera_object.camera_device.TriggerSelector)


    def set_trigger_on(self) -> None:
        self.__set_value__('On', self.camera_object.camera_device.TriggerMode)
        

    def set_trigger_off(self) -> None:
        self.__set_value__('Off', self.camera_object.camera_device.TriggerMode)

    def get_trigger_mode(self) -> str:
        return self.__get_value__(self.camera_object.camera_device.TriggerMode)

    def set_bandwith(self,):
        #fps = bandwidth / payload_size
        pass

    def set_transportlayer(self,packet_delay, packet_size = None) -> None:
        self.__set_value__(packet_size, self.camera_object.camera_device.GevSCPSPacketSize)
        self.__set_value__(packet_delay, self.camera_object.camera_device.GevSCPD)



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










class Collector:
    def __init__(
        self,
        camera_class = None,
    ):
        self.camera_class = camera_class

        self.__tl_factory = pylon.TlFactory.GetInstance()
        # ----------------------------------------------------------
        self.devices = self.get_available_devices(self.camera_class)
        self.cameras = None
        #assert self.devices, ErrorAndWarnings.no_devices()
        # ----------------------------------------------------------
    def enable_camera_emulation(self, count):
        os.environ['PYLON_CAMEMU'] = str(count)

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


    def get_camera_by_serial(self, serial_number) -> Camera:
        self.devices = self.get_available_devices(None)
        for device in self.devices:
            camera = pylon.InstantCamera(self.__tl_factory.CreateDevice(device))
            if camera.GetDeviceInfo().GetSerialNumber() == serial_number:
                return Camera(camera)
        return None

    def get_all_cameras(self, camera_class=None) -> list[Camera]:
        self.devices = self.get_available_devices(None)
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









if __name__ == "__main__":
    collector = Collector()
    collector.enable_camera_emulation(2)
    cameras = collector.get_all_cameras(camera_class=CamersClass.emulation)
    cam1 = cameras[0]
    #-----------------------------------------------------------------
    cam1.Parms.set_gain(50)
    cam1.Operations.start_grabbing()
    cam1.Parms.set_trigger_option(Trigger.source.hardware_line1, Trigger.selector.frame_start)
    #-----------------------------------------------------------------
    pass
    #a = pylon.InstantCamera()
    #x = pylon.InstantCamera()
