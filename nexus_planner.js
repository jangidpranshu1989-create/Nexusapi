const { dispatchTask } = require('./model_router');

// 🧠 The Bracket Matcher: Faltu kachra hatane ki ninja technique
function extractFirstJSON(text) {
    const start = text.indexOf('{');
    if (start === -1) return null;
    
    let openBrackets = 0;
    for (let i = start; i < text.length; i++) {
        if (text[i] === '{') openBrackets++;
        if (text[i] === '}') {
            openBrackets--;
            if (openBrackets === 0) {
                return text.substring(start, i + 1); // Exact pehla object mil gaya
            }
        }
    }
    return null;
}

async function generateArchitecture(prd) {
    const systemPrompt = `You are an elite Software Architect. 
Break down the PRD into a strict JSON architecture.
CRITICAL RULE: Output exactly ONE valid JSON object and STOP. Do not generate anything else.
Format: { "projectName": "Name", "files": [ { "path": "filename.ext", "description": "logic details" } ] }`;

    const userPrompt = `Here is the PRD:\n${prd}\n\nThink deeply, then provide ONLY the JSON.`;

    console.log("📐 Planner (DeepSeek-1.5B) Architecture (JSON) design kar raha hai... Wait kar...\n");
    
    let rawOutput = await dispatchTask("PLANNER", systemPrompt, userPrompt);

    if (!rawOutput) {
        console.log("❌ Planner se koi response nahi aaya.");
        return null;
    }

    // Step 1: <think> tags hatao
    let cleanText = rawOutput.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
    
    // Step 2: Sirf pehla asali JSON object nikalo
    let cleanJSON = extractFirstJSON(cleanText);

    try {
        const architecture = JSON.parse(cleanJSON);
        console.log(`\x1b[32m✅ Architecture generated: ${architecture.files.length} files planned.\x1b[0m`);
        console.log(JSON.stringify(architecture, null, 2));
        return architecture;
    } catch (e) {
        console.error("💥 Architect failed to produce valid JSON. Raw text was:\n", cleanJSON || cleanText);
        return null;
    }
}

if (require.main === module) {
    const dummyPRD = "Create a simple finance tracker with HTML, CSS, and JS. It needs a form to add expenses and a list to show them.";
    generateArchitecture(dummyPRD);
}

module.exports = { generateArchitecture };
