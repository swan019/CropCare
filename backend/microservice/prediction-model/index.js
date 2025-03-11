const express = require('express');
const fs = require('fs');
const app = express();
const port = 6000;

const diseases = JSON.parse(fs.readFileSync('diseases.json', 'utf8'));

app.post('/detect', (req, res) => {
    const randomDisease = diseases[Math.floor(Math.random() * diseases.length)];
    res.json(randomDisease);
});

app.listen(port, () => console.log(`Microservice running on port ${port}`));
