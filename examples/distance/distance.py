import dronekit
import socket
import exceptions
import Jetson.GPIO as GPIO
import time

#PIN_NUM 6(GND-ground),8(UART_2_TX - transmit data -> cable RXD),10(UART_2_RX-receive data -> cable TXD)

GPIO.setmode(GPIO.BCM)
TRIG = 8 #Trigger pin of the Ultrasonic Sensor
ECHO = 10 #Echo pin of the Ultrasonic Sensor

# set pin mode
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

#Connects to the vehicle using serial port.
vehicle = dronekit.connect('/dev/ttyS0', wait_ready=True, baud=57600)

#Function to convert distance and orientation into a mavlink message
def sensor_data(d,o):
    msg=vehicle.message_factory.distance_sensor_encode(
        0, #time since boot , this is not used
        5, #min distance in centimeters
        250, #max distance of the sensor in cm
        d, #distance of object detection.
        0, #type
        1, #onboard id, not used
        o, # sector
        0, # covariance, not used.
        )
    vehicle.send_mavlink(msg)

#Simple function to measure the distance using ultrasonic sensor
def measure():
    dist1=250
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    echo_state=0
    while echo_state == 0:
        echo_state = GPIO.input(ECHO)
        pulse_start = time.time()
    while GPIO.input(ECHO)==1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    if(distance<250 and distance>5): #To filter out junk values
        dist1=distance
    sensor_data(dist1,0) #Sends measured distance(dist1) and orientation(0) as a mavlink message.
    return dist1

# Main code
while True:
    d=measure()
    time.sleep(0.1)
    print(d)