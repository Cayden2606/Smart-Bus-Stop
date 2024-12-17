import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify
from flask import render_template

#https://flask.palletsprojects.com/en/3.0.x/deploying/eventlet/

from eventlet import wsgi

from flask_socketio import SocketIO
from flask_socketio import emit

import os
import sys
import subprocess

import sqlite3

import time
from threading import Lock, Thread

from datetime import datetime, timedelta, timezone
import re




app = Flask(__name__)
#socketio = SocketIO(app)
socketio = SocketIO(app, async_mode='eventlet')

#SQL Database add stuff
def execute_db_query(query, args=()):
    conn = sqlite3.connect('busStop.db')
    c = conn.cursor()
    c.execute(query, args)
    conn.commit()
    conn.close()

env_temp = {
    "temperature": None,
    "humidity": None,
    "noise": None,
    "voc": None,
    "light": None,
    "pressure": None
}
def Send_All_Environment(source, data):
    global env_temp
    if all(value is not None for value in env_temp.values()):
        execute_db_query("INSERT INTO environment (temperature, noise, humidity, pressure, voc, light) VALUES (?, ?, ?, ?, ?, ?)",
                         (env_temp["temperature"], env_temp["noise"], env_temp["humidity"], env_temp["pressure"], env_temp["voc"], env_temp["light"]))
        env_temp = {
            "temperature": None,
            "humidity": None,
            "noise": None,
            "voc": None,
            "light": None,
            "pressure": None
        }
        print("Added to Database liao HOR")

    env_temp[source] = data


@app.route('/WebPage.html')
def index():
    return render_template('WebPage.html')

@app.route('/Admin.html')
def other():
    return render_template('Admin.html')

@app.route('/HomePage.html')
def home():
    return render_template('HomePage.html')

@app.route('/AboutUs.html')
def aboutus():
    return render_template('ABoutUs.html')

@app.route('/index.html')
def testing():
    return render_template('index.html')

@app.route('/testinggoog.html')
def test():
    return render_template('testinggoog.html')

@app.route('/3dmodeltest.html')
def test1():
    return render_template('3dmodeltest.html')

@app.route('/cTable.html')
def test2():
    return render_template('cTable.html')

@app.route('/data/bus')
def get_bus_data():
    conn = sqlite3.connect('busStop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT bus_number, actual_arrive_time, predicted_arrive_time, difference_in_time FROM bus")
    rows = cursor.fetchall()
    conn.close()
    data = [
        {"bus_number": row[0], "actual_arrive_time": row[1], "predicted_arrive_time": row[2], "difference_in_time": row[3]}
        for row in rows
    ]
    return jsonify(data)


@app.route('/data/environment') # JSON Data for graphs using D3 
def get_environment_data():
    conn = sqlite3.connect('busStop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, noise, humidity, pressure, voc, light FROM environment")
    rows = cursor.fetchall()
    conn.close()
    data = [
        {"timestamp": row[0], "temperature": row[1], "noise": row[2], "humidity": row[3], "pressure": row[4], "voc": row[5], "light": row[6]}
        for row in rows
    ]
    return jsonify(data)

@app.route('/data/settings') # BBBW Threshold Settings
def get_settings_data():
    conn = sqlite3.connect('busStop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT edge_force_threshold, edge_ir_dist_threshold, edge_prox_threshold, bus_force_threshold, lighting_prox_threshold, led_target FROM settings")
    rows = cursor.fetchall()
    conn.close()
    data = [
        {"edge_force_threshold": row[0], "edge_ir_dist_threshold": row[1], "edge_prox_threshold": row[2], "bus_force_threshold": row[3], "lighting_prox_threshold": row[4], "led_target": row[5]}
        for row in rows
    ]
    return jsonify(data)

# sys.stdout = open(os.devnull, 'w')
# sys.stderr = open(os.devnull, 'w')

# @socketio.event
# def Motion_Event(RxData):
#     socketio.emit('Web_Motion_Event', RxData)
#     print('Receive Data from Motion')

# @socketio.event
# def Mic_Event(RxData):
#     socketio.emit('Web_Mic_Event', RxData)
#     print('Receive Data from Mic')

# @socketio.event
# def Threshold_Event(RxData):
#     socketio.emit('Web_Threshold_Event', RxData)
#     print('Receive Data from Threshold Event')

# @socketio.event
# def Threshold_Number_Event(RxData):
#     socketio.emit('Web_Threshold_Value', RxData)
#     print('Receive Data from Threshold Value')

# @socketio.event
# def ChangeThreshold(data):
#     print('Received Threshold Change:', data)
#     socketio.emit('BBBW_ChangedThreshold', data)

last_received_time = {
    1: None,
    2: None,
    3: None,
    4: None
}

status_lock = Lock()
operational_status = {
    1: 0,
    2: 0,
    3: 0,
    4: 0
}

def BBBWs_Ping(BBBW):
    with status_lock:
        last_received_time[BBBW] = time.time()
        operational_status[BBBW] = 1

def check_BBBW_status():
    while True:
        with status_lock:
            current_time = time.time()
            for BBBW in last_received_time:
                if last_received_time[BBBW] is None or current_time - last_received_time[BBBW] > 5:
                    operational_status[BBBW] = 0
        time.sleep(5)
        print(operational_status)
        execute_db_query("INSERT INTO ping (BBBW1, BBBW2, BBBW3, BBBW4) VALUES (?, ?, ?, ?)",
                         (operational_status[1], operational_status[2], operational_status[3], operational_status[4]))

def BBBW_Status():
        while True:
            socketio.emit("Web_BBBW_Status", operational_status)
            time.sleep(5)

socketio.start_background_task(BBBW_Status)


# Starting the status check thread
Thread(target=check_BBBW_status, daemon=True).start()


#From Node.js
@socketio.event # Admin.html sends to server.js
def Image_base64(Rxdata):
    print('Image base64 string received: ', Rxdata)
    socketio.emit('Node_Image_Base64', Rxdata)

@socketio.event # Server.js sends to Admin.html
def Text_From_Image(Rxdata):
    print('Text from Image received: ', Rxdata)
    socketio.emit('Web_Text_From_Image', Rxdata)
    

#From Website
@socketio.event   
def Bus_Arrival_SQL(RxData):
    print(RxData)
    Bus_Arr_Dict = RxData
    Actual = Bus_Arr_Dict["realArrTime"]
    Predicted = Bus_Arr_Dict["predictedArrTime"]
    Bus_Number = Bus_Arr_Dict["busNo"]

    # Correct format to parse the datetime strings
    actual_datetime_format = "%a %b %d %Y %H:%M:%S GMT%z"
    predicted_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # Strip the unwanted part from the actual datetime string
    Actual = re.sub(r' \(.+\)$', '', Actual)

    try:
        # Parse the actual and predicted times
        actual_time = datetime.strptime(Actual, actual_datetime_format)
        predicted_time = datetime.strptime(Predicted, predicted_datetime_format)
        predicted_time = predicted_time.replace(tzinfo=timezone.utc)  # Make predicted_time timezone-aware
        
        # Convert actual_time to UTC for accurate comparison
        actual_time_utc = actual_time.astimezone(timezone.utc)
    except ValueError as e:
        print(f"Error parsing datetime: {e}")
        return

    # Calculate the time difference
    time_diff = actual_time_utc - predicted_time
    time_diff_seconds = int(time_diff.total_seconds())
    
    # Determine if the bus is early or late
    if time_diff_seconds < 0:
        early_late = "early"
        time_diff_seconds = abs(time_diff_seconds)
    elif time_diff_seconds > 0:
        early_late = "late"
    else:
        time_diff_text = "on time"
        execute_db_query("INSERT INTO bus (bus_number, actual_arrive_time, predicted_arrive_time, difference_in_time) VALUES (?, ?, ?, ?)",
                         (Bus_Number, Actual, Predicted, time_diff_text))
        return

    # Calculate minutes and seconds
    minutes, seconds = divmod(time_diff_seconds, 60)
    time_diff_text = f"{minutes} mins and {seconds} secs {early_late}"

    # Convert times back to the desired format
    def format_with_timezone(dt):
        return dt.strftime("%a %b %d %Y %H:%M:%S GMT%z")
    
    actual_time_formatted = format_with_timezone(actual_time)
    predicted_time_formatted = format_with_timezone(predicted_time.astimezone(actual_time.tzinfo))

    execute_db_query("INSERT INTO bus (bus_number, actual_arrive_time, predicted_arrive_time, difference_in_time) VALUES (?, ?, ?, ?)",
                     (Bus_Number, actual_time_formatted, predicted_time_formatted, time_diff_text))



@socketio.event
def Change_Settings_SQL(RxData):
    edge_force_threshold = RxData.get('edgeForceThreshold')
    edge_ir_dist_threshold = RxData.get('edgeIRDistanceThreshold')
    edge_prox_threshold = RxData.get('edgeProximityThreshold')
    bus_force_threshold = RxData.get('busForceThreshold')
    lighting_prox_threshold = RxData.get('lightingProximityThreshold')
    led_target = RxData.get('ledTarget')
    print("          WEEEE   ")
    execute_db_query("INSERT INTO settings (edge_force_threshold, edge_ir_dist_threshold, edge_prox_threshold, bus_force_threshold, lighting_prox_threshold, led_target) VALUES (?, ?, ?, ?, ?, ?)",
                     (edge_force_threshold, edge_ir_dist_threshold, edge_prox_threshold, bus_force_threshold, lighting_prox_threshold, led_target))

    #BBBW 2
    socketio.emit('BBBW2_edge_force_threshold', edge_force_threshold)
    socketio.emit('BBBW2_edge_ir_dist_threshold', edge_ir_dist_threshold)
    socketio.emit('BBBW2_edge_prox_threshold', edge_prox_threshold)

    #BBBW 3
    socketio.emit('BBBW3_bus_force_threshold', bus_force_threshold)
    socketio.emit('BBBW3_lighting_prox_threshold', lighting_prox_threshold)

    #BBBW4
    socketio.emit('BBBW4_led_target', led_target)


socketio.start_background_task(BBBW_Status)

def emit_settings_to_BBBWs():
    while True:
        print("\n\n\nSending Settings")
        conn = sqlite3.connect('busStop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT edge_force_threshold, edge_ir_dist_threshold, edge_prox_threshold, bus_force_threshold, lighting_prox_threshold, led_target FROM settings")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            # BBBW 2
            socketio.emit('BBBW2_edge_force_threshold', rows[-1][0])
            socketio.emit('BBBW2_edge_ir_dist_threshold', rows[-1][1])
            socketio.emit('BBBW2_edge_prox_threshold', rows[-1][2])

            # BBBW 3
            socketio.emit('BBBW3_bus_force_threshold', rows[-1][3])
            socketio.emit('BBBW3_lighting_prox_threshold', rows[-1][4])

            # BBBW 4
            socketio.emit('BBBW4_led_target', rows[-1][5])

        time.sleep(10)  # Emit settings every 10 seconds

socketio.start_background_task(emit_settings_to_BBBWs)



#From BBBW1: Cayden
@socketio.event
def BBBW1_Temperature(RxData):
    temperature = float(RxData)
    Send_All_Environment("temperature", temperature)
    # execute_db_query("INSERT INTO environment (temperature) VALUES (?)", (temperature,))
    socketio.emit('Web_BBBW1_Temperature', RxData)
    print('Receive Data from BBBW1 Temperature: ' + str(RxData))
    BBBWs_Ping(1)
    # socketio.emit("Web_BBBW_Status", operational_status) # Why does it work here



@socketio.event
def BBBW1_Noise(RxData):
    noise = int(RxData)
    Send_All_Environment("noise", noise)
    # execute_db_query("INSERT INTO environment (noise) VALUES (?)", (noise,))
    socketio.emit('Web_BBBW1_Noise', RxData)
    # print('Receive Data from BBBW1 Noise: ' + str(RxData))
    BBBWs_Ping(1)

@socketio.event
def BBBW1_Humidity(RxData):
    humidity = float(RxData)
    Send_All_Environment("humidity", humidity)
    # execute_db_query("INSERT INTO environment (humidity) VALUES (?)", (humidity,))
    socketio.emit('Web_BBBW1_Humidity', RxData)
    # print('Receive Data from BBBW1 Humidity: ' + str(RxData))
    BBBWs_Ping(1)


@socketio.event
def BBBW1_Pressure(RxData):
    pressure = float(RxData)
    Send_All_Environment("pressure", pressure)
    # execute_db_query("INSERT INTO environment (pressure) VALUES (?)", (pressure,))
    socketio.emit('Web_BBBW1_Pressure', RxData)
    # print('Receive Data from BBBW1 Pressure: ' + str(RxData))
    BBBWs_Ping(1)


@socketio.event
def BBBW1_VOC(RxData):
    voc = float(RxData)
    Send_All_Environment("voc", voc)
    # execute_db_query("INSERT INTO environment (voc) VALUES (?)", (voc,))
    socketio.emit('Web_BBBW1_VOC', RxData)
    # print('Receive Data from BBBW1 VOC: ' + str(RxData))
    BBBWs_Ping(1)





#From BBBW2: Rachel
@socketio.event
def BBBW2_Edge_Detect(RxData):
    edge_warning = bool(RxData)
    execute_db_query("INSERT INTO activity (edge_warning) VALUES (?)", (edge_warning,))
    socketio.emit('Web_BBBW2_Edging', RxData)
    print('Receive Data from BBBW2 Edge Detect: ' + str(RxData))
    BBBWs_Ping(2)





#From BBBW3: Xinglu
@socketio.event
def BBBW3_Motion_Event(RxData):
    human_presence = bool(RxData)
    execute_db_query("INSERT INTO activity (human_presence) VALUES (?)", (human_presence,))
    socketio.emit('Web_BBBW3_Motion_Event', RxData)
    print('Receive Data from BBBW3 Motion: ' + str(RxData))
    BBBWs_Ping(3)


@socketio.event
def BBBW3_Light(RxData):
    light = float(RxData)
    Send_All_Environment("light", light)
    # execute_db_query("INSERT INTO environment (light) VALUES (?)", (light,))
    socketio.emit('Web_BBBW3_Light', RxData)
    print('Receive Data from BBBW3 Light: ' + str(RxData))
    socketio.emit('BBBW4_LUX', RxData)
    BBBWs_Ping(3)


@socketio.event
def BBBW3_Bus_Force_Event(RxData):
    bus_detected = bool(RxData)
    execute_db_query("INSERT INTO activity (bus_detected) VALUES (?)", (bus_detected,))
    socketio.emit('Web_BBBW3_Bus_Force_Event', RxData) #Send info that bus is here to Rachel's BBBW2
    print('Receive Data from BBBW3 Bus Force: ' + str(RxData))
    socketio.emit('BBBW2_Bus_Presence', bool(RxData))
    BBBWs_Ping(3)



#From BBBW4: Kennz
@socketio.event
def BBBW4_Emergency_Event(RxData):
    emergency = RxData
    execute_db_query("INSERT INTO activity (emergency) VALUES (?)", (emergency,))
    socketio.emit('Web_BBBW4_Emergency_Event', RxData)
    print('Receive Data from BBBW4 Emergency Event: ' + str(RxData))
    BBBWs_Ping(4)


@socketio.event
def BBBW4_Rating_Event(RxData):
    rating = int(RxData)
    execute_db_query("INSERT INTO activity (rating) VALUES (?)", (rating,))
    socketio.emit('Web_BBBW4_Rating_Event', RxData)
    print('Receive Data from BBBW4 Rating Event: ' + str(RxData))
    BBBWs_Ping(4)


@socketio.event
def BBBW4_Minor_Emergency_Event(RxData):
    minor_emergency = RxData
    execute_db_query("INSERT INTO activity (minor_emergency) VALUES (?)", (minor_emergency,))
    socketio.emit('Web_BBBW4_Minor_Emergency_Event', RxData)
    print('Receive Data from BBBW4 Minor Emergency Event: ' + str(RxData))
    print("WEEE\n\n\n\n\n\n")
    BBBWs_Ping(4)

@socketio.event
def Announcement_Event(RxData):
    announcement = RxData
    socketio.emit('BBBW4_Announcement_Event', announcement)
    print('Receive Data from Website Announcement Event: ' + str(announcement))

@socketio.event
def BBBW4_LED_DutyCycle(RxData):
    Duty_Cycle = RxData
    socketio.emit('Web_BBBW4_Duty_Cycle_Event', Duty_Cycle)
    BBBWs_Ping(4)

@socketio.event
def BBBW4_PowerSaving(RxData):
    Duty_Cycle = bool(RxData)
    socketio.emit('Web_BBBW4_PowerSaving', Duty_Cycle)



if __name__ == '__main__':
    script_path = "js/server.js"
    subprocess.Popen(["node", script_path])
    #app.run(host='192.168.X.X')
    wsgi.server(eventlet.listen(("192.168.18.69", 5000)), app)
    print("Server Established")

