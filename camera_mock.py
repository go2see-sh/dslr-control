import Image
import logging

from camera_preset import CameraPreset

class CameraMock:

    def __init__(self):
        self.camera = None
        self.liveview_enabled = False

    def connect(self):
        if self.camera is not None:
            return

        print 'Camera connected'

    def disconnect(self):
        print 'Disconnected'

    def set_shutterspeed(self, value):
        pass

    def get_shutterspeed(self):
        return Widget('shutterspeed', '1/30', ['1/2', '1/3', '1/10', '1/30', '1/40'])

    def set_aperture(self, value):
        pass

    def get_aperture(self):
        return Widget('aperture', '4', ['4', '4.5', '5', '5.5'])
   
    def set_iso(self, value):
        pass

    def get_iso(self):
        return Widget('iso', '800', ['100', '200', '400', '800', '1600'])

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

    def preview(self):
        self.enable_liveview()
        return None

    def capture(self):
        filename = 'test.jpg';
        return filename


class Widget:

    def __init__(self, name, value, choices):
        self.name = name
        self.value = value
        self.choices = choices

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_choices(self):
        return self.choices

    def json(self):
        return {'type': self.get_name(), 'options': self.get_choices(), 'value': self.get_value()}
