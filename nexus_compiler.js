const fs = require('fs-extra');
const { generateArchitecture } = require('./nexus_planner');
const { testAndHeal } = require('./nexus_executor');
const { dispatchTask } = require('./model_router');

const COLORS = {
    magenta: (txt) => `\x1b[35m${txt}\x1b[0m`,
    blue: (txt) => `\x1b[34m${txt}\x1b[0m`,
    green: (txt) => `\x1b[32m${txt}\x1b[0m`,
    yellow: (txt) => `\x1b[33m${txt}\x1b[0m`
};

async function compileProject(userPrompt) {
    console.log(COLORS.magenta(`\n🚀 [NEXUS MANAGER] Booting Multi-Agent Swarm...`));
    console.log(COLORS.magenta(`Target Project: "${userPrompt}"\n`));

    // --- PHASE 1: MANAGER (Mistral) ---
    console.log(COLORS.blue(`👔 MANAGER (Mistral) is refining requirements...`));
    const managerSystem = "You are a Tech Lead Manager. Convert the user's raw idea into a strict, clear 3-sentence technical product requirement. No fluff.";
    const refinedPrompt = await dispatchTask("MANAGER", managerSystem, userPrompt, "OFFLINE");
    console.log(COLORS.blue(`📝 Refined PRD:\n${refinedPrompt.trim()}\n`));

    // --- PHASE 2: PLANNER (Qwen 2.5 Coder) ---
    console.log(COLORS.yellow(`📐 PLANNER (Qwen) is designing architecture...`));
    const plan = await generateArchitecture(refinedPrompt);
    if (!plan) return console.log("❌ Pipeline stopped: Planner failed.");

    // --- PHASE 3: CODER (DeepSeek-R1 7B) ---
    for (const fileObj of plan.files) {
        console.log(COLORS.green(`\n⚙️ CODER (DeepSeek 7B) is building: ${fileObj.path}...`));
        
        const coderSystem = "You are an elite programmer. Write ONLY the exact code for the requested file. You MUST wrap your code in ``` tags. Do NOT write any conversational text outside the code block.";
        const coderUser = `Project: ${plan.projectName}\nFile: ${fileObj.path}\nLogic Required: ${fileObj.description}\n\nWrite the complete code.`;
        
        let codeResponse = await dispatchTask("CODER", coderSystem, coderUser, "OFFLINE");
        
        if (codeResponse) {
            // Remove R1's internal thinking process completely
            codeResponse = codeResponse.replace(/<think>[\s\S]*?<\/think>/gi, '');
            
            // Extract pure code block
            const codeMatch = codeResponse.match(/```(?:[a-zA-Z]*)?\n([\s\S]*?)```/i);
            const pureCode = codeMatch && codeMatch[1] ? codeMatch[1].trim() : codeResponse.trim();
            
            await fs.outputFile(`./workspace/${fileObj.path}`, pureCode);
            console.log(COLORS.green(`✅ File saved: ${fileObj.path}`));
            
            // --- PHASE 4: TESTER (DeepSeek-R1 1.5B) ---
            await testAndHeal(fileObj.path);
        } else {
            console.log(COLORS.yellow(`⚠️ Coder failed to generate content for ${fileObj.path}`));
        }
    }

    console.log(COLORS.magenta(`\n🎉 [SWARM COMPLETE] Project is fully compiled and tested in the workspace!\n`));
}

// Run the script with terminal arguments
const inputArgs = process.argv.slice(2).join(" ");
if(inputArgs) {
    compileProject(inputArgs);
} else {
    console.log("Please provide a prompt! Example: node nexus_compiler.js 'Make a simple math calculator api'");
}
