import Image
import ctypes
import logging
from _ctypes import POINTER

from cStringIO import StringIO
from config import Config

gp = ctypes.CDLL('libgphoto2.so.6')

gp.gp_context_new.restype = ctypes.c_void_p

# gphoto2-result.h
# gphoto constants
GP_OK = 0
GP_ERROR = -1 #generic error
GP_ERROR_BAD_PARAMETERS = -2 #bad parameters passed
GP_ERROR_NO_MEMORY = -3 # out of memory
GP_ERROR_LIBRARY = -4 # error in camera driver
GP_ERROR_UNKNOWN_PORT = -5 #unknown libgphoto2 port passed
GP_ERROR_NOT_SUPPORTED = -6 #whatever you tried isn't supported
GP_ERROR_IO = -7 # Generic I/O error - there's a surprise
GP_ERROR_FIXED_LIMIT_EXCEEDED = -8 # internal buffer overflow
GP_ERROR_TIMEOUT = -10 #timeout - no prizes for guessing that one
GP_ERROR_IO_SUPPORTED_SERIAL = -20 #Serial port not supported
GP_ERROR_IO_SUPPORTED_USB = -21 #USB ports not supported
GP_ERROR_IO_INIT = -31 #Unable to init I/O
GP_ERROR_IO_READ = -34 # I/O Error during read
GP_ERROR_IO_WRITE = -35 # I/O Error during write
GP_ERROR_IO_UPDATE = -37 #I/O during update of settings
GP_ERROR_IO_SERIAL_SPEED = -41 # Serial speed not possible
GP_ERROR_IO_USB_CLEAR_HALT = -51 #Error
# CameraCaptureType enum in 'gphoto2-camera.h'
GP_CAPTURE_IMAGE = 0
# CameraFileType enum in 'gphoto2-file.h'
GP_FILE_TYPE_NORMAL = 1


class Camera:

    def __init__(self):
        self.camera = None
        self.preview_file = ctypes.c_void_p()
        self.context = ctypes.c_void_p(gp.gp_context_new())
        gp.gp_file_new(ctypes.byref(self.preview_file))
        self.liveview_enabled = False

    def connect(self):
        if self.camera is not None:
            return

        self.camera = ctypes.c_void_p()
        gp.gp_camera_new(ctypes.byref(self.camera))
        retval = gp.gp_camera_init(self.camera, self.context)
        if retval != GP_OK:
            print "Unable to connect"
        else:
            print "Camera connected"
            self.set_canon_capture(1)

    def disconnect(self):

        gp.gp_camera_exit(self.camera, self.context)
        gp.gp_camera_unref(self.camera)

        print "Disconnected"

    def set_canon_capture(self, enabled):
        try:
            config = Config(self)
            widget = config.get_root_widget().get_child_by_name('capture')
            widget.set_value(enabled)
            config.set_config()
        except:
            pass

    def is_liveview_enabled(self):
        return self.liveview_enabled

    def enable_liveview(self):
        self.liveview_enabled = True
        return

    def disable_liveview(self):
        self.liveview_enabled = False
        return

    def preview(self):

        """Connect and capture a preview frame.

        Return the preview as a(data, length) tuple pointing to a memory
        area containing a jpeg-compressed image. The data poiner is only valid
        until the next call to preview().
        Preview can fail for short periods. If you get None back, try again
        later.
        """

        self.connect()

        logging.debug('** camera preview')
        retval = gp.gp_camera_capture_preview(self.camera,
                                              self.preview_file,
                                              self.context)
        if retval != GP_OK:
            logging.error('preview capture error %s', retval)
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
            #1
            # see effbot.org/imagingbook/introduction.html#more-on-reading-images
            res = ctypes.cast(data, POINTER(ctypes.c_ubyte * length.value)).contents
            file_jpgdata = StringIO(res)
            #im = Image.open(file_jpgdata)
            #im.show()
            data = file_jpgdata


            #2
            #res = ctypes.cast(data, POINTER(ctypes.c_ubyte * (1056 * 704 * 4))).contents
            #print(length.value)
            #print(res)
            #print(data.value)
            #im = Image.frombuffer('L', (1056, 704), res, 'raw', 'L', 0, 1)
            #im.show() # segmentation violation??
            logging.info('skip')
        except Exception as ex:
            print(ex)
            logging.error('failed')

        return data, length.value
