"""
Simple Chat with Claude
A beginner-friendly script to chat with Claude using the Anthropic API.
"""

import os
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable (loaded from .env file)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found!")
        print("Please create a .env file with: ANTHROPIC_API_KEY=your-api-key")
        return
    
    # Initialize the Anthropic client
    client = Anthropic(api_key=api_key)
    
    # Store the conversation history for API
    messages = []
    
    # Create filename with timestamp when conversation starts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"
    
    # Initialize the conversation file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"Conversation started on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
        print(f"Conversation will be saved to: {filename}")
    except Exception as e:
        print(f"Error creating conversation file: {str(e)}")
        return
    
    print("=" * 60)
    print("Welcome to Claude Chat!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("=" * 60)
    print()
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check if user wants to quit
        if user_input.lower() in ['quit', 'exit', 'bye']:
            # Add final timestamp to file
            try:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write("=" * 60 + "\n")
                    f.write(f"Conversation ended on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n")
            except Exception as e:
                print(f"Warning: Could not update file: {str(e)}")
            
            print(f"\nConversation ended. All messages saved to: {filename}")
            break
        
        # Skip empty messages
        if not user_input:
            continue
        
        # Add user message to conversation history
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Send message to Claude
            print("Claude: ", end="", flush=True)
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                messages=messages
            )
            
            # Get Claude's response text
            claude_response = response.content[0].text
            
            # Display Claude's response
            print(claude_response)
            print()
            
            # Add Claude's response to conversation history
            messages.append({"role": "assistant", "content": claude_response})
            
            # Auto-save the message pair to file
            try:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(f"You: {user_input}\n\n")
                    f.write(f"Claude: {claude_response}\n\n")
                    f.write("-" * 60 + "\n\n")
            except Exception as e:
                print(f"Warning: Could not save to file: {str(e)}")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            print()
            
            # Save error to file
            try:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(f"You: {user_input}\n\n")
                    f.write(f"{error_msg}\n\n")
                    f.write("-" * 60 + "\n\n")
            except Exception as save_error:
                print(f"Warning: Could not save error to file: {str(save_error)}")

if __name__ == "__main__":
    main()
