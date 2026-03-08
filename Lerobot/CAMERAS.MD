--- Detected Cameras ---
Camera #0: UGREEN 
  Name: OpenCV Camera @ 0
  Type: OpenCV
  Id: 0
  Backend api: AVFOUNDATION
  Default stream profile:
    Format: 16.0
    Width: 1920
    Height: 1080
    Fps: 5.0
--------------------
Camera #1: FaceTime Camera
  Name: OpenCV Camera @ 1
  Type: OpenCV
  Id: 1
  Backend api: AVFOUNDATION
  Default stream profile:
    Format: 16.0
    Width: 1280
    Height: 720
    Fps: 15.0
--------------------
Type: RealSense
  Id: 349422070330
  Firmware version: 5.17.0.10
  Usb type descriptor: 3.2
  Physical port: 1-2.2-5
  Product id: 0B07
  Product line: D400
  Default stream profile:
    Stream_type: Color
    Format: rgb8
    Width: 640
    Height: 480
    Fps: 30s

    -----
    #RUN ONLY IN MAC WITH AND SUDO COMMAND : 
    sudo python Teleport_Camera.py

    ---------
    #Get your token from hugging face : 
    https://huggingface.co/settings/tokens

    ------
    Username:
    <your_username>