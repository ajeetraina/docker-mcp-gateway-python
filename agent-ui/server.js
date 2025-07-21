const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const AGENTS_URL = process.env.AGENTS_URL || 'http://localhost:7777';

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Serve the main UI
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'src', 'index.html'));
});

// Proxy to agents service
app.post('/api/chat', async (req, res) => {
    try {
        const response = await axios.post(`${AGENTS_URL}/chat`, req.body);
        res.json(response.data);
    } catch (error) {
        console.error('Error calling agents service:', error.message);
        res.status(500).json({ error: 'Failed to communicate with agents service' });
    }
});

app.get('/api/agents', async (req, res) => {
    try {
        const response = await axios.get(`${AGENTS_URL}/agents`);
        res.json(response.data);
    } catch (error) {
        console.error('Error getting agents:', error.message);
        res.status(500).json({ error: 'Failed to get agents list' });
    }
});

app.listen(PORT, () => {
    console.log(`Agent UI server running on port ${PORT}`);
});
