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
GP_FILE_TYPE_NORMAL = 1
GP_FILE_TYPE_PREVIEW = 2
GP_FILE_TYPE_NORMAL = 3
GP_FILE_TYPE_RAW = 4
GP_FILE_TYPE_AUDIO = 5
GP_FILE_TYPE_EXIF = 6
GP_FILE_TYPE_METADATA = 7


class CameraFilePath(ctypes.Structure):
    _fields_ = [('name', (ctypes.c_char * 128)),
                ('folder', (ctypes.c_char * 1024))]

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
            self.enable_canon_capture(1)

    def disconnect(self):
        if self.camera != None
            gp.gp_camera_exit(self.camera, self.context)
            gp.gp_camera_unref(self.camera)
            self.camera = None

        print "Disconnected"

    def enable_canon_capture(self, enabled):
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

        self.connect()
        self.enable_liveview()

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
            #print(data.value)
            #im = Image.frombuffer('L', (1056, 704), res, 'raw', 'L', 0, 1)
            #im.show() # segmentation violation??
            logging.info('skip')
        except Exception as ex:
            print(ex)
            logging.error('failed')

        return data, length.value

    def capture(self):
        self.connect()

        cam_path = CameraFilePath()
        retval = gp.gp_camera_capture(self.camera,
                                      GP_CAPTURE_IMAGE,
                                      ctypes.byref(cam_path),
                                      context)

        if retval != GP_OK:
            logging.error('Unable to capture')
            return
        else:
            logging.debug("Capture OK")

        logging.debug('name = "%s"', cam_path.name)
        logging.debug('folder = "%s"', cam_path.folder)

        filename = cam_path.name
        full_filename = '/' + filename

        logging.debug('Download to %s', full_filename)
        cam_file = ctypes.c_void_p()
        fd = os.open(full_filename, os.O_CREAT | os.O_WRONLY)
        gp.gp_file_new_from_fd(ctypes.byref(cam_file), fd)
        retval = gp.gp_camera_file_get(self.camera,
                                       cam_path.folder,
                                       cam_path.name,
                                       GP_FILE_TYPE_NORMAL,
                                       cam_file,
                                       context)

        if retval != GP_OK:
            gp.gp_file_unref(cam_file)
            logging.error('Unable to download')
            return
        else:
            logging.debug("Download complete")        

        # Delete if configured
        if True:
            logging.debug('Delete file on camera')
            retval = gp.gp_camera_file_delete(self.camera, 
                            cam_path.folder, cam_path.name, context)
            if retval != GP_OK:
                logging.error('Error while deleting from camera')
            else:
                logging.debug("Deletion from camera completed")
            gp.gp_file_unref(cam_file)
