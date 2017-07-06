import logging
import json
import os

def find_all():
    config_files = [os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.getcwd(), 'presets')) if f.endswith('.json')]
    return config_files


class CameraPreset:

    def __init__(self, presetname):
        self.load(presetname)

    def load(self, filename):
        with open(os.path.join(os.getcwd(), 'presets', filename + '.json')) as config_file:    
            data = json.load(config_file)
            self.shutterspeed = data['shutterspeed']
            self.aperture = data['aperture']
            self.iso = data['iso']

    def json(self):
        return {'shutterspeed': self.shutterspeed, 'aperture': self.aperture, 'iso': self.iso}
