const express = require('express');
const https = require('https');
const socketIo = require('socket.io');
const vision = require('@google-cloud/vision');
const fs = require('fs');
const path = require('path');
const ioClient = require('socket.io-client');

const app = express();
const server = https.createServer(app);
const io = socketIo(server);


app.use(express.static('public'));

const socket = ioClient.connect('http://172.20.10.5:5000');

socket.on('connect', () => {
    console.log('Connected to the Python server');
});

socket.on('Node_Image_Base64', (data) => {
    console.log('Received base64 image string from Python server:', data);
    handleBase64Image(data);
});

const CREDENTIALS = JSON.parse(JSON.stringify({ // https://youtu.be/HgsjZhHBSV0?t=280 <<-- FOR MORE INFO
    "type": "service_account",
    "project_id": "!!ENTER API ID HERE!!",
    "private_key_id": "!!ENTER API KEY ID HERE!!",
    "private_key": "-----BEGIN PRIVATE KEY-----\n  !!ENTER API KEY HERE!! \n-----END PRIVATE KEY-----\n",
    "client_email": "!!ENTER CLIENT EMAIL!!",
    "client_id": "!!CLIENT ID!!",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "!!CERT URL!!",
    "universe_domain": "googleapis.com"
}));

const CONFIG = {
    credentials: {
        private_key: CREDENTIALS.private_key,
        client_email: CREDENTIALS.client_email
    }
};

const client = new vision.ImageAnnotatorClient(CONFIG);

const detectText = async (file_path) => {
    try {
        let [result] = await client.textDetection(file_path);
        if (result.fullTextAnnotation && result.fullTextAnnotation.text) {
            console.log(result.fullTextAnnotation.text);
            // Sends result.fullTextAnnotation.text to Webserver.py
            socket.emit('Text_From_Image', result.fullTextAnnotation.text);
        } else {
            console.log('No text detected in the image.');
        }
    } catch (error) {
        console.error('Error during text detection:', error);
    }
};

function handleBase64Image(base64String) {
    const base64Data = base64String.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(base64Data, 'base64');

    const tempFilePath = path.join(__dirname, 'temp_image.jpg');
    fs.writeFileSync(tempFilePath, buffer);

    detectText(tempFilePath)
}

server.listen(5000, () => {
    console.log('Server is running on port 5000');
});

