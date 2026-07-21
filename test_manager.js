const { dispatchTask } = require('./model_router');

async function runTest() {
    const systemPrompt = `You are an elite Tech Lead and Product Manager. 
Your job is to take a raw user request and convert it into a highly detailed, professional Product Requirement Document (PRD).
Include: 
1. Project Overview
2. Core Features
3. UI/UX Layout
4. Recommended Tech Stack.
Output ONLY the PRD content without conversational filler.`;

    const userPrompt = "create a finances tracker app for me";

    console.log("🚀 DeepSeek-1.5B (Manager) PRD bana raha hai... Wait kar...\n");
    
    const prd = await dispatchTask("MANAGER", systemPrompt, userPrompt);
    
    console.log("\x1b[36m==========================================\x1b[0m");
    console.log("\x1b[32m📝 MANAGER PRD OUTPUT:\x1b[0m");
    console.log("\x1b[36m==========================================\x1b[0m");
    console.log(prd);
    console.log("\x1b[36m==========================================\x1b[0m");
}

runTest();
