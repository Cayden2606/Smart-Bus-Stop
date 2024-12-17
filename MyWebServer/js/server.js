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

const CREDENTIALS = JSON.parse(JSON.stringify({
    "type": "service_account",
    "project_id": "image-to-text-428122",
    "private_key_id": "47b1755d2a35bba3a58ca63e70fce82e054b2112",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC4xRUfFlVKyE+p\nmj2YVRJqfihCZdrCrEDBxVjrUhN3vIe07ysgsD7yNUJ1t9GkFtYZRrhNgnPmTrPo\n1uxVHk/bcO4KdinAx+1Tqcf20LRcoKsvdnpeJaCExGlMDO9tvgzkXVFS9AR1adpI\nUQ2fvBrrIeS0AQK+dygnHZAbRKahK9LRh6wC2Vx2Ecar7cfGaQ0d91kNWlgFH7RD\nQ35Tfq+/KlfPWTZOUrltpnTM0m8+SvA9Nt8CkSgVwnOInLP/F1zdhCw2/IXYVesG\n7R11veZOYDDAxxWzrrkSiAPXQQ7GOBgD5GN8F43ynHnrRYOJ9BLeQJv0djr39PSW\nO4guXLaNAgMBAAECggEAIx6cwOOtExGHaMiPMBrtbO3tR4+WGN4GUf5phBL97cqZ\nLcgu9Z/iWwXKC9eEYrDPgY7qXZsv3eT0N8vQMG6aRa7NpBHpJkIqBza0ciKhwaBt\nYVBe+nGi9NFjZUfpI34V87sUB9UnWszjp062rPejUzGGR7uQcrTx3ht1pmUyWdxH\n9DIJg63vT3mGXU8Nu5KfL6z3B/EFKjJeBm5lwIKpGukhh9M++ZN+mGn1BXThfrcW\ni3FMrh2u5iebEkjelum2i/DtEH2cl9zsdYioXZk81d2eW5CB0vOuEihI2YNqtn9Q\n006+PzMTMPAQt6d6ZwyubbKaXDz3oMPHW/6AxvzdiQKBgQD3FCyzO/I+kCpjG0n0\nwD1uSRX2tfGHOQdI/PbLOOKofxYZk0GOeAHjzz+srwZFAHo7BBQN2pavFlijneA4\nRh+al4cQ1uCZuAbAxPt17uM+kYLX4kcmtGDVDvQgfCpJ2Lwxta732rrxcOQzRCPU\n57A+lbW/i3cVWJqlru2rRvUkuQKBgQC/cPeScYOVNZlr3Fy3dRPScygjKgQg4BSn\nVD7AfrCmI8UshpWgswZmY0UNtEeltzbOO7aWVJJtXn4waBlnDsciw0dyAAN8Qbw6\ncpYGM1EfmZbwiaWhudi5JH+WrwzWolvb5NI5aOQXdWY49hhdv8+CqslN6CpSjCzk\nklajRg9edQKBgGHUViKdoLwO3wmgu3ayS2CIha7KuZheBzlqF9m9a1lmAH0d5j4f\n3De0TrT0FBpsJvmJEtutai5nPa+DCk2dzlOqnasYOZQD3oCjPiGi9c1HVjRefuef\nUhvqMNVP9HqK23EfS+kNbSm+Fk0KNNnO5uTQ6EawVPVZwNnLWoWPse7ZAoGBAJsr\ndX+9gmnuh+xlMMGCpA5wSJg39iCvgA4gurxL8+K2G5t7esxGT2muDMqO1YP8fO+s\ndtJiukzrylxyBCUEVWRX5BEC8dBFd8voFLHx5k82rqFI8Helq4RlkQUR3dYaw1n4\nnmzqF/brsW96CUXzsr62r3P2OleuRrT96DtvDgYBAoGAaEDHGNlPXpW/eyKhb/t1\nfck1blU7JP7iCUOHCfs9q1KlSCwLCfOzGMEmEj9KxxFIV9IKUMpTyr+Zz0cbSmTY\nQWPbhoEZRvSC0Ls56p4WW4P/brY6EwezKSTPX/dVxlIczwASeHZA9wyFvVKWLd8z\n3E07PBLwBZXXaP6Jin5+nCM=\n-----END PRIVATE KEY-----\n",
    "client_email": "cayden-817@image-to-text-428122.iam.gserviceaccount.com",
    "client_id": "106185753972737944894",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cayden-817%40image-to-text-428122.iam.gserviceaccount.com",
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

