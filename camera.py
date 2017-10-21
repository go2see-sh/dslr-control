import Image
import ctypes
import logging
import os
import threading
import cv2
import numpy as np

from _ctypes import POINTER
from cStringIO import StringIO

from camera_preset import CameraPreset
from config import Config

gp = ctypes.CDLL('libgphoto2.so.6')

gp.gp_context_new.restype = ctypes.c_void_p

# gphoto2-result.h
# gphoto constants
GP_OK = 0
GP_ERROR = -1
GP_ERROR_BAD_PARAMETERS = -2 
GP_ERROR_NO_MEMORY = -3
GP_ERROR_LIBRARY = -4
GP_ERROR_UNKNOWN_PORT = -5
GP_ERROR_NOT_SUPPORTED = -6
GP_ERROR_IO = -7
GP_ERROR_FIXED_LIMIT_EXCEEDED = -8
GP_ERROR_TIMEOUT = -10
GP_ERROR_IO_SUPPORTED_SERIAL = -20
GP_ERROR_IO_SUPPORTED_USB = -21
GP_ERROR_IO_INIT = -31
GP_ERROR_IO_READ = -34
GP_ERROR_IO_WRITE = -35
GP_ERROR_IO_UPDATE = -37
GP_ERROR_IO_SERIAL_SPEED = -41
GP_ERROR_IO_USB_CLEAR_HALT = -51
# CameraCaptureType enum in 'gphoto2-camera.h'
GP_CAPTURE_IMAGE = 0
GP_CAPTURE_MOVIE = 1
GP_CAPTURE_SOUND = 2
# CameraFileType enum in 'gphoto2-file.h'
GP_FILE_TYPE_PREVIEW = 2
GP_FILE_TYPE_NORMAL = 1
GP_FILE_TYPE_RAW = 4
GP_FILE_TYPE_AUDIO = 5
GP_FILE_TYPE_EXIF = 6
GP_FILE_TYPE_METADATA = 7


class CameraFilePath(ctypes.Structure):
    _fields_ = [('name', (ctypes.c_char * 128)),
                ('folder', (ctypes.c_char * 1024))]


# http://gphoto.org/doc/remote/
class Camera:

    def __init__(self):
        self.lock = threading.Lock()
        self.camera = None
        self.preview_file = ctypes.c_void_p()
        self.context = ctypes.c_void_p(gp.gp_context_new())
        gp.gp_file_new(ctypes.byref(self.preview_file))
        self.liveview_enabled = False
        self.focuspeak_enabled = False

    def connect(self):
        if self.camera is not None:
            return

        self.camera = ctypes.c_void_p()
        gp.gp_camera_new(ctypes.byref(self.camera))
        retval = gp.gp_camera_init(self.camera, self.context)
        if retval != GP_OK:
            logging.error('Unable to connect %s', retval)
        else:
            print 'Camera connected'
            self.enable_canon_capture(1)
            self.set_capture_mode('Memory card') # save on camera sdcard

    def disconnect(self):
        if self.camera != None:
            gp.gp_camera_exit(self.camera, self.context)
            gp.gp_camera_unref(self.camera)
            self.camera = None
            self.enable_canon_capture(0)
        print 'Disconnected'

    def enable_canon_capture(self, enabled):
        try:
            config = Config(self)
            widget = config.get_root_widget().get_child_by_name('capture')
            widget.set_value(enabled)
            config.set_config()
        except:
            pass

    def get_config_widget(self, name):
        try:
            config = Config(self)
            return (config, config.get_root_widget().get_child_by_name(name))
        except:
            pass

    def set_config_widget_value(self, name, value):
        try:
            self.lock.acquire()
            (config, widget) = self.get_config_widget(name)
            choises = widget.get_choices()
            if value in choises:
                widget.set_value(value)
                config.set_config()
        except Exception as ex:
            print ex
        finally:
            self.lock.release()

    def set_config_widget_value_by_index(self, name, index):
        try:
            self.lock.acquire()
            (config, widget) = self.get_config_widget(name)
            choises = widget.get_choices()
            if index < len(choises) and index > -1:
                widget.set_value(choises[index])
                config.set_config()
        except Exception as ex:
            print ex
        finally:
            self.lock.release()

    def get_config_widget_options(self, name):
        try:
            self.lock.acquire()
            widget = self.get_config_widget(name)
            print widget.get_choices()
            return widget.get_choices()
        except Exception as ex:
            print(ex)
        finally:
            self.lock.release()
        
    def set_capture_mode(self, mode):
        self.set_config_widget_value('capturetarget', mode)

    def set_shutterspeed(self, value):
        self.set_config_widget_value('shutterspeed', value)

    def get_shutterspeed(self):
        return self.get_config_widget('shutterspeed')[1]

    def set_aperture(self, value):
        self.set_config_widget_value('aperture', value)

    def get_aperture(self):
        return self.get_config_widget('aperture')[1]
   
    def set_iso(self, value):
        self.set_config_widget_value('iso', value)

    def get_iso(self):
        return self.get_config_widget('iso')[1]
    
    def apply_preset(self, preset):
        self.set_shutterspeed(preset.shutterspeed)
        self.set_aperture(preset.aperture)
        self.set_iso(preset.iso)
 
    def is_liveview_enabled(self):
        return self.liveview_enabled

    def enable_liveview(self):
        self.liveview_enabled = True
        return

    def disable_liveview(self):
        self.liveview_enabled = False
        return

    def enable_focuspeak(self):
        self.focuspeak_enabled = True
        return

    def disable_focuspeak(self):
        self.focuspeak_enabled = False
        return

    def preview(self):
        try:
            self.lock.acquire()
            self.enable_liveview()

            logging.debug('** camera preview')
            retval = gp.gp_camera_capture_preview(self.camera,
                                                  self.preview_file,
                                                  self.context)
            if retval != GP_OK:
                # logging.error('preview capture error %s', retval)
                return None

            data = ctypes.c_void_p();
            length = ctypes.c_ulong();
            retval = gp.gp_file_get_data_and_size(self.preview_file,
                                                  ctypes.byref(data),
                                                  ctypes.byref(length))
            if retval != GP_OK or data.value is None:
                logging.error('preview fetch error %s', retval)
                return None

            logging.debug('preview: frame at addr %d, length %d',
                          data.value, length.value)

            try:
                # see effbot.org/imagingbook/introduction.html#more-on-reading-images
                res = ctypes.cast(data, POINTER(ctypes.c_ubyte * length.value)).contents
                file_jpgdata = None
                
                if self.focuspeak_enabled is False:
                    file_jpgdata = StringIO(res)
                else:
                    img_buffer=np.asarray(bytearray(res), dtype=np.uint8)
                    im = cv2.imdecode(img_buffer, cv2.CV_LOAD_IMAGE_COLOR)
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    canny = cv2.Canny(blur, 0, 150)

                    colorIm = np.zeros(im.shape, im.dtype)
                    colorIm[:,:] = (255,0,255)

                    colorMask = cv2.bitwise_and(colorIm, colorIm, mask=canny)
                    cv2.addWeighted(colorMask, 1, im, 1, 0, im)
                    retval, im2 = cv2.imencode('.jpg', im)
                    file_jpgdata = StringIO(im2.tostring())
                    
                #im = Image.open(file_jpgdata)
                #im.show()
                
                data = file_jpgdata
            except Exception as ex:
                print(ex)
                logging.error('failed')

            #lock.release()
            return data, length.value
        finally:
            self.lock.release()        

    def capture(self):
        try:
            self.lock.acquire()
            cam_path = CameraFilePath()
            retval = gp.gp_camera_capture(self.camera,
                                          GP_CAPTURE_IMAGE,
                                          ctypes.byref(cam_path),
                                          self.context)

            if retval != GP_OK:
                logging.error('Unable to capture %s', retval)
                return
            else:
                logging.debug("Capture OK")

            logging.info('name = "%s"', cam_path.name)
            logging.info('folder = "%s"', cam_path.folder)

            print cam_path.name
            print cam_path.folder
            

            filename = cam_path.name
            full_filename = os.path.join(os.getcwd(), 'incoming', filename)

            logging.debug('Download to %s', full_filename)
            cam_file = ctypes.c_void_p()
            fd = os.open(full_filename, os.O_CREAT | os.O_WRONLY)
            gp.gp_file_new_from_fd(ctypes.byref(cam_file), fd)
            retval = gp.gp_camera_file_get(self.camera,
                                           cam_path.folder,
                                           cam_path.name,
                                           GP_FILE_TYPE_NORMAL,
                                           cam_file,
                                           self.context)

            if retval != GP_OK:
                gp.gp_file_unref(cam_file)
                logging.error('Unable to download %s', retval)
                return
            else:
                logging.debug("Download complete")        

            # Delete if configured
            if False:
                logging.debug('Delete file on camera')
                retval = gp.gp_camera_file_delete(self.camera, 
                                cam_path.folder, cam_path.name, self.context)
                if retval != GP_OK:
                    logging.error('Error while deleting from camera %s', retval)
                else:
                    logging.debug("Deletion from camera completed")
                gp.gp_file_unref(cam_file)
        finally:
            self.lock.release()
