const fs = require('fs');
const path = require('path');
const { dispatchTask } = require('./model_router');

// 🧠 Ninja Technique 2: Markdown blocks se sirf asali code nikalna
function extractCode(text) {
    const match = text.match(/```[\w]*\n([\s\S]*?)```/);
    return match ? match[1].trim() : text.trim();
}

async function generateFiles(architecture) {
    const { projectName, files } = architecture;
    
    // Project ke naam ka ek clean folder name banate hain
    const folderName = projectName.replace(/\s+/g, '_').toLowerCase();
    const projectPath = path.join(__dirname, 'workspace', folderName);

    // Agar workspace folder nahi hai, toh bana do
    if (!fs.existsSync(projectPath)) {
        fs.mkdirSync(projectPath, { recursive: true });
    }

    console.log(`\n📂 Workspace ready: ${projectPath}\n`);

    // Har ek file ke liye loop chalayenge
    for (const file of files) {
        // Path me se shuru ka slash '/' hata dete hain (jaise '/html' ko 'index.html' banana)
        // Dummy test ke liye agar path me extension nahi hai, toh hum default laga denge.
        let safeFileName = file.path.replace(/^\/+/, '');
        if (!safeFileName.includes('.')) safeFileName += '.html'; // Fallback for dummy test

        console.log(`👨‍💻 Coder (Qwen-1.5B) likh raha hai: ${safeFileName} ...`);

        const systemPrompt = `You are an elite Senior Developer. 
Write the complete code for the requested file based on the description. 
CRITICAL RULE: Output ONLY the raw code inside a single Markdown code block (e.g., \`\`\`html ... \`\`\`). No explanations, no pleasantries, no chat.`;
        
        const userPrompt = `Project: ${projectName}\nFile: ${safeFileName}\nDescription: ${file.description}\n\nPlease write the complete and working code.`;

        // 🚀 Call the Majdoor (Qwen2.5-Coder:1.5b)
        let rawOutput = await dispatchTask("CODER", systemPrompt, userPrompt);
        
        if (!rawOutput) {
            console.log(`❌ Failed to get code for ${safeFileName}`);
            continue;
        }

        // DeepSeek/Qwen ka think tag aur markdown backticks hatao
        let cleanCode = rawOutput.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
        cleanCode = extractCode(cleanCode);

        // Actual file save karo
        const filePath = path.join(projectPath, safeFileName);
        
        // Agar file kisi sub-folder me hai (jaise components/app.js), toh pehle folder banao
        fs.mkdirSync(path.dirname(filePath), { recursive: true });
        fs.writeFileSync(filePath, cleanCode);
        
        console.log(`✅ File Saved: ${filePath}\n`);
    }

    console.log(`🎉 Project [${projectName}] is successfully generated! Check your workspace folder.`);
}

// Chota sa Test Logic
if (require.main === module) {
    const dummyArchitecture = {
        "projectName": "Test App",
        "files": [
            {
                "path": "index.html",
                "description": "A simple HTML file with a heading 'Hello World from CMF Phone' and linked to style.css."
            },
            {
                "path": "style.css",
                "description": "Basic CSS that sets background to dark gray and text to neon green."
            }
        ]
    };
    generateFiles(dummyArchitecture);
}

module.exports = { generateFiles };
