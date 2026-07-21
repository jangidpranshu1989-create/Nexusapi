const http = require('http');

const payload = JSON.stringify({
    model: "deepseek-r1:1.5b",
    messages: [
        { role: "system", content: "You are an elite Tech Lead. Make a strict PRD for the user's idea." },
        { role: "user", content: "create a finances tracker app for me" }
    ],
    stream: true // Ye jadoo karega!
});

const options = {
    hostname: '127.0.0.1',
    port: 11434,
    path: '/api/chat',
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': payload.length }
};

console.log("🚀 Live Typing Start (DeepSeek-1.5B)...\n");

const req = http.request(options, (res) => {
    res.on('data', (chunk) => {
        const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
        for (const line of lines) {
            const data = JSON.parse(line);
            if (data.message && data.message.content) {
                process.stdout.write(data.message.content); // Live print karega
            }
        }
    });
});

req.on('error', (e) => console.error(`Problem: ${e.message}`));
req.write(payload);
req.end();
