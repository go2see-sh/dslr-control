import Image
import logging

class CameraMock:

    def __init__(self):
        self.camera = None
        self.liveview_enabled = False

    def connect(self):
        if self.camera is not None:
            return

        print "Camera connected"

    def disconnect(self):
        print "Disconnected"

    def set_canon_capture(self, enabled):
        try:
            """"""
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
        self.enable_liveview()
        return data, length.value

    def capture(self):
        self.connect()
        filename = "test.jpg";
        return filename
