import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# 1. Environment variables load karein
load_dotenv()

# Agar .env kaam na kare toh temporary key yahan direct bhi de sakte hain
mistral_key = "xoIgbKyyUSP3VIl0hs9dQRsy5yQ8LZd4" 

app = Flask(__name__)
CORS(app)

# 2. LLM Model setup (Mistral)
my_llm = LLM(model="mistral/open-mistral-7b", api_key=mistral_key)

# 3. Agents Definition (Aapke original logic ke mutabiq)
wish_analyzer = Agent(
    role='Context Analyzer',
    goal='User ki input se relationship, mood aur occasion ki barikiyaan samajhna.',
    backstory='Aap mahir hain insani jazbaat aur social context ko decode karne mein.',
    llm=my_llm,
    allow_delegation=False
)

creative_writer = Agent(
    role='Emoji-Expert Creative Writer',
    goal='Dil-kash wishes likhna English mein, jinmein dher saare relevant emojis.',
    backstory='Aap aik modern digital writer hain jo emojis ko jazbaat ke taur par use karte hain.',
    llm=my_llm,
    allow_delegation=False
)

# 4. HTML Interface (Home Page)
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>WishNexa - AI Wish Generator</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #fdf2f8; display: flex; justify-content: center; padding: 40px; }
        .container { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 500px; text-align: center; }
        h1 { color: #db2777; margin-bottom: 10px; }
        input { width: 90%; padding: 15px; border: 2px solid #fbcfe8; border-radius: 12px; margin: 20px 0; font-size: 16px; }
        button { background: #db2777; color: white; border: none; padding: 15px 30px; border-radius: 12px; cursor: pointer; font-size: 18px; font-weight: bold; width: 100%; }
        button:hover { background: #be185d; }
        #result { margin-top: 30px; text-align: left; background: #fff5f8; padding: 20px; border-radius: 12px; white-space: pre-wrap; display: none; line-height: 1.6; border: 1px solid #fbcfe8; }
        .loader { color: #db2777; font-weight: bold; margin-top: 20px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ WishNexa AI</h1>
        <p>Who is the wish for and what message would you like to create?</p>
        <input type="text" id="userInput" placeholder="Example: Birthday wish for sister...">
        <button onclick="generateWishes()">Generate Magic Wishes 🚀</button>
        <div id="loader" class="loader">AI aapke jazbaat ko alfaz de raha hai... ✨</div>
        <div id="result"></div>
    </div>

    <script>
        async function generateWishes() {
            const input = document.getElementById('userInput').value;
            const resDiv = document.getElementById('result');
            const loader = document.getElementById('loader');

            if(!input) { alert("Write something!"); return; }

            resDiv.style.display = "none";
            loader.style.display = "block";

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: input })
                });
                const data = await response.json();
                loader.style.display = "none";
                resDiv.style.display = "block";
                resDiv.innerText = data.wish || data.error;
            } catch (e) {
                loader.style.display = "none";
                alert("connection error occurred.");
            }
        }
    </script>
</body>
</html>
"""

# 5. Routes
@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        user_input = data.get('message', '')

        if not user_input:
            return jsonify({"error": "Input is required"}), 400

        # Task 1: Analysis
        analysis_task = Task(
            description=f'Analyze the input: "{user_input}". Determine relationship and occasion.',
            expected_output='A very precise summary of the emotional profile.',
            agent=wish_analyzer
        )

        # Task 2: Creative Writing
        writing_task = Task(
            description='Create 2 versions of wishes in English in a sentence: Short, Heartfelt, and Fun with emojis.',
            expected_output='in two sentences Two beautifully formatted wish versions.',
            agent=creative_writer,
            context=[analysis_task]
        )

        # Crew Execution
        wishes_crew = Crew(
            agents=[wish_analyzer, creative_writer],
            tasks=[analysis_task, writing_task],
            process=Process.sequential
        )

        result = wishes_crew.kickoff()
        return jsonify({"wish": str(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)