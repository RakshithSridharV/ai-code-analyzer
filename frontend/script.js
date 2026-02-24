async function analyzeCode() {
    const code = document.getElementById("code").value;
    const resultBox = document.getElementById("result");

    resultBox.innerText = "🔍 Analyzing code...";

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();

        let output = "";
        output += "🔍 CODE ANALYSIS RESULT\n";
        output += "============================\n\n";

        // 🔤 LANGUAGE
        output += "🔤 LANGUAGE\n";
        output += `• Detected / Selected: ${data.language ?? "Unknown"}\n\n`;

        // 🧠 AI INSIGHTS
        output += "🧠 AI INSIGHTS\n";
        output += `• Prediction: ${data.ai?.prediction ?? "N/A"}\n`;
        output += `• Optimization Priority: ${data.ai?.optimization_priority ?? "N/A"}\n\n`;

        // 📊 COMPLEXITY ANALYSIS
        output += "📊 COMPLEXITY ANALYSIS\n";
        output += `• Time Complexity: ${data.analysis?.time_complexity ?? "Unknown"}\n`;
        output += `• Space Complexity: ${data.analysis?.space_complexity ?? "Unknown"}\n\n`;

        // 🚨 DETECTED PATTERNS
        output += "🚨 DETECTED PATTERNS\n";
        if (
            data.patterns &&
            data.patterns.length > 0 &&
            !data.patterns.includes("efficient_code")
        ) {
            data.patterns.forEach(p => {
                output += `• ${p.replaceAll("_", " ")}\n`;
            });
        } else {
            output += "• No inefficient patterns detected\n";
        }

        // 💡 SUGGESTIONS
        output += "\n💡 SUGGESTIONS\n";
        if (data.suggestions && data.suggestions.length > 0) {
            data.suggestions.forEach(s => {
                output += `• ${s}\n`;
            });
        } else {
            output += "• No suggestions available\n";
        }

        // 🚀 OPTIMIZED CODE / SUGGESTION
        if (data.optimization) {
            output += "\n🚀 OPTIMIZED CODE (Suggestion)\n";
            output += "----------------------------\n";
            output += typeof data.optimization === "string"
                ? data.optimization
                : data.optimization.optimized_code ?? "No optimized code available";
            output += "\n";
        }

        // 📈 QUALITY SCORE
        output += `\n📈 QUALITY SCORE: ${data.quality_score ?? "N/A"} / 100\n`;

        resultBox.innerText = output;

    } catch (error) {
        console.error(error);
        resultBox.innerText = "❌ Error: Unable to connect to backend.";
    }
}