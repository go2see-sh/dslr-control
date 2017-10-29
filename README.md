# dslr-control
This projects provides a DSLR camera controller that runs on an linux machine. 
It was built especially to run on a Raspberry Pi. 

## Features
* Control a Canon EOS DSLR with a Raspberry Pi
* Control Aperture, Shutter an ISO
* Provide focus peaking
* Liveview in 15 fsp
* Remote Caputre

## Setup
First run the following commands on your system to get everythign up to date:

    sudo apt-get update
    sudo apt-get upgrade

libgphoto is used to communicate with the camera. Therefore, libgphoto has to be installed on the system.
The sources can be downloaded and then installed:

    wget https://downloads.sourceforge.net/project/gphoto/libgphoto/2.5.14/libgphoto2-2.5.14.tar.bz2
    tar xjvf libgphoto2–2.5.2.tar.bz2
    cd libgphoto2–2.5.2/
    ./configure
    make
    sudo make install
    cd ..

The main application is a python 2.7 based web server. Therefore, python and several other python libraries have to be installed on the system.
    sudo apt-get install python2.7-dev
    sudo apt-get install python-pip
    sudo apt-get install python-imaging
    pip install numpy

On a Raspberry Pi, a connected Canon DSLR is automatically mounted by other system tools which causes the dsrl control to be unable to connect. If this is the case, we can disable the mounting:

    sudo rm /usr/share/dbus-1/services/org.gtk.Private.GPhoto2VolumeMonitor.service
    sudo rm /usr/share/gvfs/mounts/gphoto2.mount
    sudo rm /usr/share/gvfs/remote-volume-monitors/gphoto2.monitor
    sudo rm /usr/lib/gvfs/gvfs-gphoto2-volume-monitor

Focus peaking is based on OpenCV. Therefore, OpenCV and some other libraries have to be installed on the system:

    sudo apt-get install python-opencv
    sudo apt-get install libcv-dev
    sudo apt-get install python-opencv
    sudo apt-get install libopencv-dev
    sudo apt-get install libcv2.3
    sudo apt-get install opencv-doc

It is also worth to include the following libraries:

    sudo apt-get install libjpeg8-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libgtk2.0-dev libatlas-base-dev gfortran
