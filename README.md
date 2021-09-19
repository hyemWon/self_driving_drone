# Safe Return Home Service With Self-Driving Drone

---

Safe return home service using self-driving drone (2021. 07. 26 ~ 2021. 09. 03)

Hustar AI/SW 3rd Team Project 

Last updated at 2021.9.19

## Implements In Project

---

- **Computer Vision Develeopments**
    - **Person detection & tracking** using SSD Mobile-Net v3
    - **Violence detection & User authentication** using ResNet152
    - **Obstacle avoidance** using Mask R-CNN
    - **Thermal camera pre-processing** using Opencv

- **System and Web Developments**
    - **Drone communication system** using mav-sdk and mavlink
    - **Base station and Drone Firmware Setting** using QGroundControl
    - **Server(Base Station), Socket Client(Drone) System** using TCP socket
    - **API Server** based Flask framework, WSGI, Nginx, and Firebase
    - **Mobile Application** using Flutter

### Prerequisites

---

- server
    - Python 3.6+
    - tensorflow 2.2+
    - pytorch 1.5+
    - torchvision 0.3.0+
    - opencv 4.2+
    - flask
    - firebase-admin
    - CUDA 10.2, cudnn 7.6.5
- client
    - Python 3.6+
    - opencv 4.2+
    - mavsdk
    - pyrealsense2
    - usblib
- flutter
    - flutter
    - java-sdk

## Directory Structures

---

- examples : tests and examples
- flutter : flutter
- scripts : running code using bash script
- src : server and client code

```
self-drving-drone
├─examples
│   ├─ActionAI
│   ├─alphapose
│   ├─distance
│   ├─drone
│   ├─person_tracking
│   ├─realsense
│   ├─seekthermal
│   ├─socket
│   └─update_ActionAI
├─flutter
│   ├─android
│   │   ├─app
│   │   │   └─src
│   │   │       ├─debug
│   │   │       ├─main
│   │   │       │   ├─kotlin
│   │   │       │   │   └─com
│   │   │       │   │       └─example
│   │   │       │   │           └─flutter_auth
│   │   │       │   └─res
│   │   │       └─profile
│   │  └─gradle
│   │      └─wrapper
│   ├─assets
│   │  ├─icons
│   │  └─images
│   ├─ios
│   │  ├─build
│   │  ├─Flutter
│   │  ├─Runner
│   │  ├─Runner.xcodeproj
│   │  └─Runner.xcworkspace
│   ├─lib
│   │  ├─components
│   │  └─Screens
│   │      ├─Googlemap
│   │      ├─Login
│   │      ├─Signup
│   │      └─Welcome
│   └─test
├─scripts
└─src
    ├─client
    │   ├─ manage.py
    │   ├─ drone.py
    │   ├─ realsense.py
    │   ├─ seek_thermal.py
    │   └─ util
    └─server
        ├─ controller
        ├─ db
        ├─ util
        │   ├─ actionai
        │   └─ mobilenet
        ├─ view
        ├─ manage.py
        ├─ drone.py
        ├─ processor.py
        ├─ realsense.py
        └─ seek_theraml.py
```

## Drone Hardware Specification

---

- Drone Frame : [GSN 750](https://smartstore.naver.com/itssg/products/5164489850)
- Flight Controller - Pixhawk 4
- Motor - TAROT 4006 Motor
- Propeller - MAD FLUXER 16 x 5.4 Propeller
- ESC -  Xrotor 40A ESC
- GPS - Pixhawk 4 GPS Module
- Imbedded Board - NVIDIA Jetson Nano Development Kit 2GB
- Telemetry - 3DR Radio Telemetry Module
- Battery : PolyTronics PT-B10000-NSR35 Li-Po Battery
- LTE Modem - HUAWEI E8372h-320
- Radio Receiver : CoolTech RSF08SB 8ch Futaba S-FHSS Compatible Receiver(2.4GHz/S.BUS/HV)
- Depth Camera : Inter Realsense

## **Team members**

---

- Deep Learning
    - [Hyewon, Jeong](https://github.com/hyemWon) : Team leader, Violence detection and User Authentication
    - [Suyeong, Jeon](https://github.com/devsuyoung) : Violence detection and User Authentication
- Image Pre-processing and Detection
    - Saemi, Yoon : Person Detection and Tracking, Obstacle Avoidance
    - [Nuri, Kim](https://github.com/dev-wendy) : Person Detection and Tracking, Obstacle Avoidance
- System & Application Development
    - [Hoyeon, Kim](https://github.com/mozzihozzi) : Back-end developments, Drone control system, TCP Socket server-client system, API server, Image data collection
    - [Jeongeun, Jin](https://github.com/dev-merry) : Front-end developments, Flutter-based Mobile Application

## References

---

- You Only Look Once: Unified, Real-Time Object Detection (Propose by Joseph Redmon , Santosh Divvala, Ross Girshick, Ali Farhadi at CVPR 2016)
- SSD: Single Shot MultiBox Detector (Propose by Wei Liu, Dragomir Anguelov, Dumitru Erhan, Christian Szegedy, Scott Reed, Cheng-Yang Fu, Alexander C. Berg at CVPR 2016)
- Focal Loss for Dense Object Detection (Propose by Tsung-Yi Lin Priya Goyal Ross Girshick Kaiming He Piotr Dollar at CVPR 2016)
- Real-Time 3D-Sensing Technologies and Applications in Interactive and Immersive Device (Propose by Achintya K. Howmik, 2016)
- Eye in the Sky: Real time Drone Surveillance System ( for ViolentIndividuals Identification using ScatterNet Hybrid Deep Learning Network(proposed by Amarjot, Devendra Patil, SN Omkar at CVPR, 2018)
- Deep Learning based violent protest detection syste m(proposed by Yeonsu Lee, Hyunchul Kim in Journal of the Korea Society of Computer and Information, 2019)
- Violence Detection in Surveillance Videos with Deep Network using Transfer Learning(proposed by Aqib Mumtaz, Allah Bux Sargano, Zulfiqar Habib at EE CS, 2018)
- [Cloud Robotics](https://en.wikipedia.org/wiki/Cloud_robotics)
- [PX4 Autopilot Documentation](https://docs.px4.io/master/en/)
- [MAVSDK Python Documentation](http://mavsdk-python-docs.s3-website.eu-central-1.amazonaws.com/)
- [QGroundControl Documentation](https://docs.qgroundcontrol.com/master/en/index.html)
- [MAVLink Documentation](https://mavlink.io/en/)
- [human action classification, dronefreak github](https://github.com/dronefreak/human-action-classification)
- [ActionAI, smellslikeml github](https://github.com/smellslikeml/ActionAI)
- [fight_detection, imsoo github](https://github.com/imsoo/fight_detection)
