"""
================================================================================
OASIS INFOBYTE SIP — TASK 1: VOICE ASSISTANT (WEB INTERACTION SUITE)
================================================================================
A web-based interface for the Oasis Voice Assistant.
Combines real-time voice speech recognition, live text-to-speech audio,
interactive weather widgets, background reminders, and system command execution.
================================================================================
"""

import os
import sys
import json
import time
import re
import platform
import webbrowser
import threading
from datetime import datetime
from typing import Optional

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Import assistant engine
import main

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oasis Voice Assistant — Advanced Web Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.75);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-glow: rgba(6, 182, 212, 0.35);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background: radial-gradient(circle at 50% 10%, #1e1b4b 0%, var(--bg-primary) 60%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Top Header */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.25rem 2.5rem;
            background: rgba(11, 15, 25, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .brand-logo {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px var(--accent-glow);
        }

        .brand-logo svg {
            width: 24px;
            height: 24px;
            fill: white;
        }

        .brand-text h1 {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(90deg, #ffffff, #93c5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-text p {
            font-size: 0.75rem;
            color: var(--accent-cyan);
            font-weight: 500;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .status-pill {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0.9rem;
            border-radius: 9999px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            font-size: 0.8rem;
            color: var(--success);
            font-weight: 500;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 8px var(--success);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.2); }
        }

        /* Main Container */
        main {
            flex: 1;
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            padding: 2rem 1.5rem;
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 1.75rem;
        }

        @media (max-width: 900px) {
            main {
                grid-template-columns: 1fr;
            }
        }

        /* Voice Interaction Central Arena */
        .assistant-arena {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .visualizer-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(16px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }

        .visualizer-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 60%);
            pointer-events: none;
        }

        .orb-wrapper {
            position: relative;
            margin: 1.5rem 0;
        }

        .voice-orb {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            position: relative;
            z-index: 10;
            box-shadow: 0 0 35px var(--accent-glow);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 3px solid rgba(255, 255, 255, 0.2);
        }

        .voice-orb:hover {
            transform: scale(1.06);
            box-shadow: 0 0 50px rgba(6, 182, 212, 0.6);
        }

        .voice-orb.listening {
            animation: orb-pulse 1.5s infinite;
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
            box-shadow: 0 0 60px rgba(236, 72, 153, 0.7);
        }

        @keyframes orb-pulse {
            0% { transform: scale(1); box-shadow: 0 0 30px rgba(236, 72, 153, 0.5); }
            50% { transform: scale(1.12); box-shadow: 0 0 70px rgba(236, 72, 153, 0.9); }
            100% { transform: scale(1); box-shadow: 0 0 30px rgba(236, 72, 153, 0.5); }
        }

        .voice-orb svg {
            width: 52px;
            height: 52px;
            fill: white;
            transition: transform 0.2s;
        }

        /* Sound Wave Visualizer Bars */
        .waves-container {
            display: flex;
            align-items: center;
            gap: 6px;
            height: 32px;
            margin-top: 0.5rem;
        }

        .wave-bar {
            width: 4px;
            height: 8px;
            background: var(--accent-cyan);
            border-radius: 4px;
            transition: height 0.15s ease;
        }

        .listening .wave-bar {
            animation: sound-wave 1s ease-in-out infinite;
        }

        .listening .wave-bar:nth-child(1) { animation-delay: 0.1s; }
        .listening .wave-bar:nth-child(2) { animation-delay: 0.3s; }
        .listening .wave-bar:nth-child(3) { animation-delay: 0.5s; }
        .listening .wave-bar:nth-child(4) { animation-delay: 0.2s; }
        .listening .wave-bar:nth-child(5) { animation-delay: 0.4s; }
        .listening .wave-bar:nth-child(6) { animation-delay: 0.6s; }
        .listening .wave-bar:nth-child(7) { animation-delay: 0.15s; }

        @keyframes sound-wave {
            0%, 100% { height: 8px; }
            50% { height: 32px; background: #ec4899; }
        }

        .orb-status {
            margin-top: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-main);
        }

        .orb-substatus {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        /* Chat History Box */
        .chat-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            height: 380px;
            backdrop-filter: blur(16px);
        }

        .chat-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-color);
        }

        .chat-card-title {
            font-size: 0.95rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding-right: 0.5rem;
        }

        .chat-messages::-webkit-scrollbar {
            width: 5px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .message {
            display: flex;
            gap: 0.75rem;
            max-width: 85%;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.assistant {
            align-self: flex-start;
        }

        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .msg-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
            flex-shrink: 0;
        }

        .message.assistant .msg-avatar {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
            color: white;
        }

        .message.user .msg-avatar {
            background: #4b5563;
            color: white;
        }

        .msg-content {
            padding: 0.85rem 1.15rem;
            border-radius: 16px;
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .message.assistant .msg-content {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            border-top-left-radius: 4px;
        }

        .message.user .msg-content {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: white;
            border-top-right-radius: 4px;
        }

        /* Input Controls */
        .input-bar-wrapper {
            display: flex;
            gap: 0.65rem;
            position: relative;
        }

        .cmd-input {
            flex: 1;
            padding: 0.9rem 1.25rem;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            color: white;
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
        }

        .cmd-input:focus {
            border-color: var(--accent-cyan);
            box-shadow: 0 0 12px var(--accent-glow);
            background: rgba(255, 255, 255, 0.07);
        }

        .send-btn {
            padding: 0 1.4rem;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
            border: none;
            color: white;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.2s;
        }

        .send-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px var(--accent-glow);
        }

        /* Sidebar Panels */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .panel-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 1.25rem;
            backdrop-filter: blur(14px);
        }

        .panel-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.85rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* Quick Chips */
        .chips-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
        }

        .chip {
            padding: 0.45rem 0.75rem;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            color: #d1d5db;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }

        .chip:hover {
            background: rgba(6, 182, 212, 0.15);
            border-color: var(--accent-cyan);
            color: white;
            transform: translateY(-1px);
        }

        /* Weather Widget */
        .weather-widget {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1));
            border-radius: 14px;
            border: 1px solid rgba(6, 182, 212, 0.2);
        }

        .weather-city {
            font-size: 1.1rem;
            font-weight: 700;
        }

        .weather-desc {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .weather-temp {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--accent-cyan);
        }

        /* Live Terminal / Events Drawer */
        .terminal-box {
            font-family: 'JetBrains Mono', monospace;
            background: #050811;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 0.85rem;
            font-size: 0.75rem;
            color: #10b981;
            height: 140px;
            overflow-y: auto;
            line-height: 1.5;
        }

        .terminal-box::-webkit-scrollbar {
            width: 4px;
        }

        .terminal-box::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
        }

        .terminal-line {
            margin-bottom: 0.25rem;
            word-break: break-all;
        }

        .terminal-line.err { color: var(--danger); }
        .terminal-line.info { color: var(--accent-cyan); }
        .terminal-line.rem { color: var(--warning); }

        /* Notification Toast */
        .toast-container {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 100;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .toast {
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid var(--warning);
            border-left: 4px solid var(--warning);
            padding: 1rem 1.25rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            color: white;
            font-size: 0.9rem;
            backdrop-filter: blur(12px);
            animation: slideIn 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo">
                <svg viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
            </div>
            <div class="brand-text">
                <h1>OASIS VOICE ASSISTANT</h1>
                <p>Task 1: Advanced Tier • Oasis Infobyte SIP</p>
            </div>
        </div>
        <div class="status-pill">
            <div class="status-dot"></div>
            <span>System Active & Online</span>
        </div>
    </header>

    <main>
        <!-- Center Arena -->
        <section class="assistant-arena">
            
            <!-- Voice Visualizer Card -->
            <div class="visualizer-card">
                <div class="orb-wrapper">
                    <div class="voice-orb" id="voiceOrb" onclick="toggleVoiceListening()" title="Click to Speak">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                        </svg>
                    </div>
                </div>

                <div class="waves-container" id="wavesContainer">
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                </div>

                <div class="orb-status" id="orbStatus">Click Microphone or Speak</div>
                <div class="orb-substatus" id="orbSubstatus">Listening enabled via browser Web Speech and backend Python engine</div>
            </div>

            <!-- Chat & Interaction Stream -->
            <div class="chat-card">
                <div class="chat-card-header">
                    <div class="chat-card-title">
                        <span>💬 Live Conversation Stream</span>
                    </div>
                    <button class="chip" onclick="clearChat()" style="cursor:pointer">Clear</button>
                </div>

                <div class="chat-messages" id="chatMessages">
                    <div class="message assistant">
                        <div class="msg-avatar">AI</div>
                        <div class="msg-content">
                            Hello! I am Oasis Voice Assistant. How can I assist you today? You can speak or type your command below.
                        </div>
                    </div>
                </div>

                <!-- Input Field -->
                <div class="input-bar-wrapper">
                    <input type="text" id="cmdInput" class="cmd-input" placeholder="Type a command (e.g. 'What is the weather in London?')" onkeydown="handleKeyPress(event)">
                    <button class="send-btn" onclick="sendTypedCommand()">
                        <span>Send</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </section>

        <!-- Sidebar -->
        <aside class="sidebar">
            
            <!-- Quick Commands -->
            <div class="panel-card">
                <div class="panel-title">Quick Voice Commands</div>
                <div class="chips-grid">
                    <div class="chip" onclick="triggerCommand('what time is it')">🕒 Time</div>
                    <div class="chip" onclick="triggerCommand('what is today\'s date')">📅 Date</div>
                    <div class="chip" onclick="triggerCommand('weather in London')">🌤️ London Weather</div>
                    <div class="chip" onclick="triggerCommand('weather in Tokyo')">🗼 Tokyo Weather</div>
                    <div class="chip" onclick="triggerCommand('set a reminder for 5 seconds to drink water')">⏰ 5s Reminder</div>
                    <div class="chip" onclick="triggerCommand('tell me a joke')">😄 Joke</div>
                    <div class="chip" onclick="triggerCommand('what is machine learning')">🤖 What is ML?</div>
                    <div class="chip" onclick="triggerCommand('what is python')">🐍 Python</div>
                    <div class="chip" onclick="triggerCommand('search for artificial intelligence')">🔍 Search AI</div>
                    <div class="chip" onclick="triggerCommand('open youtube')">▶️ YouTube</div>
                    <div class="chip" onclick="triggerCommand('open github')">🐙 GitHub</div>
                    <div class="chip" onclick="triggerCommand('open calculator')">🧮 Calculator</div>
                    <div class="chip" onclick="triggerCommand('open notepad')">📝 Notepad</div>
                </div>
            </div>

            <!-- Live Weather Preview -->
            <div class="panel-card">
                <div class="panel-title">Live Weather Hub</div>
                <div class="weather-widget">
                    <div>
                        <div class="weather-city" id="wCity">London</div>
                        <div class="weather-desc" id="wDesc">Live Weather Data</div>
                    </div>
                    <div class="weather-temp" id="wTemp">18°C</div>
                </div>
            </div>

            <!-- System Activity Terminal -->
            <div class="panel-card">
                <div class="panel-title">Backend Activity Log</div>
                <div class="terminal-box" id="terminalLog">
                    <div class="terminal-line info">[SYSTEM] Oasis Voice Assistant Engine initialized.</div>
                    <div class="terminal-line info">[STATUS] Speech-to-Text & Text-to-Speech active.</div>
                    <div class="terminal-line info">[WEATHER] OpenWeatherMap & wttr.in ready.</div>
                </div>
            </div>

        </aside>
    </main>

    <!-- Toast Container -->
    <div class="toast-container" id="toastContainer"></div>

    <script>
        const orb = document.getElementById('voiceOrb');
        const orbStatus = document.getElementById('orbStatus');
        const orbSubstatus = document.getElementById('orbSubstatus');
        const waves = document.getElementById('wavesContainer');
        const chatMessages = document.getElementById('chatMessages');
        const cmdInput = document.getElementById('cmdInput');
        const terminalLog = document.getElementById('terminalLog');
        const toastContainer = document.getElementById('toastContainer');

        let isListening = false;
        let recognition = null;

        // Initialize Web Speech API for Browser Voice Input
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                isListening = true;
                orb.classList.add('listening');
                waves.classList.add('listening');
                orbStatus.innerText = "Listening...";
                orbSubstatus.innerText = "Speak your command clearly into your microphone";
                logTerminal("[VOICE] Microphone listening started...", "info");
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                logTerminal(`[VOICE RECOGNIZED] "${transcript}"`, "info");
                triggerCommand(transcript);
            };

            recognition.onerror = (event) => {
                logTerminal(`[VOICE ERROR] ${event.error}`, "err");
                stopListeningState();
            };

            recognition.onend = () => {
                stopListeningState();
            };
        } else {
            logTerminal("[WARNING] Web Speech API not natively supported in this browser. Using typed input fallback.", "err");
        }

        function toggleVoiceListening() {
            if (!recognition) {
                alert("Voice recognition is not supported in this browser. Please use the input box to type commands.");
                return;
            }

            if (isListening) {
                recognition.stop();
                stopListeningState();
            } else {
                try {
                    recognition.start();
                } catch (e) {
                    console.error(e);
                }
            }
        }

        function stopListeningState() {
            isListening = false;
            orb.classList.remove('listening');
            waves.classList.remove('listening');
            orbStatus.innerText = "Click Microphone or Speak";
            orbSubstatus.innerText = "Listening ready via browser or terminal";
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendTypedCommand();
            }
        }

        function sendTypedCommand() {
            const text = cmdInput.value.trim();
            if (!text) return;
            cmdInput.value = '';
            triggerCommand(text);
        }

        function appendMessage(role, text) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${role}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'msg-avatar';
            avatar.innerText = role === 'assistant' ? 'AI' : 'YOU';
            
            const content = document.createElement('div');
            content.className = 'msg-content';
            content.innerText = text;

            msgDiv.appendChild(avatar);
            msgDiv.appendChild(content);
            chatMessages.appendChild(msgDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function logTerminal(msg, type = "normal") {
            const line = document.createElement('div');
            line.className = `terminal-line ${type}`;
            const timeStr = new Date().toLocaleTimeString();
            line.innerText = `[${timeStr}] ${msg}`;
            terminalLog.appendChild(line);
            terminalLog.scrollTop = terminalLog.scrollHeight;
        }

        function showToast(title, message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `
                <div>
                    <strong>⏰ ${title}</strong>
                    <div style="font-size:0.8rem; opacity:0.85; margin-top:2px;">${message}</div>
                </div>
            `;
            toastContainer.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 6000);
        }

        // Speak response out loud using SpeechSynthesis
        function speakBrowser(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }

        async function triggerCommand(commandText) {
            appendMessage('user', commandText);
            logTerminal(`[COMMAND] Executing: "${commandText}"`, "info");

            try {
                const response = await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: commandText })
                });

                const data = await response.json();
                
                appendMessage('assistant', data.response);
                speakBrowser(data.response);
                logTerminal(`[RESPONSE] ${data.response}`);

                // Update weather widget if weather data returned
                if (data.weather) {
                    document.getElementById('wCity').innerText = data.weather.city;
                    document.getElementById('wTemp').innerText = `${data.weather.temp}°C`;
                    document.getElementById('wDesc').innerText = data.weather.condition;
                }

                // Handle timer notifications
                if (data.reminder) {
                    showToast('Reminder Scheduled', `Set for ${data.reminder.seconds} seconds.`);
                    setTimeout(() => {
                        showToast('Reminder Complete!', data.reminder.note);
                        speakBrowser(`Reminder alert: ${data.reminder.note}`);
                        logTerminal(`[REMINDER ALERT] ${data.reminder.note}`, "rem");
                    }, data.reminder.seconds * 1000);
                }

            } catch (err) {
                logTerminal(`[ERROR] Network or server failure: ${err}`, "err");
                appendMessage('assistant', "I encountered an error connecting to the backend server.");
            }
        }

        function clearChat() {
            chatMessages.innerHTML = '';
            appendMessage('assistant', "Conversation cleared. How can I help you?");
        }
    </script>
</body>
</html>
"""

# ==============================================================================
# API ROUTING & BACKEND LOGIC
# ==============================================================================
async def index_page(request):
    """Serve the single-page voice assistant Web Dashboard."""
    return HTMLResponse(HTML_CONTENT)


async def api_command(request):
    """Process voice or typed command via the Python assistant engine."""
    try:
        data = await request.json()
        command = data.get("command", "").strip()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    if not command:
        return JSONResponse({"response": "Please provide a command."})

    text = command.lower()
    response_text = ""
    weather_info = None
    reminder_info = None

    # 1. Exit Intent
    if any(re.search(pattern, text) for pattern in [r"\b(?:exit|quit|stop|goodbye|bye)\b"]):
        response_text = f"Goodbye! Thank you for using {main.ASSISTANT_NAME}."

    # 2. Greeting Intent
    elif any(re.search(pattern, text) for pattern in [r"^(?:hello|hi|hey|greetings)\b", r"\bgood (?:morning|afternoon|evening)\b"]):
        response_text = main.handle_greeting()

    # 3. Time Intent
    elif re.search(r"\b(?:time|what time|tell me the time|current time)\b", text):
        response_text = main.get_current_time()

    # 4. Date Intent
    elif re.search(r"\b(?:date|what is today's date|today's date|tell me the date)\b", text):
        response_text = main.get_current_date()

    # 5. Weather Intent
    elif "weather" in text or "temperature" in text:
        city_match = re.search(r"(?:weather|temperature|forecast)\s+(?:in|for|at|of)\s+([a-zA-Z\s]+)", text)
        if not city_match:
            city_match = re.search(r"([a-zA-Z\s]+)\s+(?:weather|temperature)", text)
        city = city_match.group(1).strip() if city_match else "London"
        city = re.sub(r"\b(what is the|tell me the|how is the|the|today|now)\b", "", city).strip() or "London"
        
        response_text = main.get_weather(city)
        # Parse approximate temp from response for UI widget
        temp_match = re.search(r"(\d+)\s*degrees Celsius", response_text)
        temp_val = temp_match.group(1) if temp_match else "20"
        weather_info = {
            "city": city.title(),
            "temp": temp_val,
            "condition": "Live Forecast"
        }

    # 6. Reminder Intent
    elif re.search(r"\b(?:reminder|remind me|timer|set (?:a )?timer)\b", text):
        seconds, note = main.reminder_mgr.parse_time_duration(text)
        if not seconds or seconds <= 0:
            seconds = 5
            note = "Your timer is complete."
        response_text = f"Got it. I have set a reminder for {seconds} seconds. I will alert you when it completes."
        reminder_info = {
            "seconds": seconds,
            "note": note
        }

    # 7. System Apps Launcher Intent
    elif any(app in text for app in ["calculator", "notepad", "paint", "task manager", "command prompt", "terminal"]):
        for app in ["calculator", "notepad", "paint", "task manager", "command prompt", "terminal"]:
            if app in text:
                response_text = main.open_system_app(app)
                break

    # 8. Web Search Intent
    elif re.search(r"\b(?:search (?:for|web for)?|google|look up|find)\s+(.+)$", text):
        search_match = re.search(r"\b(?:search (?:for|web for)?|google|look up|find)\s+(.+)$", text)
        query = search_match.group(1).strip()
        response_text = main.search_web(query)

    # 9. Open Website Intent
    elif any(f"open {site}" in text for site in main.POPULAR_WEBSITES.keys()):
        for site in main.POPULAR_WEBSITES.keys():
            if f"open {site}" in text:
                response_text = main.open_website(site)
                break

    # 10. General Knowledge Base Intent
    elif main.get_knowledge_response(text):
        response_text = main.get_knowledge_response(text)

    # 11. Fallback / Unrecognized
    else:
        response_text = "Sorry, I didn't quite catch that command. Say 'help' or try one of the quick command chips!"

    return JSONResponse({
        "response": response_text,
        "weather": weather_info,
        "reminder": reminder_info
    })


async def api_status(request):
    """Return backend status metadata."""
    return JSONResponse({
        "assistant_name": main.ASSISTANT_NAME,
        "platform": platform.system(),
        "python_version": sys.version.split()[0],
        "weather_configured": bool(main.WEATHER_API_KEY),
        "status": "Online"
    })


routes = [
    Route("/", endpoint=index_page, methods=["GET"]),
    Route("/api/command", endpoint=api_command, methods=["POST"]),
    Route("/api/status", endpoint=api_status, methods=["GET"]),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == "__main__":
    port = 8000
    print(f"\n================================================================")
    print(f"      OASIS VOICE ASSISTANT — WEB DASHBOARD SERVER")
    print(f"================================================================")
    print(f"  Web UI URL : http://localhost:{port}")
    print(f"  API Docs   : http://localhost:{port}/api/status")
    print(f"================================================================\n")
    webbrowser.open(f"http://localhost:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
