import time
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.PWM as PWM
import board
import adafruit_vcnl4010
import socketio

def main():
    global Bus_Presence, edge_ir_dist_threshold, edge_prox_threshold, edge_force_threshold 
    
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print('Connection established.')
    
    @sio.event
    def disconnect():
        print('Disconnected from server.')
    
    while True:
        try:
            sio.connect('http://192.168.0.188:5000')
            break
        except:
            print("Try to connect to the server.")
            pass
    
    @sio.event
    def BBBW2_Bus_Presence(RxData):
        global Bus_Presence
        Bus_Presence = RxData
        print(Bus_Presence)
        
    @sio.event
    def BBBW2_edge_force_threshold(RxData):
        global edge_force_threshold
        edge_force_threshold = RxData
        print(edge_force_threshold)
    
    @sio.event
    def BBBW2_edge_ir_dist_threshold(RxData):
        global edge_ir_dist_threshold
        edge_ir_dist_threshold = RxData
        print(edge_ir_dist_threshold)
    
    @sio.event
    def BBBW2_edge_prox_threshold(RxData):
        global edge_prox_threshold
        edge_prox_threshold = RxData
        print(edge_prox_threshold)
    
    
    i2c = board.I2C()
    sensor = adafruit_vcnl4010.VCNL4010(i2c)
    ADC.setup()
    Bus_Presence = False
    
    edge_ir_dist_threshold = 33
    edge_prox_threshold = 2400
    edge_force_threshold = 0.01
    
    while True:
        try:
            print(edge_force_threshold)
            print(edge_prox_threshold)
            print(edge_ir_dist_threshold)
            while not Bus_Presence:
                DigitalValue_Dist = ADC.read("P9_38")
                if DigitalValue_Dist != 0:
                    AnalogVoltage_Dist = (DigitalValue_Dist * 1.8) * (2200 / 1200)
                    DistanceCM = 29.988 * pow(AnalogVoltage_Dist , -1.173)
                print("Distance(cm): %f" % DistanceCM)
                time.sleep(0.3)
                
                proximity = sensor.proximity
                print("Proximity: {0}".format(proximity))
                time.sleep(0.3)
                
                DigitalValue_Force = ADC.read("P9_39")
                AnalogVoltage_Force = (DigitalValue_Force * 1.8) * (2200 / 1200)
                print("Digital Value: %f, Analog Voltage: %f" % (DigitalValue_Force, AnalogVoltage_Force))
                time.sleep(0.3)
                
                print(Bus_Presence)
    
                if (DistanceCM < edge_ir_dist_threshold or proximity > edge_prox_threshold) and  AnalogVoltage_Force > edge_force_threshold:
                    sio.emit('BBBW2_Edge_Detect', True )
                    print("go away")
                    PWM.start("P8_19", 90)
                    PWM.set_frequency("P8_19", 523)
                    time.sleep(1)
                else:
                    PWM.start("P8_19", 0)
                    sio.emit('BBBW2_Edge_Detect', False)
                    break
            sio.emit('BBBW2_Edge_Detect', False)
            time.sleep(0.3)
        except:
            pass 
    if time.time() % 2 < 1:
        raise ValueError("An error occurred!")   
        
while True:
    try:
        main()
        break 
    except Exception as e:
        print("\n\nSomething didn't work...")
        print(f"Error encountered: {e}. Retrying...\n\n")