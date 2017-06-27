from camera import Camera


def main():
    camera = Camera()
    camera.connect()
    camera.preview()
    camera.disconnect()

if __name__ == "__main__": main()