import socketio
import time
from Adafruit_BBIO.SPI import SPI
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import board
import adafruit_bme680
import math

def main():
    
    sio = socketio.Client()
    
    ADC.setup()
     
    #Create sensor object, communicating over the board's default I2C bus
    i2c = board.I2C()
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, 0x77)
    
    #Singapore mean pressure (hPa) at sea level
    bme680.sea_level_pressure = 1008.5
    
    #Calibrate the temperature sensor value
    temperature_offset = -5
    
    
    
    @sio.event
    def connect():
        print('Connection established.')
    
    @sio.event
    def disconnect():
        print('Disconnected from server.')
        
    # @sio.event
    # def BBW_ChangedThreshold(RxData):
    #     global Threshold
    #     Threshold = int(RxData['value'])
    #     print(Threshold)
    
    
    def BarGraph2Init():
        GPIO.setup("P9_14", GPIO.OUT)
        GPIO.setup("P9_12", GPIO.OUT)
        GPIO.output("P9_14", GPIO.HIGH)
        GPIO.output("P9_12", GPIO.HIGH)
        L_Spi1 = SPI(1,0)
        L_Spi1.mode = 0
        return L_Spi1
        
    def SevenSegInit():
        GPIO.setup("P8_19", GPIO.OUT)
        GPIO.setup("P8_14", GPIO.OUT)
        GPIO.output("P8_19", GPIO.HIGH)
        GPIO.output("P8_14", GPIO.HIGH)
        L_Spi0 = SPI(0,0)
        L_Spi0.mode = 0
        return L_Spi0
    
    def SevenSegDisplay(L_Spi0, L_Number):
        DigitList = [0x7E, 0x0A, 0xB6, 0x9E, 0xCA, 0xDC, 0xFC, 0x0E, 0xFE, 0xDE]
        OnesDigit = L_Number % 10
        TensDigit = L_Number / 10
        L_Spi0.writebytes([DigitList[int(OnesDigit)], DigitList[int(TensDigit)]])
    
    def BarGraph2Display(L_Spi1, L_NumberOfBar):
        if L_NumberOfBar == 0:
            # L_Spi1.writebytes([0x00, 0x00, 0x00])
            L_Spi1.writebytes([0x0F, 0xC0, 0xFF])
    
        elif L_NumberOfBar == 1:
            L_Spi1.writebytes([0x00, 0x00, 0x01])
        elif L_NumberOfBar == 2:
            L_Spi1.writebytes([0x00, 0x00, 0x03])
        elif L_NumberOfBar == 3:
            L_Spi1.writebytes([0x00, 0x00, 0x07])
        elif L_NumberOfBar == 4:
            L_Spi1.writebytes([0x00, 0x00, 0x0F])
        elif L_NumberOfBar == 5:
            L_Spi1.writebytes([0x00, 0x40, 0x1F])
        elif L_NumberOfBar == 6:
            L_Spi1.writebytes([0x00, 0xC0, 0x3F])
        elif L_NumberOfBar == 7:
            L_Spi1.writebytes([0x01, 0xC0, 0x7F])
        elif L_NumberOfBar == 8:
            L_Spi1.writebytes([0x03, 0xC0, 0xFF])
        elif L_NumberOfBar == 9:
            L_Spi1.writebytes([0x07, 0xC0, 0xFF])
        elif L_NumberOfBar == 10:
            L_Spi1.writebytes([0x0F, 0xC0, 0xFF])
            
    # def Threshold_values(value):
    #     if value > Mic_threshold:
    #         output = 10
    #     elif value > Mic_threshold - 0.0042:
    #         output = 9
    #     elif value > Mic_threshold - 0.0042*2:
    #         output = 8
    #     elif value > Mic_threshold - 0.0042*3:
    #         output = 7
    #     elif value > Mic_threshold - 0.0042*4:
    #         output = 6
    #     elif value > Mic_threshold - 0.0042*5:
    #         output = 5
    #     elif value > Mic_threshold - 0.0042*6:
    #         output = 4
    #     elif value > Mic_threshold - 0.0042*7:
    #         output = 3
    #     elif value >  Mic_threshold - 0.0042*8:
    #         output = 2
    #     elif value >  Mic_threshold - 0.0042*9:
    #         output = 1
    #     else:
    #         output = 0
    #     return output
    
    def Threshold_values(value):
        output = 0  # Initialize output to ensure it's always assigned
    
        if value > (0.0253 * 2.718**(0.1018 * 10)):
            output = 10
        elif value > (0.0253 * 2.718**(0.1018 * 9)):
            output = 9
        elif value > (0.0253 * 2.718**(0.1018 * 8)):
            output = 8
        elif value > (0.0253 * 2.718**(0.1018 * 7)):
            output = 7
        elif value > (0.0253 * 2.718**(0.1018 * 6)):
            output = 6
        elif value > (0.0253 * 2.718**(0.1018 * 5)):
            output = 5
        elif value > (0.0253 * 2.718**(0.1018 * 4)):
            output = 4
        elif value > (0.0253 * 2.718**(0.1018 * 3)):
            output = 3
        elif value > (0.0253 * 2.718**(0.1018 * 2)):
            output = 2
        elif value > (0.0253 * 2.718**(0.1018 * 1)):
            output = 1
        elif value == 0:
            output = 10
    
        return output
    
    
    G_Number = 0
    G_Spi0 = SevenSegInit()
        
    G_NumberOfBar = 0
    G_Spi1 = BarGraph2Init()
    Mic_threshold = 0.07
    Lower_threshold = 0.028
    Threshold = 9
    
    while True:
        try:
            sio.connect('http://192.168.0.188:5000')
            break
        except:
            print("Try to connect to the server.")
            pass
        
    
    G_NumberOfBar = Threshold_values(0)
    temp_bar = 0
    PastAnalogVoltage = 0
    while True:
        try:
            while True:
                DigitalValue = ADC.read("P9_37") # Mic
                AnalogVoltage = (DigitalValue * 1.8) * (2200 / 1200)
                # print(AnalogVoltage)
                temp_temperature = bme680.temperature
                if temp_temperature < 0 or temp_temperature > 100:
                    continue
                else:
                    sio.emit('BBBW1_Temperature', round(temp_temperature + temperature_offset, 1))
                    
                    G_Number = round((temp_temperature + temperature_offset), 0)
                    SevenSegDisplay(G_Spi0, G_Number)
    
                # if G_NumberOfBar >= Threshold:
                #     BarGraph2Display(G_Spi1, G_NumberOfBar)
                
                
    
                if AnalogVoltage == 0:
                    AnalogVoltage = PastAnalogVoltage
                G_NumberOfBar = Threshold_values(AnalogVoltage)
                BarGraph2Display(G_Spi1, G_NumberOfBar) # Bar Graph
    
                sio.emit('BBBW1_Noise', round(G_NumberOfBar, 1))
                sio.emit('BBBW1_Humidity', round(bme680.relative_humidity, 1))
                sio.emit('BBBW1_Pressure', round(bme680.pressure/1000, 1))
                sio.emit('BBBW1_VOC', round(bme680.gas, 1))
                
                #temp light emit
                # sio.emit('BBBW3_Light', 78)
                print(f"Temperature: {temp_temperature  + temperature_offset }, Noise: {G_NumberOfBar}, Humidity: {bme680.relative_humidity}, Pressure: {bme680.pressure}, VOC: {bme680.gas}")
                PastAnalogVoltage = AnalogVoltage
                time.sleep(0.01)
    
    
        except Exception as error:
            print('Unable to transmit data. ', error)
            pass
        time.sleep(0.1)
        
    if time.time() % 2 < 1:
        raise ValueError("An error occurred!")   


while True:
    try:
        main()
        break 
    except Exception as e:
        print("\n\nSomething didn't work...")
        print(f"Error encountered: {e}. Retrying...\n\n")