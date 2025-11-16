import speech_recognition as sr
import os
import webbrowser
import datetime
import platform
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

# https://youtu.be/Z3ZAJoi4x6Q

# Initialize TTS using pyttsx3 (speaks directly without MP3 files)
tts_engine = None
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_available = True
    print("pyttsx3 TTS initialized successfully")
except ImportError:
    print("Warning: pyttsx3 not available. Install it for text-to-speech")
    print("Run: pip install pyttsx3")
    tts_available = False
except Exception as e:
    print(f"Warning: Could not initialize pyttsx3: {e}")
    tts_available = False

# Initialize Llama model from HuggingFace
llama_model = None
llama_tokenizer = None
try:
    model_name = "meta-llama/Llama-2-7b-chat-hf"  # Using Llama 2, can be changed to other Llama models
    print("Loading Llama model from HuggingFace...")
    llama_tokenizer = AutoTokenizer.from_pretrained(model_name)
    llama_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        low_cpu_mem_usage=True
    )
    print("Llama model loaded successfully")
except Exception as e:
    print(f"Warning: Could not load Llama model: {e}")
    print("AI features may be limited. Trying alternative model...")
    try:
        # Fallback to a smaller model
        model_name = "microsoft/DialoGPT-medium"
        llama_tokenizer = AutoTokenizer.from_pretrained(model_name)
        llama_model = AutoModelForCausalLM.from_pretrained(model_name)
        print("Fallback model loaded successfully")
    except Exception as e2:
        print(f"Could not load fallback model: {e2}")

def say(text):
    """Use pyttsx3 to speak text directly without creating MP3 files"""
    try:
        if not tts_available or tts_engine is None:
            print(text)  # Fallback to printing text
            return
        
        # Stop any current speech before speaking new text
        try:
            tts_engine.stop()
        except:
            pass
        
        # Speak directly using pyttsx3 (no MP3 files created)
        tts_engine.say(text)
        tts_engine.runAndWait()
                
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        print(text)  # Fallback to printing text

def get_ai_response(query):
    """Get AI response using Llama model from HuggingFace"""
    if llama_model is None or llama_tokenizer is None:
        return "I'm sorry, the AI model is not available. Please try again later."
    
    try:
        # Format the prompt for Llama (using chat template if available)
        if hasattr(llama_tokenizer, 'apply_chat_template'):
            messages = [{"role": "user", "content": query}]
            prompt = llama_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt = f"User: {query}\nAssistant:"
        
        # Tokenize input
        inputs = llama_tokenizer.encode(prompt, return_tensors="pt")
        
        # Move inputs to same device as model
        if torch.cuda.is_available():
            inputs = inputs.cuda()
        
        # Generate response
        with torch.no_grad():
            outputs = llama_model.generate(
                inputs,
                max_new_tokens=150,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=llama_tokenizer.eos_token_id if llama_tokenizer.pad_token_id is None else llama_tokenizer.pad_token_id,
                eos_token_id=llama_tokenizer.eos_token_id
            )
        
        # Decode response (only the new tokens)
        response = llama_tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        
        # Clean up response
        response = response.strip()
        
        return response if response else "I'm not sure how to respond to that."
    except Exception as e:
        print(f"AI response error: {e}")
        return "I encountered an error processing your request. Please try again."

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # r.pause_threshold =  0.6
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            print(f"Error: {e}")
            return "Some Error Occurred. Sorry from Jarvis"

if __name__ == '__main__':
    print('Welcome to Jarvis A.I')
    say("Jarvis A.I")
    
    # Windows directory paths
    user_profile = os.path.expanduser("~")
    windows_directories = {
        "documents": os.path.join(user_profile, "Documents"),
        "downloads": os.path.join(user_profile, "Downloads"),
        "desktop": os.path.join(user_profile, "Desktop"),
        "pictures": os.path.join(user_profile, "Pictures"),
        "videos": os.path.join(user_profile, "Videos"),
        "music": os.path.join(user_profile, "Music"),
        "appdata": os.path.join(user_profile, "AppData"),
        "appdata local": os.path.join(user_profile, "AppData", "Local"),
        "appdata roaming": os.path.join(user_profile, "AppData", "Roaming"),
        "onedrive": os.path.join(user_profile, "OneDrive"),
    }
    
    while True:
        try:
            print("Listening...")
            query = takeCommand()
            
            # Skip if query is an error message
            if query == "Some Error Occurred. Sorry from Jarvis":
                continue
            
            query_lower = query.lower().strip()
            
            # Check for simple "jarvis quit" command to stop the loop
            if "jarvis quit" in query_lower:
                try:
                    say("Goodbye! Shutting down Jarvis.")
                except:
                    pass  # Don't block exit if TTS fails
                print("Goodbye! Shutting down Jarvis.")
                break  # Exit the loop cleanly
            
            # Handle site opening
            sites_opened = False
            sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"], 
                    ["google", "https://www.google.com"], ["stake", "https://stake.ac"], 
                    ["spotify", "https://www.spotify.com"]]
            for site in sites:
                if f"open {site[0]}" in query_lower:
                    say(f"Opening {site[0]} sir...")
                    webbrowser.open(site[1])
                    sites_opened = True
                    break
            
            if sites_opened:
                continue
            
            # Handle Windows directory opening
            dir_opened = False
            if "open" in query_lower:
                for dir_name, dir_path in windows_directories.items():
                    if dir_name in query_lower and os.path.exists(dir_path):
                        say(f"Opening {dir_name} folder...")
                        if platform.system() == "Windows":
                            os.startfile(dir_path)
                        else:
                            os.system(f"open '{dir_path}'" if platform.system() == "Darwin" else f"xdg-open '{dir_path}'")
                        dir_opened = True
                        break
            
            if dir_opened:
                continue
            
            # Handle music opening
            if "open music" in query_lower:
                musicPath = os.path.join(windows_directories["downloads"], "downfall-21371.mp3")
                if os.path.exists(musicPath):
                    if platform.system() == "Windows":
                        os.startfile(musicPath)
                    else:
                        os.system(f"open '{musicPath}'" if platform.system() == "Darwin" else f"xdg-open '{musicPath}'")
                    say("Playing music...")
                else:
                    say("Music file not found in Downloads folder.")
                continue

            # Handle time query
            elif "the time" in query_lower or "what time" in query_lower or "time now" in query_lower:
                hour = datetime.datetime.now().strftime("%H")
                min = datetime.datetime.now().strftime("%M")
                say(f"Sir time is {hour} bajke {min} minutes")
                print(f"Current time: {hour}:{min}")

            # Handle FaceTime/Network settings
            elif "open facetime" in query_lower or "open network" in query_lower:
                if platform.system() == "Windows":
                    os.system("start ms-availablenetworks:")
                    say("Opening network settings...")
                else:
                    os.system("open /System/Applications/FaceTime.app")
                    say("Opening FaceTime...")
                continue

            # Handle password manager
            elif "open pass" in query_lower:
                if platform.system() == "Windows":
                    os.system("start passky")
                    say("Opening password manager...")
                else:
                    os.system("open /Applications/Passky.app")
                    say("Opening password manager...")
                continue

            # Handle file creation
            elif "create file" in query_lower or "make file" in query_lower:
                match = re.search(r'(?:create|make)\s+file\s+(?:called|named)?\s*["\']?([^"\']+)["\']?', query_lower)
                if match:
                    filename = match.group(1).strip()
                    try:
                        with open(filename, 'w') as f:
                            f.write("")  # Create empty file
                        say(f"File {filename} created successfully")
                        print(f"File {filename} created successfully")
                    except Exception as e:
                        error_msg = f"Error creating file: {str(e)}"
                        say(error_msg)
                        print(error_msg)
                else:
                    say("Please specify a filename. For example: create file test.txt")
                continue
            
            # Handle file deletion
            elif "delete file" in query_lower or "remove file" in query_lower:
                match = re.search(r'(?:delete|remove)\s+file\s+(?:called|named)?\s*["\']?([^"\']+)["\']?', query_lower)
                if match:
                    filename = match.group(1).strip()
                    try:
                        if os.path.exists(filename):
                            os.remove(filename)
                            say(f"File {filename} deleted successfully")
                            print(f"File {filename} deleted successfully")
                        else:
                            say(f"File {filename} not found")
                            print(f"File {filename} not found")
                    except Exception as e:
                        error_msg = f"Error deleting file: {str(e)}"
                        say(error_msg)
                        print(error_msg)
                else:
                    say("Please specify a filename. For example: delete file test.txt")
                continue

            # Handle chat reset
            elif "reset chat" in query_lower:
                say("Chat history has been reset.")
                print("Chat history reset")
                continue

            # Use AI model for general queries
            else:
                print("Processing with AI...")
                ai_response = get_ai_response(query)
                print(f"Jarvis: {ai_response}")
                
                # Ensure AI response is spoken
                if ai_response and ai_response.strip():
                    say(str(ai_response).strip())
                else:
                    say("I couldn't generate a response. Please try again.")
                
        except KeyboardInterrupt:
            print("\nShutting down Jarvis...")
            break  # Exit the loop cleanly
        except Exception as e:
            print(f"Unexpected error: {e}")
            continue





        # say(query)