# Oasis Infobyte SIP — Python Programming Internship
## Task 1: Voice Assistant (Advanced Tier)

![Python Version](https://img.shields.io/badge/Python-3.8%2B%20%7C%203.14-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Completed%20%26%20Tested-brightgreen.svg)
![Tier](https://img.shields.io/badge/SIP%20Tier-Advanced-purple.svg)

---

## 1. Project Title
**Oasis Intelligent Voice Assistant** (`Oasis Voice Assistant`)

---

## 2. Oasis Infobyte SIP Task
* **Organization:** Oasis Infobyte (Oasis SIP)
* **Domain:** Python Programming Internship
* **Task Identifier:** Task 1 — Voice Assistant
* **Target Tier:** Advanced Tier

---

## 3. Objective
The primary goal of this project is to develop a Python-based voice assistant capable of:
1. Capturing spoken audio through the user's microphone.
2. Converting spoken language to text via Speech Recognition algorithms.
3. Parsing complex natural language intents.
4. Performing system operations, fetching live external data, scheduling timers, and automating tasks.
5. Providing audible responses using an offline Text-to-Speech (TTS) synthesizer.

---

## 4. Core Features
* **Dynamic Time-Aware Greetings:** Contextual greetings based on time of day (Morning, Afternoon, Evening).
* **System Time & Date:** Accurate real-time system clock and calendar queries.
* **Web Search:** Direct queries routed to default web browser via Google.
* **Website Launching:** Quick voice access to popular platforms (Google, YouTube, GitHub, Wikipedia, StackOverflow, etc.).
* **Polite Exit & Shutdown:** Clean termination on voice/text commands (`exit`, `quit`, `goodbye`).

---

## 5. Advanced Features (Advanced Tier)
* **Natural Language Intent Handling:** Multi-pattern regex token matching that supports phrasing variations without fragile exact-match constraints.
* **Live Weather Forecasting:**
  - Full support for OpenWeatherMap API (configured via `WEATHER_API_KEY`).
  - Seamless zero-configuration fallback to live `wttr.in` JSON API if no API key is provided.
  - Returns condition, temperature (°C), feels-like index, and humidity.
* **Non-Blocking Background Reminders / Timers:**
  - Supports seconds, minutes, and hours (e.g., *"set a reminder for 10 seconds to drink water"*).
  - Uses background worker threads so the assistant remains responsive to new commands.
  - Provides audible and visual alert once the timer completes.
* **Voice-Guided Email Composition (smtplib):**
  - Interactive multi-step prompt collecting recipient, subject, and message.
  - Mandatory confirmation check (*"Please confirm: Do you want me to send this email?"*) before sending.
  - Secure credential management through environment variables.
* **Local Knowledge Base & Utilities:**
  - Built-in instant answers for computer science & AI definitions (Python, Machine Learning, AI).
  - Fun commands (programming jokes, facts).
  - Cross-platform desktop application launcher (Calculator, Notepad, Command Prompt, Task Manager).
* **Dual-Input Mode (Voice & Text Fallback):**
  - Seamlessly accepts microphone speech or typed input (`--text` mode) for development, testing, and noisy environments.

---

## 6. Technologies Used
* **Programming Language:** Python 3 (Python 3.8 - 3.14+)
* **Speech Recognition:** `SpeechRecognition` (Google Speech API backend)
* **Audio Drivers:** `sounddevice` & `pyaudio` (Multi-backend audio capture)
* **Text-to-Speech:** `pyttsx3` (Offline SAPI5 / NSSpeechSynthesizer / espeak engine)
* **HTTP & Web Data:** `requests`
* **Email & Network:** `smtplib`, `ssl`, `email.message`
* **Environment Management:** `python-dotenv`
* **Operating System Tools:** `subprocess`, `platform`, `webbrowser`, `threading`

---

## 7. Project Structure
```text
OIBSIP/
└── Python-Task1-VoiceAssistant/
    ├── main.py                  # Core assistant application & intent engine
    ├── test_voice_assistant.py  # Comprehensive automated test suite
    ├── requirements.txt         # Required Python dependencies
    ├── .env.example             # Template for optional API & email credentials
    ├── README.md                # Full project documentation & instructions
    └── screenshots/             # Terminal session logs & interaction previews
        ├── 01_startup_banner.png
        ├── 02_weather_query.png
        ├── 03_reminder_alert.png
        └── session_sample.log
```

---

## 8. Installation & Setup

### 8.1 Required Python Version
* Python **3.8** or higher (tested on **Python 3.14**).

### 8.2 Dependency Installation
Open your terminal in the `Python-Task1-VoiceAssistant` folder and run:
```bash
pip install -r requirements.txt
```

---

## 9. Microphone Setup & Troubleshooting
* **Windows:** Ensure Microphone permissions are enabled under `Settings -> Privacy & Security -> Microphone -> Allow apps to access your microphone`.
* **Microphone Backends:** The application includes dual-backend microphone capture:
  1. `pyaudio` (standard backend)
  2. `sounddevice` (automatic fallback driver if PyAudio is not available)
* **Text Fallback Mode:** If a microphone is not connected or in a quiet environment, run with the `--text` or `-t` flag:
  ```bash
  python main.py --text
  ```

---

## 10. Weather API Setup (Optional)
The assistant works out-of-the-box using the live `wttr.in` fallback service. To use the official OpenWeatherMap API:
1. Register for a free API key at [OpenWeatherMap](https://openweathermap.org/api).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Add your key:
   ```env
   WEATHER_API_KEY=your_openweathermap_api_key_here
   ```

---

## 11. Email Configuration (Optional)
To enable voice-guided email sending with Gmail:
1. Enable 2-Step Verification on your Google Account.
2. Generate an **App Password** (`Google Account -> Security -> App passwords`).
3. Add your credentials in `.env`:
   ```env
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_16_char_app_password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=465
   ```
> **Security Notice:** Never commit your `.env` file containing real credentials to GitHub.

---

## 12. Environment Variables Reference

| Variable Name | Required? | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `WEATHER_API_KEY` | Optional | `""` (wttr.in used) | OpenWeatherMap API token |
| `EMAIL_ADDRESS` | Optional | `""` | Sender email address |
| `EMAIL_PASSWORD` | Optional | `""` | Sender application password |
| `SMTP_SERVER` | Optional | `smtp.gmail.com` | SMTP host server |
| `SMTP_PORT` | Optional | `465` | SMTP SSL Port |
| `TTS_RATE` | Optional | `175` | Speech speed (words per minute) |
| `TTS_VOLUME` | Optional | `1.0` | Speech volume (0.0 to 1.0) |

---

## 13. How to Run

### Standard Voice Mode
```bash
python main.py
```

### Typed / Text Mode (Interactive Terminal)
```bash
python main.py --text
```

### Run Automated Test Suite
```bash
python test_voice_assistant.py
```

---

## 14. Example Voice & Text Commands

| Category | Example Commands | Assistant Action |
| :--- | :--- | :--- |
| **Greeting** | *"Hello"*, *"Good morning"*, *"Hi"* | Dynamic time-based greeting |
| **Time** | *"What time is it?"*, *"Tell me the current time"* | Speaks 12-hour formatted time |
| **Date** | *"What is today's date?"*, *"Tell me the date"* | Speaks day, month, and year |
| **Search** | *"Search for Python documentation"*, *"Google AI news"* | Opens Google search in browser |
| **Websites** | *"Open YouTube"*, *"Open GitHub"*, *"Open Wikipedia"* | Launches website URL |
| **Weather** | *"What is the weather in Tokyo?"*, *"Paris temperature"* | Fetches temperature, weather condition & humidity |
| **Reminders** | *"Set a reminder for 10 seconds to drink water"* | Schedules non-blocking background timer |
| **Email** | *"Send an email"*, *"Compose email"* | Interactive guided email sender |
| **Knowledge** | *"What is Python?"*, *"What is machine learning?"* | Reads definitions from local knowledge base |
| **Fun** | *"Tell me a joke"*, *"Tell me a fact"* | Delivers programming trivia/humor |
| **Utilities** | *"Open calculator"*, *"Open notepad"* | Launches desktop applications |
| **Help** | *"Help"*, *"What can you do?"*, *"Commands"* | Lists assistant command menu |
| **Exit** | *"Exit"*, *"Quit"*, *"Goodbye"*, *"Stop"* | Polite farewell & clean shutdown |

---

## 15. Error Handling & Robustness
* **Speech Recognition Timeouts:** Handled without crashes; prompts the user gently or waits for the next cycle.
* **Unintelligible Audio:** Plays `"Sorry, I didn't quite catch that. Could you please repeat?"` rather than throwing exceptions.
* **Network & API Drops:** Graceful messaging and offline knowledge base fallback.
* **Missing Credentials:** Informs user of missing configuration rather than failing silently or crashing.
* **Thread Safety:** Thread-safe locking prevents audio collision between background reminders and foreground answers.

---

## 16. Privacy & Security Notes
1. **Zero Hardcoded Secrets:** No API keys, passwords, or tokens exist in source files.
2. **Safe Development:** Credentials must only reside in a localized `.env` file (ignored by version control).
3. **Explicit Confirmation:** Sensitive operations like sending an email require mandatory two-step confirmation from the user.

---

## 17. Screenshots & Terminal Demonstration

### Terminal Startup & Greeting
```text
================================================================
              OASIS INFOBYTE SIP — TASK 1
               ADVANCED VOICE ASSISTANT
================================================================
  Assistant Name : Oasis Assistant
  Platform       : Windows 11
  Python Version : 3.14.6
  Weather API    : Live wttr.in Fallback
  Email Config   : Optional (Not Set)
================================================================
  Type 'help' or say 'help' at any time for sample commands.
  Type 'exit' or say 'exit' / 'quit' to terminate.
================================================================

[ASSISTANT] Good afternoon! Hello, I am Oasis Assistant. How can I assist you today?
```

### Live Command Execution
```text
[YOU] What time is it?
[ASSISTANT] The current time is 03:41 PM.

[YOU] What is the weather in Paris?
[WEATHER] Fetching live weather data for 'Paris'...
[ASSISTANT] The current weather in Paris is Partly Cloudy with a temperature of 21 degrees Celsius (feels like 20 degrees) and 50 percent humidity.

[YOU] Set a reminder for 10 seconds to drink water
[ASSISTANT] Got it. I have set a reminder for 10 second(s). I will notify you when it finishes.
...
[REMINDER ALERT] Time's up! Reminder: Don't forget to drink water
[ASSISTANT] Reminder alert: Your timer for 10 seconds is complete. Don't forget to drink water
```

---

## 18. Future Improvements
* Integration with offline speech-to-text models like OpenAI Whisper or Vosk for full offline voice recognition.
* Support for smart home IoT integration (e.g., Home Assistant or Philips Hue).
* Multi-language support and customized wake-word detection (e.g., *"Hey Oasis"*).
* Calendar synchronization (Google Calendar / Outlook API).

---

## 19. OASIS SIP Requirement Checklist
- [x] Voice input via microphone
- [x] Contextual Greeting
- [x] Current Time inquiry
- [x] Current Date inquiry
- [x] Google Web search integration
- [x] Offline Text-to-Speech (pyttsx3)
- [x] Graceful speech recognition error handling
- [x] Natural language intent variations
- [x] Non-blocking background reminder/timer
- [x] Live Weather forecast with fallback
- [x] Voice-guided email workflow with confirmation
- [x] Custom desktop application launcher
- [x] Comprehensive README documentation
- [x] Minimal clean `requirements.txt`
- [x] Security and privacy compliance
- [x] 100% Automated and manual testing verified
