import time
import random
import board
import busio
import digitalio
import adafruit_ssd1306
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import socketio
import requests
import json
import adafruit_apds9960.apds9960
import threading 

led_target = 1200
PowerSaving = False
current_lux = 0
last_lux = 0
current_duty_cycle = 50

def main():
    global led_target, PowerSaving, current_lux, last_lux, current_duty_cycle, Announcement_Type, Announcement_Text, Announcement_Bool     
    # Initialize GPIO, PWM, and ADC
    GPIO.setup("P8_17", GPIO.IN)
    PWM.start("P8_13", 50)
    PWM.start("P9_14", 0)
    ADC.setup()

    sio = socketio.Client()
    
    @sio.event
    def connect():
        print('Connection established.')
    
    @sio.event
    def disconnect():
        print('Disconnected from server.')
        
    @sio.event
    def BBBW4_LUX(RxData):
        global current_lux
        current_lux = RxData
        print("Current LUX: " + str(current_lux)) #Receives Lux value from BBBW3
        
    @sio.event
    def BBBW4_Announcement_Event(RxData):
        global Announcement_Type, Announcement_Text, Announcement_Bool
        Announcement_Type = RxData["Type"]
        Announcement_Text = RxData["Text"]
        print(Announcement_Type +"\n"+Announcement_Text)
        Announcement_Bool = True
        print(Announcement_Bool)
    
    @sio.event
    def BBBW4_led_target(RxData):
        global led_target
        led_target = RxData
        print(led_target)
        
    @sio.event
    def BBBW4_PowerSaving(RxData):
        global PowerSaving
        PowerSaving = bool(RxData)
        print(PowerSaving)
    
    # Connect to the server
    while True:
        try:
            sio.connect('http://192.168.0.188:5000')
            break
        except:
            print("Try to connect to the server.")
            pass
    

    def light_control():
        global current_duty_cycle, current_lux, led_target, last_lux
        step = 0.1  # Adjust this step value based on your needs
        
        while True:
            if not PowerSaving:
                lux_diff = int(led_target) - int(current_lux)
                # print(lux_diff)
                
                if (current_lux - last_lux) > 1000:
                    current_duty_cycle += 0
                    
                else:
                    if lux_diff > 0:
                        current_duty_cycle += step
                    elif lux_diff < 0:
                        current_duty_cycle -= step
            
                current_duty_cycle = max(0, min(100, current_duty_cycle))
                PWM.set_duty_cycle("P9_14", current_duty_cycle)
                # print(f"Current Lux: {current_lux}, Duty Cycle: {current_duty_cycle}")
                last_lux = current_lux
                sio.emit("BBBW4_LED_DutyCycle", round(current_duty_cycle, 0))
                time.sleep(0.03)
            else:
                current_duty_cycle = 20
                current_duty_cycle = max(0, min(100, current_duty_cycle))
                PWM.set_duty_cycle("P9_14", current_duty_cycle)
                # print(f"Current Lux: {current_lux}, Duty Cycle: {current_duty_cycle}")
                sio.emit("BBBW4_LED_DutyCycle", round(current_duty_cycle, 0))
                time.sleep(0.03)
            
    # Start light control in a separate thread
    light_thread = threading.Thread(target=light_control)
    light_thread.start()
    
    
    # # Function to initialize OLED display
    def OLEDClickInit():
        Pin_DC = digitalio.DigitalInOut(board.P9_16)
        Pin_DC.direction = digitalio.Direction.OUTPUT
        Pin_DC.value = False
        Pin_RESET = digitalio.DigitalInOut(board.P9_23)
        Pin_RESET.direction = digitalio.Direction.OUTPUT
        Pin_RESET.value = True
        L_I2c = busio.I2C(SCL, SDA)
        return L_I2c
    
    def Announcement_Present():
        Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
        Draw.text((46, 10), Announcement_Type, font=Font, fill=1)
        Draw.text((46, 20), Announcement_Text, font=Font, fill=1)
        Display.image(ImageObj)
        Display.show()
        time.sleep(5)
    
    
    # OLED display initialization
    G_I2c = OLEDClickInit()
    Display = adafruit_ssd1306.SSD1306_I2C(128, 32, G_I2c, addr=0x3C)
    ImageObj = Image.new("1", (Display.width, Display.height))
    Draw = ImageDraw.Draw(ImageObj)
    Draw.rectangle((0, 10, Display.width - 21, Display.height - 20), outline=0, fill=0)
    Font = ImageFont.load_default()
    
    
    options = {
        1: "Police",
        2: "Ambulance",
        3: "Fire",
        4: "Maintenance", 
        5: "Submit"
    }
    
    
    Options = ""
    Draw.text((45, 10), Options, font=Font, fill=1)
    Display.image(ImageObj)
    Display.show()
    Choice = 1
    Mode = True
    Submit = False
    
    
    Announcement_Bool = False
    
    
        
    # Main control loop
    try:
        while True:
            sio.emit("BBBW4_LED_DutyCycle", round(current_duty_cycle, 0))

            
            if Announcement_Bool:
                Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
                Display.image(ImageObj)
                Display.show()
                Announcement_Present()
                Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
                Display.image(ImageObj)
                Display.show()
                Announcement_Bool = False
            else:
                
                
                # Lux 500
                # PWM.set_duty_cycle("P8_13", 100)
                
                # ADC input
                DigitalValue = ADC.read("P9_40")
                if 0.00 <= DigitalValue < 0.10:
                    pass
                    # Ratings = "No Key"
                elif 0.16 < DigitalValue < 0.18:
                    print("T6 Key is Pressed")
                    Mode = not Mode
                    time.sleep(1)
                elif 0.33 < DigitalValue < 0.35:
                    print("T5 Key is Pressed")
                    Submit = True
                elif 0.50 < DigitalValue < 0.52:
                    print("T4 Key is Pressed")
                    Choice = 4
                elif 0.67 < DigitalValue < 0.69:
                    print("T3 Key is Pressed")
                    Choice = 3
                elif 0.84 < DigitalValue < 0.87:
                    print("T2 Key is Pressed")
                    Choice = 2
                elif 0.90 < DigitalValue < 1.10:
                    print("T1 Key is Pressed")
                    Choice = 1
                
                # Ensure Choice is within valid range
                if Choice not in options.keys():
                    Choice = 1
        
                if Mode: # Emergency
                    Options = options[Choice]
                    Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
                    Draw.text((45, 15), Options, font=Font, fill=1)
                    Display.image(ImageObj)
                    Display.show()
                    if Submit: # Submit
                        sio.emit("BBBW4_Minor_Emergency_Event", options[Choice])
                        Submit = False
                        Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
                        Draw.text((40, 15), "Emergency Sent!", font=Font, fill=1)
                        Display.image(ImageObj)
                        Display.show()
                        time.sleep(1)
        
                elif not Mode:
                    Options = f"Rating {Choice}"
                    Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
                    Draw.text((45, 15), Options, font=Font, fill=1)
                    Display.image(ImageObj)
                    Display.show()
                    if Submit: # Submit
                        print("RATING..." + str(Choice))
                        sio.emit("BBBW4_Rating_Event", Choice)
                        Submit = False
                        Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
                        Draw.text((46, 10), f"Thank you", font=Font, fill=1)
                        Draw.text((46, 20), f"for rating! {str(Choice)}", font=Font, fill=1)
                        Display.image(ImageObj)
                        Display.show()
                        time.sleep(1)
            
        
                while True:
                    if GPIO.input("P8_17"):
                        PWM.start("P8_13", 50)
                        sio.emit('BBBW4_Emergency_Event', "Calling 999")
                        Draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)
                        Draw.text((45, 15), "Calling 999", font=Font, fill=1)
                        Display.image(ImageObj)
                        Display.show()
                    else:
                        PWM.start("P8_13", 0)
                        break
    
    except KeyboardInterrupt:
        print("Exiting...")
        PWM.cleanup()
        GPIO.cleanup()
        
    if time.time() % 2 < 1:
        raise ValueError("An error occurred!")   


while True:
    try:
        main()
        break 
    except Exception as e:
        print("\n\nSomething didn't work...")
        print(f"Error encountered: {e}. Retrying...\n\n")
