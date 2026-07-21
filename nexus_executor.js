const { exec } = require('child_process');
const fs = require('fs-extra');
const { dispatchTask } = require('./model_router');

const COLORS = {
    red: (txt) => `\x1b[31m${txt}\x1b[0m`,
    green: (txt) => `\x1b[32m${txt}\x1b[0m`,
    yellow: (txt) => `\x1b[33m${txt}\x1b[0m`,
    cyan: (txt) => `\x1b[36m${txt}\x1b[0m`
};

async function testAndHeal(fileName, currentAttempt = 1, maxAttempts = 3) {
    if (currentAttempt > maxAttempts) {
        console.log(COLORS.red(`\n❌ Self-Healing Failed after ${maxAttempts} retries. Manual review required.`));
        return false;
    }

    console.log(COLORS.yellow(`\n🛡️ [Self-Healing] Attempt ${currentAttempt}/${maxAttempts}: Running test for ${fileName}...`));
    
    return new Promise((resolve) => {
        exec(`node --check ./workspace/${fileName}`, async (error, stdout, stderr) => {
            if (!error) {
                console.log(COLORS.green(`\n✅ PASS: ${fileName} syntax validation clear!`));
                resolve(true);
            } else {
                const errorLog = stderr || error.message;
                console.log(COLORS.red(`\n⚠️ CRASH DETECTED inside ${fileName}!`));
                
                const fileContent = await fs.readFile(`./workspace/${fileName}`, 'utf8');
                
                // System prompt me strict tag wrapper use karne ko bolenge
                const systemPrompt = "You are an automated code repair bot. Fix the error. You MUST wrap your fixed code inside ```javascript ... ``` tags. Do NOT output anything outside these tags.";
                const userPrompt = `File Name: ${fileName}\n\nSource Code:\n${fileContent}\n\nTerminal Execution Error:\n${errorLog}`;
                
                let correctedCode = await dispatchTask("TESTER", systemPrompt, userPrompt, "OFFLINE");
                
                if (correctedCode) {
                    // 1. R1 ke reasoning <think> tags ko poora uda do
                    correctedCode = correctedCode.replace(/<think>[\s\S]*?<\/think>/gi, '');
                    
                    // 2. Strict Extraction: Sirf ```javascript aur ``` ke beech ka content nikalo
                    let cleanCode = "";
                    const codeMatch = correctedCode.match(/```(?:javascript|js)?\n([\s\S]*?)```/i);
                    
                    if (codeMatch && codeMatch[1]) {
                        cleanCode = codeMatch[1].trim(); // Extract exact code
                    } else {
                        // Agar model tag bhool gaya, toh direct trim karke try karo
                        cleanCode = correctedCode.trim();
                    }
                    
                    await fs.outputFile(`./workspace/${fileName}`, cleanCode);
                    console.log(COLORS.green(`🔧 Fixed patch injected into ${fileName}. Re-running test...`));
                    resolve(await testAndHeal(fileName, currentAttempt + 1, maxAttempts));
                } else {
                    resolve(false);
                }
            }
        });
    });
}

module.exports = { testAndHeal };
