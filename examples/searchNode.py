import dorsaPylon
from dorsaPylon import Collector, Camera
import cv2


collector = Collector()
collector.enable_camera_emulation(2)
cameras = collector.get_all_cameras(camera_class=dorsaPylon.CamersClass.emulation)
cam1 = cameras[0]
#-----------------------------------------------------------------
nodes_name = cam1.search_in_nodes('gain')

