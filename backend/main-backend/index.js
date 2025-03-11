const express = require('express');
const axios = require('axios');
const multer = require('multer');
const app = express();
const port = 5000;

const upload = multer({ dest: 'uploads/' });

app.post('/api/detect-disease', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:6000/detect', {}, {
            headers: { 'Content-Type': 'application/json' }
        });
        res.json(response.data);
        // res.json({message : "OK"});
    } catch (error) {
        res.status(500).json({ error: 'Error communicating with microservice' });
    }
});

app.listen(port, () => console.log(`Backend running on port ${port}`));