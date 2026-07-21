const axios = require('axios');
require('dotenv').config();

const MATRIX = {
    OFFLINE: {
        URL: "http://127.0.0.1:11434/api/chat",
        HEADERS: () => ({ "Content-Type": "application/json" }),
        models: {
            MANAGER: "deepseek-r1:1.5b",
            PLANNER: "deepseek-r1:1.5b",
            DESIGNER: "deepseek-r1:1.5b",
            CODER: "qwen2.5-coder:1.5b",
            TESTER: "qwen2.5-coder:1.5b"
        }
    }
};

async function dispatchTask(role, systemPrompt, userPrompt, mode = "OFFLINE") {
    const config = MATRIX[mode];
    const targetModel = config.models[role];
    const payload = {
        model: targetModel,
        messages: [{ role: "system", content: systemPrompt }, { role: "user", content: userPrompt }],
        stream: false
    };

    try {
        const response = await axios.post(config.URL, payload, { headers: config.HEADERS() });
        return response.data.message.content;
    } catch (error) {
        console.error(`💥 Router Error [${role}]:`, error.message);
        return null;
    }
}

module.exports = { dispatchTask };
