from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import time
import json

#from camera import Camera
from camera_mock import CameraMock
import camera_preset
from camera_preset import CameraPreset

cam = None


class CameraHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_body)

        if self.path.endswith('shutterspeed'):
            cam.set_shutter(data['value'])
        elif self.path.endswith('aperture'):
            cam.set_aperture(data['value'])
        elif self.path.endswith('iso'):
            cam.set_iso(data['value'])
        elif self.path.endswith('preset'):
            camera_preset = CameraPreset(data['presetname'])
            cam.apply_preset(camera_preset)
    
    def do_GET(self):
        if self.path.endswith('disconnect'):
            cam.disconnect()
            self.wfile.write('disconnect')
        elif self.path.endswith('connect'):
            cam.connect()
            self.wfile.write('connect')
        elif self.path.endswith('capture'):
            cam.capture()
            self.wfile.write('capture')
        elif self.path.endswith('enableliveview'):
            cam.enable_liveview()
            self.wfile.write('enableliveview')
        elif self.path.endswith('disableliveview'):
            cam.disable_liveview()
            self.wfile.write('disableliveview')
        elif self.path.endswith('preview'):
            self.preview()
        elif self.path.endswith('shutterspeed'):
            self.write_json(cam.get_shutterspeed().json())
        elif self.path.endswith('aperture'):
            self.write_json(cam.get_aperture().json())
        elif self.path.endswith('iso'):
            self.write_json(cam.get_iso().json())
        elif self.path.endswith('exposure'):
            self.write_json({'shutterspeed': cam.get_shutterspeed().json(), 'aperture': cam.get_aperture().json(), 'iso': cam.get_iso().json()})
        elif self.path.endswith('liveview'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head></body>')
            self.wfile.write('<img src="http://localhost:8000/preview" />')
            self.wfile.write('</body></html>')
        elif self.path.endswith('presets'):
            self.write_json({'presets': camera_preset.find_all()})            
        elif self.path.endswith('preset'):
            self.write_json(CameraPreset().json())
        else:
            self.wfile.write("unknown cmd")

    def write_json(self, json_data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        res = json.dumps(json_data)
        self.wfile.write(res)

    def preview(self):
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
        self.end_headers()
        while cam.is_liveview_enabled():
            res = cam.preview()
            if res is None:
                continue
            (frame, length) = res
            header = "\r\n--jpgboundary\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(length) + "\r\n\r\n"
            self.wfile.write(header)
            self.wfile.write(frame.read())
            time.sleep(0.05)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Server startup"""


def main():
    global cam
    #cam = Camera()
    cam = CameraMock()
    cam.connect()
    server = ThreadedHTTPServer(('localhost', 8000), CameraHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
