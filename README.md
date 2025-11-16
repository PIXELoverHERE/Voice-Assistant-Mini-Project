
## 🎙️ Voice Assistant Mini-Project

This is a **Python-based Voice Assistant** developed as a mini-project for college internals. It's designed to perform various common tasks using **voice commands**, demonstrating core concepts of speech recognition, natural language processing (NLP), and basic system interaction.

---

## ✨ Features

The Voice Assistant can handle a range of commands, including:

* **Greeting:** Responds to greetings like "hello" or "hi."
* **Time & Date:** Tells the current time and date.
* **Web Search:** Searches the web using a specified query.
* **Open Applications:** Launches common applications (e.g., Google Chrome, Notepad - *may require platform-specific configuration*).
* **Weather Updates:** Provides current weather for a specified location (requires an API key).
* **Wikipedia Search:** Reads out a summary from a Wikipedia topic.
* **Music Playback:** Plays a song or video on YouTube (simple implementation).
* **Self-Introduction:** States its name and purpose.
* **Exit:** Shuts down the assistant gracefully.

---

## 💻 Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python** | Primary programming language. |
| **`SpeechRecognition`** | For converting speech to text (STT). |
| **`pyttsx3`** | For converting text to speech (TTS) – the assistant's voice. |
| **`webbrowser`** | To open web links and perform searches. |
| **`wikipedia`** | To fetch information from Wikipedia. |
| **`requests`** | For making API calls (e.g., for weather). |
| **`datetime`** | To get current time and date. |
| **`os`** | For interacting with the operating system (e.g., opening apps). |

---

## 🚀 Setup and Installation

### 1. Prerequisites

Make sure you have **Python 3.x** installed on your system.

### 2. Clone the Repository

```bash
git clone <Your-Repository-URL>
cd <Your-Project-Folder>
