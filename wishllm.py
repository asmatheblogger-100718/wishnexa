import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# 1. Environment variables load karen
load_dotenv()
# Is line ko temporary add karein taake confirm ho jaye ke key sahi hai
mistral_key = "xoIgbKyyUSP3VIl0hs9dQRsy5yQ8LZd4" 

# 2. LLM Model setup (Mistral)
my_llm = LLM(model="mistral/open-mistral-7b", api_key=mistral_key)

# 3. Agents Definition
wish_analyzer = Agent(
    role='Context Analyzer',
    goal='User ki input se relationship, mood aur occasion ki barikiyaan samajhna.',
    backstory='Aap mahir hain insani jazbaat aur social context ko decode karne mein. Aap samajhte hain ke kab mazaq (funny) hona hai aur kab sanjeeda (emotional).',
    llm=my_llm,
    allow_delegation=False
)

creative_writer = Agent(
    role='Emoji-Expert Creative Writer',
    goal='Dil-kash wishes likhna Roman Urdu mein, jinmein dher saare relevant emojis aur behtareen formatting ho.',
    backstory='Aap aik modern digital writer hain jo emojis ko jazbaat ke taur par use karte hain. Aap ki likhi hui wishes direct dil par asar karti hain.',
    llm=my_llm,
    allow_delegation=False
)

# 4. Main Function for Terminal Execution
def run_wishes_app():
    print("\n" + "✨"*15)
    print(" 🌟 AI MAGIC WISHES GENERATOR 🌟 ")
    print("✨"*15)
    print("Tip: Program band karne ke liye 'exit' likhen.")

    while True:
        # Terminal Input
        user_input = input("\n📝 Kiske liye aur kya message likhna hai? \n(Example: Birthday wish for younger sister who is very annoying but cute): ")

        if user_input.lower() == 'exit':
            print("\nKhuda Hafiz! 👋✨")
            break

        # Task 1: Analysis
        analysis_task = Task(
            description=f'Analyze the input: "{user_input}". Determine: 1. Relationship 2. Occasion 3. Exact Tone.',
            expected_output='A summary of the emotional profile for the wish.',
            agent=wish_analyzer
        )

        # Task 2: Creative Writing with Emojis
        writing_task = Task(
            description=(
                'Create 3 versions of wishes in Roman Urdu: \n'
                '1. Short & Sweet (Minimalist) \n'
                '2. Heartfelt & Deep (Emotional) \n'
                '3. Fun & Quirky (With extra emojis) \n'
                'Use lots of relevant emojis and separate each version clearly.'
            ),
            expected_output='Three beautifully formatted wish versions with heavy emoji usage.',
            agent=creative_writer,
            context=[analysis_task]
        )

        # Crew Execution
        wishes_crew = Crew(
            agents=[wish_analyzer, creative_writer],
            tasks=[analysis_task, writing_task],
            process=Process.sequential
        )

        print("\n🚀 AI aapke jazbaat ko alfaz de raha hai...")
        result = wishes_crew.kickoff()

        print("\n" + "✅"*20)
        print(result)
        print("✅"*20)

if __name__ == "__main__":
    run_wishes_app()