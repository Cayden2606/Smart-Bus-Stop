import time
import board
import busio
import socketio
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import adafruit_vcnl4010


lighting_prox_threshold = 500
bus_force_threshold = 0.8

def main():
    global lighting_prox_threshold, bus_force_threshold
    # Initialize I2C and proximity sensor
    i2c = busio.I2C(board.SCL, board.SDA)
    proximity_sensor = adafruit_vcnl4010.VCNL4010(i2c)
    
    # Setup ADC and GPIO
    ADC.setup()
    GPIO.setup("P8_18", GPIO.IN)  # Motion sensor 1
    GPIO.setup("P9_15", GPIO.IN)  # Motion sensor 2
    
    # Initialize SocketIO
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print('Connection established.')
    
    @sio.event
    def disconnect():
        print('Disconnected from server.')
    
    # Attempt to connect to the server
    while True:
        try:
            sio.connect('http://192.168.0.188:5000')
            break
        except:
            print("Trying to connect to the server...")
            pass
    
    
    @sio.event
    def BBBW3_bus_force_threshold(RxData):
        global bus_force_threshold
        bus_force_threshold = float(RxData)
        print("\n\n\n" + str(bus_force_threshold))
    
    @sio.event
    def BBBW3_lighting_prox_threshold(RxData):
        global lighting_prox_threshold
        lighting_prox_threshold = float(RxData)
        print("\n\n\n" + str(lighting_prox_threshold))
    
    
    def read_adc(pin):
        digital_value = ADC.read(pin)
        analog_voltage = (digital_value * 1.8) * (2200 / 1200)
        if analog_voltage > 0:
            distance_cm = 29.988 * pow(analog_voltage, -1.173)
        else:
            distance_cm = float('inf')
        return digital_value, analog_voltage, distance_cm
    
    # Define threshold values

    
    while True:
        print(bus_force_threshold)
        print(lighting_prox_threshold)
        # Read sensors
        _, force_analog_voltage, _ = read_adc("P9_39")  # Force Click
        proximity = proximity_sensor.proximity  # Proximity Click
        lux = proximity_sensor.ambient_lux  # Ambient Light sensor from Proximity Click
        motion_detected_1 = GPIO.input("P8_18")  # Motion sensor 1
        motion_detected_2 = GPIO.input("P9_15")  # Motion sensor 2
    
        # Triple check for presence detection
        print(f"Prox: {proximity}, Motion1: {motion_detected_1}, Motion2: {motion_detected_2}")
        presence_detected = bool(proximity > lighting_prox_threshold and (motion_detected_1 or motion_detected_2))
    
        # Check for heavy bus detection
        print("Current Force: "+ str(force_analog_voltage))
        heavy_bus_detected = force_analog_voltage > bus_force_threshold
    
        print("Presence detected: {}".format(presence_detected))
        print("Heavy bus detected: {}".format(heavy_bus_detected))
        print("Lux level: {}".format(lux))
    
        # Emit events only if connected
        if sio.connected:
            sio.emit('BBBW3_Light', lux)
            sio.emit('BBBW3_Motion_Event', presence_detected)
            sio.emit('BBBW3_Bus_Force_Event', heavy_bus_detected)
        else:
            print("Not connected to the server, cannot emit events.")
    
        time.sleep(0.3)


    if time.time() % 2 < 1:
        raise ValueError("An error occurred!")
        
        
while True:
    try:
        main()
        break 
    except Exception as e:
        print(f"Error encountered: {e}. Retrying...")
        time.sleep(1) 