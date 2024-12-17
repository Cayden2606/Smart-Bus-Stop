---

# 🚏 **Smart Bus Stop System**

## 📄 **Project Overview**  
The **Smart Bus Stop System** enhances safety, convenience, and sustainability at bus stops using IoT technologies, real-time data monitoring, and human interaction systems. By integrating smart sensors, camera-based recognition, and energy-efficient solutions, this project improves commuter experiences while promoting urban efficiency.

---

## 🌟 **Key Features**

### 1. **Environmental Monitoring**  
- Measures **temperature**, **humidity**, **noise levels**, and **light intensity** in real-time.  
- Optimizes energy usage for lighting, heating, or cooling systems.  

### 2. **Proximity Warning System**  
- Multi-sensor safety alerts:  
  - **IR Distance Sensor** detects proximity to the road.  
  - **Force Sensors** and **Proximity Sensors** validate edge safety.  
- **Buzzer Alarm** triggers warnings if users step too close to the road.  

### 3. **Energy-Efficient Lighting**  
- Adaptive lighting system adjusts brightness based on:  
  - Human presence detection.  
  - Lux levels measured at the bus stop.  

### 4. **Bus Arrival Detection**  
- **Google Cloud Vision API** detects bus numbers from images captured by the camera.  
- **Text-to-Speech API** announces bus arrival, e.g., *"Bus 12 has arrived."*  

### 5. **Emergency Alert System**  
- **Button Alarm Click**: Emergency button sends immediate alerts to the server and dashboard.  
- **Analog Buttons** allow users to report issues or emergencies.  

### 6. **Admin Dashboard & Web Features**  
- Displays real-time environmental and safety data.  
- Logs user interactions and emergency alerts.  
- Provides real bus arrival timings through **LTA DataMall API**.  

---

## 🛠 **Technologies Used**

### **Hardware**  
- BeagleBone Black Wireless (BBBW)  
- Sensors:  
  - **Environment Click**: Temperature and Humidity  
  - **Mic Click**: Noise Levels  
  - **IR Distance**: Proximity Detection  
  - **Force Click**: Pressure Detection  
- **Camera**: For capturing bus arrival images  

### **Software**  
- **Node.js**: Backend server and API handling  
- **Python**: Data processing and sensor integration  
- **Google Cloud Vision API**: Text recognition from bus images  
- **HTML/CSS/JavaScript**: User dashboard and web interface  
- **Socket.io**: Real-time communication between server and devices  
- **LTA DataMall API**: Real-time bus timings  

---

## 🚀 **Setup Instructions**

### 1. **Install Node.js and Python**  
Ensure Node.js and Python are installed:  
- Download [Node.js](https://nodejs.org/)  
- Install Python from the [Python website](https://www.python.org/).  

### 2. **Install Required npm Packages**  
In the project directory, run:  
```bash
npm install express socket.io @google-cloud/vision fs path
```

### 3. **Set Up Google Cloud Vision API**  
1. **Create a Google Cloud Project**:  
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).  
2. **Enable the Vision API**.  
3. **Create a Service Account**:  
   - Navigate to **IAM & Admin > Service Accounts**.  
   - Generate and download the JSON key file.  
4. **Replace Credentials**:  
   - Update `server.js` with the JSON file credentials (private_key, client_email).  

### 4. **Run the Servers**  

#### Start the Node.js Server  
Run:  
```bash
node server.js
```

#### Start the Python Web Server  
Run:  
```bash
python WebServer.py
```

### 5. **Access the Dashboard**  
- Open your browser and visit:  
  ```http://your device's IP address:5000```  

---

## 📷 **Bus Arrival Detection Flow**

1. **Image Capture**:  
   - The camera takes a picture of the arriving bus.  
   - The image is converted to **base64** and sent to the backend server via **Socket.io**.  

2. **Google Vision API Processing**:  
   - The image is sent to Google Cloud Vision API for text recognition.  
   - Extracted bus numbers are filtered to match valid bus numbers at the stop.  

3. **Text-to-Speech Announcement**:  
   - If a bus number is detected, the system announces:  
     > *"Bus XX has arrived."*  

4. **Logs and Alerts**:  
   - Data is saved to the database, including timestamps and bus arrival details.  

---

## 💻 **Website Structure**

### **Home Page**  
- Overview of the Smart Bus Stop system.  
- Embedded video and 3D model showcasing the design and features.

### **About Page**  
- Mission and Vision statements:  
  > *"Our mission is to harness technological advancements to enhance the quality of life for our communities."*  
- Introduction to the team, project history, and values.  

### **Product Page**  
- Detailed information about system components and benefits.

### **Contact Page**  
- Contact information for feedback, support, and emergencies.

### **Admin Page**  
- Control dashboard for:  
  - Emergency alerts  
  - Sensor settings (thresholds, logs)  
  - Live data monitoring  

---

## 📝 **SQL Database Structure**

| Column                     | Description                       |  
|----------------------------|-----------------------------------|  
| **Temperature**            | Real-time temperature readings   |  
| **Humidity**               | Relative humidity levels         |  
| **Noise Levels**           | Detected noise levels            |  
| **Light Levels (LUX)**     | Measured light intensity         |  
| **Edge Detection**         | Proximity safety status          |  
| **Human Presence**         | User presence flag               |  
| **Emergency Call**         | Emergency alert status           |  
| **Bus Arrival Time Logs**  | Estimated vs Actual timings      |  

---

## 📊 **Future Enhancements**  
- Integration with solar panels for energy independence.  
- Passenger counting to determine bus occupancy.  
- Predictive AI for bus arrival times.  
- Real-time weather and air quality monitoring.

---

## 📜 **License**  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

---
