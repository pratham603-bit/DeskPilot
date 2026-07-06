import sys
from agent import chat

def main():
    history = []
    
    # Initialize conversation with a hidden prompt to generate the morning briefing seamlessly
    hidden_prompt = "The user just started the CLI. Call the daily_briefing tool and then greet the user with a 1-2 sentence summary of their day exactly like 'Good morning! Here's your briefing: you have X tasks and Y events scheduled for today. Let me know what you'd like to add.'"
    
    response = chat(hidden_prompt, history)
    
    # We don't append the hidden prompt to the visible history to keep it clean,
    # but the chat function maintains the SDK history internally. We just print the response.
    print(f"\nDeskPilot: {response}\n")
    
    # Add the initial model response to history so context is kept
    history.append({"role": "user", "parts": [hidden_prompt]})
    history.append({"role": "model", "parts": [response]})
    
    while True:
        try:
            user_input = input("> ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if user_input.strip().lower() == "exit":
            break
            
        if not user_input.strip():
            continue
            
        history.append({"role": "user", "parts": [user_input]})
        
        response = chat(user_input, history)
        
        history.append({"role": "model", "parts": [response]})
        
        print(f"DeskPilot: {response}\n")

if __name__ == "__main__":
    main()
