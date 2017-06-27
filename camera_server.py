from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import time

from camera import Camera

cam = None


class CameraResource(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('disconnect'):
            cam.disconnect()
            self.wfile.write('disconnect')
        elif self.path.endswith('connect'):
            cam.connect()
            self.wfile.write('connect')
        elif self.path.endswith('capture'):
            self.capture()
            self.wfile.write('capture')
        elif self.path.endswith('enableliveview'):
            cam.enable_liveview()
            self.wfile.write('enableliveview')
        elif self.path.endswith('disableliveview'):
            cam.disable_liveview()
            self.wfile.write('disableliveview')
        elif self.path.endswith('preview'):
            self.preview()
        elif self.path.endswith('test'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head></body>')
            self.wfile.write('<img src="http://localhost:8000/preview" />')
            self.wfile.write('</body></html>')
        else:
            self.wfile.write("Test")

    def capture(self):
        cam.capture()

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
    """Test"""


def main():
    global cam
    cam = Camera()
    server = ThreadedHTTPServer(('localhost', 8000), CameraResource)
    server.serve_forever()

if __name__ == "__main__":
    main()