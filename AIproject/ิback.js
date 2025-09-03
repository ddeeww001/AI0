const express = require('express');
const { spawn } = require('child_process');

const app = express();
const port = 3000;

// รับข้อมูลจากหน้า page1.html
app.use(express.json());

app.post('/run-ai', (req, res) => {
    // รับ input จาก client
    const inputData = req.body.input;

    // เรียกใช้งาน Ai.py ด้วย Python
    const pythonProcess = spawn('python', ['Ai.py', inputData]);

    let result = '';
    pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        res.json({ output: result });
    });
});

app.listen(port, () => {
    console.log(`Backend server running at http://localhost:${port}`);
});