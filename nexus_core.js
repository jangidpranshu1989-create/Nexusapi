const { dispatchTask } = require('./model_router');
const { generateArchitecture } = require('./nexus_planner');
const { generateFiles } = require('./nexus_coder');

async function runNexusAgent(userIdea) {
    console.log(`\n🚀 [NEXUS AGENT ACTIVATED]`);
    console.log(`🎯 Goal: ${userIdea}\n`);
    console.log("==================================================");

    // ---------------------------------------------------------
    // PHASE 1: MANAGER (Idea -> PRD)
    // ---------------------------------------------------------
    console.log("🧠 PHASE 1: MANAGER (DeepSeek-1.5B) is writing the PRD...");
    const managerSystemPrompt = `You are an elite Tech Lead and Product Manager. 
Convert the user's idea into a highly detailed, professional Product Requirement Document (PRD).
Include: 1. Project Overview, 2. Core Features, 3. UI/UX Layout, 4. Tech Stack.
Output ONLY the PRD content without conversational filler.`;
    
    const prd = await dispatchTask("MANAGER", managerSystemPrompt, userIdea);
    if (!prd) {
        console.log("❌ Mission Failed: Manager could not generate PRD.");
        return;
    }
    console.log("✅ PRD Generated successfully!\n");

    // ---------------------------------------------------------
    // PHASE 2: PLANNER (PRD -> JSON Architecture)
    // ---------------------------------------------------------
    console.log("📐 PHASE 2: PLANNER (DeepSeek-1.5B) is designing the file structure...");
    const architecture = await generateArchitecture(prd);
    
    if (!architecture || !architecture.files || architecture.files.length === 0) {
        console.log("❌ Mission Failed: Planner could not generate a valid JSON architecture.");
        return;
    }
    // Note: generateArchitecture already prints success logs, so we move on.

    // ---------------------------------------------------------
    // PHASE 3: CODER (JSON -> Actual Files)
    // ---------------------------------------------------------
    console.log("\n👨‍💻 PHASE 3: CODER (Qwen-1.5B) is writing the code...");
    await generateFiles(architecture);

    console.log("\n==================================================");
    console.log(`🏆 MISSION ACCOMPLISHED! Your app is ready in the workspace folder.`);
    console.log("==================================================\n");
}

// 🎯 Terminal se User Input uthana
const args = process.argv.slice(2);
const idea = args.length > 0 ? args.join(" ") : "Create a simple digital clock app using HTML, CSS, and JS";

runNexusAgent(idea);
