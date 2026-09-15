"""
================================================================================
OASIS INFOBYTE SIP — PYTHON PROGRAMMING INTERNSHIP
Task 1: Voice Assistant (Advanced Tier)
================================================================================
Author: Oasis Infobyte Intern
Description: A voice assistant built in Python that listens to voice
             commands, processes natural language intents, executes real-world
             actions, and responds via text-to-speech.

Features:
- Live Speech Recognition (Microphone & SoundDevice multi-backend + Text fallback)
- Offline Text-to-Speech (pyttsx3)
- System Time & Date with natural variations
- Web Searching & Direct Website Launching
- Live Weather Forecast (OpenWeatherMap API & wttr.in fallback)
- Non-blocking Background Reminder / Timer System
- Voice-Guided Email Sender with confirmation safeguards (smtplib)
- Local Knowledge Base & System Utilities Launcher
- Robust error handling for offline/timeout/microphone exceptions
================================================================================
"""

import os
import sys
import time
import json
import re
import ssl
import smtplib
import platform
import subprocess
import threading
import webbrowser
from datetime import datetime
from email.message import EmailMessage
from typing import Optional, Tuple, Dict, Any

# Third-party imports
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import requests
except ImportError:
    requests = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sd = None
    np = None


# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
ASSISTANT_NAME = "Oasis Assistant"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "").strip()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "465").strip() or 465)
TTS_RATE = int(os.getenv("TTS_RATE", "175").strip() or 175)
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0").strip() or 1.0)

# Thread lock for TTS engine to prevent concurrent access issues
tts_lock = threading.Lock()

# Knowledge Base Dictionary
KNOWLEDGE_BASE = {
    "what is python": (
        "Python is a high-level, versatile programming language created by Guido van Rossum. "
        "It is famous for its clean syntax and is widely used in AI, data science, web development, and automation."
    ),
    "what is ai": (
        "Artificial Intelligence, or AI, refers to computer systems engineered to simulate human intelligence. "
        "It encompasses capabilities like learning, problem solving, decision making, and natural language understanding."
    ),
    "what is artificial intelligence": (
        "Artificial Intelligence is the branch of computer science focused on creating machines capable of "
        "performing tasks that typically require human cognition, such as visual perception and speech recognition."
    ),
    "what is machine learning": (
        "Machine Learning is a subset of AI that allows software systems to automatically learn and improve "
        "from data without being explicitly programmed."
    ),
    "who are you": (
        f"I am {ASSISTANT_NAME}, an intelligent Python voice assistant developed for the Oasis Infobyte SIP program."
    ),
    "what can you do": (
        "I can tell the time and date, check live weather forecasts, search the web, open websites, "
        "launch desktop apps like notepad and calculator, set non-blocking timers, send emails, and answer general questions."
    ),
    "who created you": (
        "I was created as part of the Oasis Infobyte Internship Task 1 Voice Assistant project."
    ),
    "tell me a joke": (
        "Why do programmers prefer dark mode? Because light attracts bugs!"
    ),
    "tell me a fact": (
        "Did you know? Python was not named after the snake, but after the British comedy television show Monty Python's Flying Circus!"
    ),
}

# Supported Websites Mapping
POPULAR_WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "wikipedia": "https://www.wikipedia.org",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "gmail": "https://mail.google.com",
    "oasis infobyte": "https://oasisinfobyte.com",
    "oasis": "https://oasisinfobyte.com",
}


# ==============================================================================
# TEXT-TO-SPEECH (TTS) MODULE
# ==============================================================================
class TextToSpeechEngine:
    """Thread-safe Text-to-Speech wrapper using pyttsx3."""

    def __init__(self, rate: int = TTS_RATE, volume: float = TTS_VOLUME):
        self.rate = rate
        self.volume = volume
        self.available = False
        self.engine = None
        self._initialize_engine()

    def _initialize_engine(self):
        if pyttsx3 is None:
            self.available = False
            return

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)
            self.available = True
        except Exception as err:
            print(f"[ERROR] Could not initialize pyttsx3 TTS engine: {err}")
            self.available = False

    def speak(self, text: str, print_text: bool = True):
        """Speak the given text out loud and optionally print to console."""
        if print_text:
            print(f"\n[ASSISTANT] {text}", flush=True)

        if not text or not text.strip():
            return

        with tts_lock:
            if not self.available or self.engine is None:
                return

            try:
                # Re-initialize if previous run finished or engine in busy state
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as err:
                try:
                    # Attempt a fresh engine instance if COM/driver failed
                    self.engine = pyttsx3.init()
                    self.engine.setProperty("rate", self.rate)
                    self.engine.setProperty("volume", self.volume)
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception:
                    pass


# Global TTS instance
tts = TextToSpeechEngine()


def speak(text: str, print_text: bool = True):
    """Global helper function to speak text."""
    tts.speak(text, print_text=print_text)


# ==============================================================================
# SPEECH RECOGNITION (STT) MODULE
# ==============================================================================
class SpeechListener:
    """Robust multi-backend Speech-to-Text Listener with fallback mechanisms."""

    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None
        if self.recognizer:
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
        self.has_pyaudio = False
        if sr:
            try:
                import pyaudio
                self.has_pyaudio = True
            except (ImportError, Exception):
                self.has_pyaudio = False

    def _listen_sounddevice(self, duration: int = 5, sample_rate: int = 16000) -> Optional[str]:
        """Microphone recorder using sounddevice and SpeechRecognition AudioData."""
        if sd is None or np is None or self.recognizer is None:
            return None

        try:
            print("\n[LISTENING] Listening for command (speak clearly into your microphone)...", flush=True)
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="int16",
            )
            sd.wait()
            raw_pcm = recording.tobytes()
            audio_data = sr.AudioData(raw_pcm, sample_rate, 2)
            print("[PROCESSING] Recognizing speech...", flush=True)
            recognized = self.recognizer.recognize_google(audio_data)
            print(f"[YOU] {recognized}", flush=True)
            return recognized.strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as req_err:
            print(f"[ERROR] Could not connect to Google Speech Recognition service: {req_err}", flush=True)
            speak("I am having trouble connecting to the speech service. Please check your internet connection.")
            return None
        except Exception:
            return None

    def listen(self, timeout: int = 5, phrase_time_limit: int = 6) -> Optional[str]:
        """
        Listen for voice input from the user.
        Returns recognized string or None if nothing was heard or an error occurred.
        """
        if self.recognizer is None:
            print("[ERROR] SpeechRecognition library is not installed.", flush=True)
            return None

        # Strategy 1: PyAudio backend if available
        if self.has_pyaudio:
            try:
                with sr.Microphone() as source:
                    print("\n[LISTENING] Listening for command (speak clearly into your microphone)...", flush=True)
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit,
                    )
                    print("[PROCESSING] Recognizing speech...", flush=True)
                    text = self.recognizer.recognize_google(audio)
                    print(f"[YOU] {text}", flush=True)
                    return text.strip()

            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print("[INFO] Speech was unintelligible.", flush=True)
                speak("Sorry, I didn't quite catch that. Could you please repeat?")
                return None
            except sr.RequestError as req_err:
                print(f"[ERROR] Could not request results from Google Speech Recognition service: {req_err}", flush=True)
                speak("I am having trouble connecting to the speech recognition service. Please check your internet connection.")
                return None
            except Exception:
                pass

        # Strategy 2: SoundDevice backend
        if sd is not None and np is not None:
            return self._listen_sounddevice(duration=5)

        return None

    def prompt_or_listen(self, prompt_text: str, force_text_mode: bool = False) -> Optional[str]:
        """Ask the user a question via voice/text and retrieve their answer."""
        speak(prompt_text)
        if force_text_mode:
            try:
                user_input = input(f"[INPUT] {prompt_text}\n> ").strip()
                return user_input if user_input else None
            except (EOFError, KeyboardInterrupt):
                return None

        # Try voice input first
        result = self.listen(timeout=6, phrase_time_limit=8)
        if not result:
            # Fallback to text prompt if voice failed or timed out
            try:
                print(f"\n[FALLBACK INPUT] Type your response (or press Enter to skip):")
                user_input = input("> ").strip()
                return user_input if user_input else None
            except (EOFError, KeyboardInterrupt):
                return None
        return result


# Global listener instance
listener = SpeechListener()


# ==============================================================================
# FEATURE IMPLEMENTATIONS
# ==============================================================================

# ------------------------------------------------------------------------------
# Feature A & B: Greetings, Time, Date
# ------------------------------------------------------------------------------
def handle_greeting() -> str:
    """Return an appropriate dynamic greeting based on current time of day."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        period = "Good morning"
    elif 12 <= hour < 17:
        period = "Good afternoon"
    else:
        period = "Good evening"
    response = f"{period}! Hello, I am {ASSISTANT_NAME}. How can I assist you today?"
    speak(response)
    return response


def get_current_time() -> str:
    """Retrieve and speak the current system time."""
    now = datetime.now()
    formatted_time = now.strftime("%I:%M %p")
    response = f"The current time is {formatted_time}."
    speak(response)
    return response


def get_current_date() -> str:
    """Retrieve and speak the current system date."""
    now = datetime.now()
    formatted_date = now.strftime("%A, %B %d, %Y")
    response = f"Today is {formatted_date}."
    speak(response)
    return response


# ------------------------------------------------------------------------------
# Feature C: Web Search & Website Navigation
# ------------------------------------------------------------------------------
def search_web(query: str) -> str:
    """Search the web via Google in the default web browser."""
    clean_query = query.strip()
    if not clean_query:
        response = "What would you like me to search for?"
        speak(response)
        return response

    search_url = f"https://www.google.com/search?q={requests.utils.quote(clean_query) if requests else clean_query.replace(' ', '+')}"
    print(f"[SEARCH] Opening web search for: '{clean_query}'")
    webbrowser.open(search_url)
    response = f"Here are the web search results for {clean_query}."
    speak(response)
    return response


def open_website(site_name: str) -> str:
    """Open a known or custom website URL in the browser."""
    site_key = site_name.strip().lower()
    target_url = POPULAR_WEBSITES.get(site_key)

    if not target_url:
        if "." in site_key and not site_key.startswith("http"):
            target_url = f"https://{site_key}"
        else:
            target_url = f"https://www.{site_key}.com"

    print(f"[BROWSER] Navigating to: {target_url}")
    try:
        webbrowser.open(target_url)
        response = f"Opening {site_name} in your web browser."
        speak(response)
        return response
    except Exception as err:
        response = f"Sorry, I could not open {site_name}. Error: {err}"
        speak(response)
        return response


# ------------------------------------------------------------------------------
# Feature D: Weather Forecasting (OpenWeatherMap + wttr.in fallback)
# ------------------------------------------------------------------------------
def get_weather(city: Optional[str] = None) -> str:
    """
    Retrieve live weather for the specified city.
    Uses OpenWeatherMap if WEATHER_API_KEY is configured, otherwise uses wttr.in.
    """
    if requests is None:
        response = "The requests library is required to retrieve weather forecasts."
        speak(response)
        return response

    # If city is not provided, prompt the user
    if not city or not city.strip():
        city_input = listener.prompt_or_listen("Which city would you like the weather for?")
        if not city_input:
            response = "I did not receive a city name for the weather query."
            speak(response)
            return response
        city = city_input

    city = city.strip().title()
    print(f"[WEATHER] Fetching live weather data for '{city}'...")

    # Strategy 1: OpenWeatherMap API (if API Key provided)
    if WEATHER_API_KEY:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={requests.utils.quote(city)}&appid={WEATHER_API_KEY}&units=metric"
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                condition = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                response = (
                    f"The current weather in {city} is {condition} with a temperature of "
                    f"{round(temp)} degrees Celsius (feels like {round(feels_like)} degrees) "
                    f"and {humidity} percent humidity."
                )
                speak(response)
                return response
            elif res.status_code == 404:
                response = f"Sorry, I could not find weather details for the city named {city}."
                speak(response)
                return response
            else:
                print(f"[WARNING] OpenWeatherMap API returned status {res.status_code}. Trying fallback...")
        except Exception as err:
            print(f"[WARNING] OpenWeatherMap request failed: {err}. Trying fallback...")

    # Strategy 2: wttr.in JSON Live Weather (Fallback with zero API key requirement)
    try:
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
        res = requests.get(url, timeout=8, headers={"User-Agent": "OasisVoiceAssistant/1.0"})
        if res.status_code == 200:
            data = res.json()
            current_cond = data["current_condition"][0]
            temp_c = current_cond["temp_C"]
            feels_c = current_cond["FeelsLikeC"]
            desc = current_cond["weatherDesc"][0]["value"]
            humidity = current_cond["humidity"]
            response = (
                f"The current weather in {city} is {desc} with a temperature of "
                f"{temp_c} degrees Celsius (feels like {feels_c} degrees) and {humidity} percent humidity."
            )
            speak(response)
            return response
        else:
            response = f"Could not retrieve weather for {city}. Please check the city name."
            speak(response)
            return response
    except requests.exceptions.RequestException:
        response = "Unable to connect to the weather service. Please check your internet connection."
        speak(response)
        return response
    except Exception as err:
        response = f"An unexpected error occurred while fetching weather: {err}"
        speak(response)
        return response


# ------------------------------------------------------------------------------
# Feature E: Non-Blocking Reminder / Timer System
# ------------------------------------------------------------------------------
class ReminderManager:
    """Manages background non-blocking reminders with audible completion alerts."""

    def __init__(self):
        self.active_timers = []

    def _timer_callback(self, seconds: int, reminder_text: str):
        """Executed in background thread when timer expires."""
        print(f"\n\n{'='*50}")
        print(f"[REMINDER ALERT] Time's up! Reminder: {reminder_text}")
        print(f"{'='*50}\n")
        alert_msg = f"Reminder alert: Your timer for {seconds} seconds is complete. {reminder_text}"
        speak(alert_msg)

    def parse_time_duration(self, text: str) -> Tuple[Optional[int], str]:
        """
        Extract duration in seconds and any reminder note from text.
        Supports phrases like: '10 seconds', '2 minutes', '1 hour', 'reminder for 5 mins to drink water'
        """
        lower = text.lower()

        # Extract note if user specified 'to [do something]'
        note_match = re.search(r"\bto\s+(.+)$", lower)
        reminder_note = f"Don't forget to {note_match.group(1).strip()}" if note_match else "Your timer has finished."

        # Regex for hour/minute/second patterns
        seconds = 0
        found = False

        hour_match = re.search(r"(\d+)\s*(?:hours?|hrs?|h)\b", lower)
        if hour_match:
            seconds += int(hour_match.group(1)) * 3600
            found = True

        min_match = re.search(r"(\d+)\s*(?:minutes?|mins?|m)\b", lower)
        if min_match:
            seconds += int(min_match.group(1)) * 60
            found = True

        sec_match = re.search(r"(\d+)\s*(?:seconds?|secs?|s)\b", lower)
        if sec_match:
            seconds += int(sec_match.group(1))
            found = True

        # Pure number fallback (e.g. 'set reminder for 10')
        if not found:
            num_match = re.search(r"\b(?:for|in)\s+(\d+)\b", lower)
            if num_match:
                seconds = int(num_match.group(1))
                found = True

        if found and seconds > 0:
            return seconds, reminder_note
        return None, reminder_note

    def set_reminder(self, command_text: str) -> str:
        """Create and schedule a non-blocking reminder."""
        seconds, note = self.parse_time_duration(command_text)

        if not seconds or seconds <= 0:
            # Prompt user for duration
            duration_input = listener.prompt_or_listen("How many seconds or minutes should I set the reminder for?")
            if not duration_input:
                response = "I could not determine the duration for the reminder."
                speak(response)
                return response
            seconds, note = self.parse_time_duration(duration_input)
            if not seconds or seconds <= 0:
                response = "Invalid reminder duration provided. Please specify in seconds or minutes."
                speak(response)
                return response

        # Format human-friendly time
        if seconds >= 60:
            time_str = f"{seconds // 60} minute(s)" + (f" and {seconds % 60} second(s)" if seconds % 60 else "")
        else:
            time_str = f"{seconds} second(s)"

        timer_thread = threading.Timer(seconds, self._timer_callback, args=[seconds, note])
        timer_thread.daemon = True
        timer_thread.start()
        self.active_timers.append(timer_thread)

        response = f"Got it. I have set a reminder for {time_str}. I will notify you when it finishes."
        speak(response)
        return response


# Global reminder manager instance
reminder_mgr = ReminderManager()


# ------------------------------------------------------------------------------
# Feature F: Voice-Guided Email Sender with Confirmation Safeguards
# ------------------------------------------------------------------------------
def send_email_flow() -> str:
    """
    Voice-guided email workflow with recipient, subject, message input,
    and mandatory confirmation before sending via smtplib.
    """
    # Verify environment credentials
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        response = (
            "Email credentials are not configured in your environment. "
            "Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your .env file to enable email sending."
        )
        print(f"[SECURITY / CONFIG] {response}")
        speak(response)
        return response

    print("\n--- VOICE-GUIDED EMAIL WORKFLOW ---")
    speak("Starting email composition. Who is the recipient email address?")

    # 1. Recipient
    recipient = input("[INPUT] Enter recipient email address (e.g., example@gmail.com):\n> ").strip()
    if not recipient or "@" not in recipient:
        response = "Invalid recipient email address. Email composition cancelled."
        speak(response)
        return response

    # 2. Subject
    subject = listener.prompt_or_listen("What is the subject of the email?")
    if not subject:
        subject = "Message from Oasis Voice Assistant"
    print(f"[INFO] Email Subject: {subject}")

    # 3. Message Body
    message_body = listener.prompt_or_listen("What is the content of the message you want to send?")
    if not message_body:
        response = "No message body provided. Email composition cancelled."
        speak(response)
        return response
    print(f"[INFO] Email Message: {message_body}")

    # 4. Mandatory Explicit Confirmation
    confirmation = listener.prompt_or_listen(
        f"Please confirm: Do you want me to send this email to {recipient} with subject '{subject}'? Say yes to send or no to cancel."
    )

    if not confirmation or not any(word in confirmation.lower() for word in ["yes", "send", "confirm", "sure", "ok", "okay"]):
        response = "Email sending has been cancelled upon your request."
        speak(response)
        return response

    # 5. Send via smtplib SSL
    print(f"[EMAIL] Sending email to {recipient} via {SMTP_SERVER}:{SMTP_PORT}...")
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(message_body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        response = f"The email was successfully sent to {recipient}."
        speak(response)
        return response

    except smtplib.SMTPAuthenticationError:
        response = "Authentication failed. Please check your EMAIL_ADDRESS and EMAIL_PASSWORD / App Password."
        print(f"[ERROR] {response}")
        speak(response)
        return response
    except Exception as err:
        response = f"Failed to send email due to an error: {err}"
        print(f"[ERROR] {response}")
        speak(response)
        return response


# ------------------------------------------------------------------------------
# Feature G: Desktop Applications & System Utilities Launcher
# ------------------------------------------------------------------------------
def open_system_app(app_name: str) -> str:
    """Launch local system applications cross-platform."""
    app_key = app_name.lower().strip()
    current_os = platform.system().lower()

    commands = {
        "windows": {
            "calculator": ["calc"],
            "notepad": ["notepad"],
            "paint": ["mspaint"],
            "task manager": ["taskmgr"],
            "terminal": ["cmd"],
            "command prompt": ["cmd"],
            "file explorer": ["explorer"],
        },
        "linux": {
            "calculator": ["gnome-calculator"],
            "notepad": ["gedit"],
            "terminal": ["x-terminal-emulator"],
            "file explorer": ["nautilus"],
        },
        "darwin": {
            "calculator": ["open", "-a", "Calculator"],
            "notepad": ["open", "-a", "TextEdit"],
            "terminal": ["open", "-a", "Terminal"],
        },
    }

    os_commands = commands.get(current_os, {})
    matched_cmd = None
    for key, cmd in os_commands.items():
        if key in app_key or app_key in key:
            matched_cmd = cmd
            break

    if matched_cmd:
        try:
            subprocess.Popen(matched_cmd, shell=False)
            response = f"Opening {app_name} on your computer."
            speak(response)
            return response
        except Exception as err:
            response = f"Could not launch {app_name}: {err}"
            speak(response)
            return response
    else:
        response = f"Sorry, I do not have a launch command configured for {app_name} on {platform.system()}."
        speak(response)
        return response


# ------------------------------------------------------------------------------
# Feature H: General Knowledge & FAQ
# ------------------------------------------------------------------------------
def get_knowledge_response(query: str) -> Optional[str]:
    """Check if the query matches local knowledge base questions."""
    clean = query.lower().strip()
    clean = re.sub(r"[^\w\s]", "", clean)

    for key, answer in KNOWLEDGE_BASE.items():
        key_clean = re.sub(r"[^\w\s]", "", key)
        if key_clean in clean or clean in key_clean:
            speak(answer)
            return answer

    return None


def show_help_menu() -> str:
    """Print and speak assistant capabilities."""
    help_text = (
        "Here are sample commands you can say:\n"
        "  • 'Hello' or 'Good morning' (Greeting)\n"
        "  • 'What time is it?' (Current Time)\n"
        "  • 'What is today\'s date?' (Current Date)\n"
        "  • 'Search for Python tutorials' (Web Search)\n"
        "  • 'Open YouTube' or 'Open GitHub' (Websites)\n"
        "  • 'What is the weather in Mumbai?' (Live Weather)\n"
        "  • 'Set a reminder for 10 seconds' (Timer)\n"
        "  • 'Send an email' (Voice Email)\n"
        "  • 'Open calculator' or 'Open notepad' (System Utilities)\n"
        "  • 'What is AI?' or 'Tell me a joke' (Knowledge Base)\n"
        "  • 'Exit' or 'Quit' (Terminate Assistant)"
    )
    print(f"\n{help_text}\n")
    speak("I have listed the available commands in your terminal. How can I help you?")
    return help_text


# ==============================================================================
# NATURAL LANGUAGE INTENT PARSER & DISPATCHER
# ==============================================================================
def handle_command(command: str) -> bool:
    """
    Process recognized user command using natural language intent detection.
    Returns False when exit command is recognized, True to continue listening.
    """
    if not command or not command.strip():
        return True

    text = command.strip().lower()
    print(f"\n[PROCESSING] Command: '{command}'")

    # 1. Exit / Quit Intent
    if any(re.search(pattern, text) for pattern in [
        r"\b(?:exit|quit|stop|terminate|goodbye|bye|shut down|close)\b",
        r"\bsee you later\b",
        r"\bhave a good day\b"
    ]):
        farewell = f"Goodbye! Have a wonderful day. Thank you for using {ASSISTANT_NAME}."
        speak(farewell)
        return False

    # 2. Greeting Intent
    if any(re.search(pattern, text) for pattern in [
        r"^(?:hello|hi|hey|greetings|howdy)\b",
        r"\bgood (?:morning|afternoon|evening|day)\b",
        r"\bhow are you\b"
    ]):
        handle_greeting()
        return True

    # 3. Help Intent
    if re.search(r"\b(?:help|commands?|what can you do|features)\b", text):
        show_help_menu()
        return True

    # 4. Time Intent
    if re.search(r"\b(?:time|what time|tell me the time|current time|what's the time)\b", text):
        get_current_time()
        return True

    # 5. Date Intent
    if re.search(r"\b(?:date|what is today's date|today's date|tell me the date|what day is it|which day)\b", text):
        get_current_date()
        return True

    # 6. Weather Intent
    if "weather" in text or "temperature" in text or "forecast" in text:
        # Check if city is part of the command (e.g. 'weather in London' or 'Tokyo weather')
        city_match = re.search(r"(?:weather|temperature|forecast)\s+(?:in|for|at|of)\s+([a-zA-Z\s]+)", text)
        if not city_match:
            city_match = re.search(r"([a-zA-Z\s]+)\s+(?:weather|temperature|forecast)", text)

        city = city_match.group(1).strip() if city_match else None
        # Exclude auxiliary query words from city match
        if city:
            city = re.sub(r"\b(what is the|tell me the|how is the|the|today|now)\b", "", city).strip()
        get_weather(city)
        return True

    # 7. Reminder / Timer Intent
    if re.search(r"\b(?:reminder|remind me|timer|set (?:a )?timer|alarm)\b", text):
        reminder_mgr.set_reminder(text)
        return True

    # 8. Email Intent
    if re.search(r"\b(?:email|send (?:an )?email|send mail|compose email)\b", text):
        send_email_flow()
        return True

    # 9. System Utility Launch Intent
    if any(app in text for app in ["calculator", "notepad", "paint", "task manager", "command prompt", "terminal", "file explorer"]):
        for app in ["calculator", "notepad", "paint", "task manager", "command prompt", "terminal", "file explorer"]:
            if app in text:
                open_system_app(app)
                return True

    # 10. Open Popular Website Intent
    for site in POPULAR_WEBSITES.keys():
        if f"open {site}" in text or f"launch {site}" in text or f"go to {site}" in text:
            open_website(site)
            return True

    # 11. Generic Website Launch Intent
    open_match = re.search(r"\b(?:open|launch|go to)\s+([a-zA-Z0-9\-\.]+(?:\.com|\.org|\.io|\.net|\.in|\.edu)?)\b", text)
    if open_match and not any(k in text for k in ["camera", "app", "file"]):
        site_candidate = open_match.group(1).strip()
        if site_candidate not in ["the", "a", "my", "website", "browser"]:
            open_website(site_candidate)
            return True

    # 12. Web Search Intent
    search_match = re.search(r"\b(?:search (?:for|web for)?|google|look up|find)\s+(.+)$", text)
    if search_match:
        query = search_match.group(1).strip()
        search_web(query)
        return True

    # 13. General Knowledge Base Intent
    knowledge_answer = get_knowledge_response(text)
    if knowledge_answer:
        return True

    # 14. Fallback / Unrecognized Command
    speak("Sorry, I didn't recognize that command. Say 'help' to see what I can do, or ask me to search the web for it.")
    return True


# ==============================================================================
# MAIN APPLICATION RUNNER
# ==============================================================================
def print_banner():
    """Print the clean, professional terminal banner."""
    print("=" * 64)
    print("              OASIS INFOBYTE SIP — TASK 1")
    print("               ADVANCED VOICE ASSISTANT")
    print("=" * 64)
    print(f"  Assistant Name : {ASSISTANT_NAME}")
    print(f"  Platform       : {platform.system()} {platform.release()}")
    print(f"  Python Version : {sys.version.split()[0]}")
    print(f"  Weather API    : {'Configured' if WEATHER_API_KEY else 'Live wttr.in Fallback'}")
    print(f"  Email Config   : {'Configured' if EMAIL_ADDRESS and EMAIL_PASSWORD else 'Optional (Not Set)'}")
    print("=" * 64)
    print("  Type 'help' or say 'help' at any time for sample commands.")
    print("  Type 'exit' or say 'exit' / 'quit' to terminate.")
    print("=" * 64)


def main():
    """Main execution loop for the Oasis Voice Assistant."""
    print_banner()

    # Parse command line flags
    text_mode_only = "--text" in sys.argv or "-t" in sys.argv

    # Initial Greeting
    handle_greeting()

    # Main interaction loop
    is_running = True
    while is_running:
        try:
            if text_mode_only:
                try:
                    user_cmd = input("\n[YOU (Typed)] > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[INFO] Keyboard interrupt detected. Exiting...")
                    break
            else:
                user_cmd = listener.listen(timeout=6, phrase_time_limit=8)

            if user_cmd:
                is_running = handle_command(user_cmd)
            else:
                # Short pause before next listen cycle
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n[INFO] Exiting on user request...")
            speak("Goodbye! Shutting down Oasis Assistant.")
            break
        except Exception as unhandled_err:
            print(f"[ERROR] An error occurred in main loop: {unhandled_err}")
            time.sleep(1)


if __name__ == "__main__":
    main()
