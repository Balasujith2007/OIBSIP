# 🔐 Secure Random Password Generator

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Internship](https://img.shields.io/badge/Oasis%20Infobyte-OIBSIP-orange.svg)](https://oasisinfobyte.com/)
[![Security](https://img.shields.io/badge/CSPRNG-Python%20secrets-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

> **Oasis Infobyte Internship Program (OIBSIP)**  
> **Domain:** Python Programming  
> **Task 3:** Advanced Random Password Generator  
> **Author:** Balasujith2007  

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Architecture & Design Principles](#-architecture--design-principles)
4. [Why `secrets` Instead of `random`?](#-why-secrets-instead-of-random)
5. [Password Generation Logic](#-password-generation-logic)
6. [Strength Analysis & Entropy Calculation](#-strength-analysis--entropy-calculation)
7. [Ambiguous Character Exclusion](#-ambiguous-character-exclusion)
8. [Session-Only Privacy & Security](#-session-only-privacy--security)
9. [Technologies Used](#-technologies-used)
10. [Installation & How to Run](#-installation--how-to-run)
11. [Project Structure](#-project-structure)
12. [Automated Testing Suite](#-automated-testing-suite)
13. [Future Enhancements](#-future-enhancements)

---

## 📖 Project Overview

The **Secure Random Password Generator** is a high-security, desktop application built with Python and modern Tkinter. Designed specifically for cybersecurity-conscious workflows, the tool generates cryptographically unpredictable, high-entropy passwords tailored to custom security policies, enterprise complexity requirements, and user preferences.

Unlike basic password scripts that use insecure linear pseudo-random number generators (PRNGs), this application strictly leverages Python's built-in **`secrets`** Cryptographically Secure Pseudo-Random Number Generator (**CSPRNG**) and implements a secure **Fisher-Yates shuffle** algorithm.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🛡️ CSPRNG Randomness** | Uses Python's `secrets` module backed by operating system entropy (`/dev/urandom` or Windows `BCryptGenRandom`). |
| **🎯 Guaranteed Category Inclusion** | Ensures at least one character is included from every selected character class. |
| **🔀 Secure Fisher-Yates Shuffling** | Shuffles characters in $O(N)$ time using `secrets.randbelow()` to eliminate positional bias. |
| **📏 Flexible Length Control** | Generates passwords from 8 up to 128 characters with live slider and quick presets (8, 12, 16, 20, 32, 64). |
| **🎛️ Granular Character Options** | Independent toggles for Uppercase (`A-Z`), Lowercase (`a-z`), Numbers (`0-9`), and Symbols (`!@#$...`). |
| **👁️ Ambiguous Character Exclusion** | Option to exclude visually confusable characters (`0/O/o`, `1/l/I`, `|`, `` ` ``, `'`, `"`, `;`, `:`). |
| **📊 Real-Time Strength Meter** | Heuristic evaluation considering length, variety, repeated sequences, and sequential patterns. |
| **📐 Shannon Entropy Estimator** | Displays theoretical pool entropy in bits ($H \approx L \cdot \log_2 R$). |
| **📋 1-Click Clipboard with Auto-Clear** | Seamless clipboard copying with instant visual feedback and optional 45-second memory clearing. |
| **🔒 Mask / Unmask Toggle** | Masked password display (`••••••••`) prevents shoulder-surfing in public environments. |
| **📜 Session Metadata History** | In-memory audit trail of generation parameters (time, length, categories, entropy) — **NEVER saves plaintext passwords**. |
| **💻 Dual GUI & CLI Modes** | Polished Slate-dark Tkinter GUI with automated CLI fallback and `--cli` flag support. |
| **📴 100% Offline & Private** | Zero network dependencies, zero persistent disk logging, zero telemetry. |

---

## 🔒 Why `secrets` Instead of `random`?

In Python, the standard `random` module uses the **Mersenne Twister (MT19937)** algorithm. 

### Why `random` is INSECURE for Passwords:
1. **Deterministic State:** Mersenne Twister is designed for scientific simulations and modeling, not cryptography.
2. **Reversible Internal State:** Observing just **624 outputs** of a 32-bit Mersenne Twister allows an adversary to reconstruct the entire 2.5 KB internal state and predict every past and future "random" output with 100% accuracy.
3. **Vulnerable to Seed Sniffing:** If seeded with system clock timestamps, an attacker can brute-force the seed in milliseconds.

### Why `secrets` is CRYPTOGRAPHICALLY SECURE:
- The `secrets` module (introduced in Python 3.6, PEP 506) accesses the operating system's cryptographic random engine:
  - Windows: `BCryptGenRandom()`
  - Linux: `getrandom(2)` syscall / `/dev/urandom`
  - macOS: `getentropy()`
- It utilizes hardware noise, CPU interrupt timing, and OS kernel entropy pools.
- **Unpredictable:** Even with extensive computational resources, past or future outputs cannot be inferred from observed samples.

```python
# INSECURE (Never used in this application)
import random
pwd = "".join(random.choice(pool) for _ in range(16))  # INSECURE!

# SECURE (Implemented across this project)
import secrets
pwd = "".join(secrets.choice(pool) for _ in range(16)) # CRYPTOGRAPHICALLY SECURE
```

---

## ⚙️ Password Generation Logic

The generation workflow guarantees mathematical uniformity and strict compliance with selected policies:

```
[User Input / Presets]
        │
        ▼
[Configuration Validation] ──(Invalid)──► [Display Warning Dialog]
        │ (Valid)
        ▼
[Build Filtered Pools] (Apply ambiguous exclusions)
        │
        ▼
[1. Guarantee Inclusion] ──► Select 1 character per chosen category via secrets.choice()
        │
        ▼
[2. Sample Remaining] ────► Sample (L - K) characters from combined pool via secrets.choice()
        │
        ▼
[3. Cryptographic Shuffle] ─► Fisher-Yates shuffle using secrets.randbelow()
        │
        ▼
[4. Strength & Entropy] ───► Compute Shannon bits & heuristic score
        │
        ▼
[5. Update Interface] ─────► Render masked output, meter bar, and session metadata
```

### Cryptographic Fisher-Yates Shuffle
```python
def secure_shuffle(items: List[str]) -> List[str]:
    shuffled = list(items)
    n = len(shuffled)
    for i in range(n - 1, 0, -1):
        j = secrets.randbelow(i + 1)  # CSPRNG bounded random integer
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled
```

---

## 📊 Strength Analysis & Entropy Calculation

### 1. Theoretical Entropy (Information Theory)
The theoretical entropy $H$ represents the number of bits of randomness in the password:

$$H \approx L \times \log_2(R)$$

- $L$: Length of the password
- $R$: Size of the active character pool (e.g., $26 + 26 + 10 + 28 = 90$)

| Length | Active Character Classes | Pool Size ($R$) | Entropy ($H$) | Resistance Level |
| :---: | :---: | :---: | :---: | :---: |
| 8 | Lowercase only | 26 | ~37.6 bits | Vulnerable |
| 12 | Upper + Lower + Digits | 62 | ~71.4 bits | Moderate |
| 16 | Upper + Lower + Digits + Symbols | 90 | ~103.9 bits | **Strong / Enterprise** |
| 32 | Upper + Lower + Digits + Symbols | 90 | ~207.7 bits | **Military / Quantum-Resistant** |

### 2. Heuristic Strength Meter
The analyzer tests for real-world attack surfaces:
- **Base length score** (up to 45 pts)
- **Character diversity** (+10 pts for each class present: Upper, Lower, Numbers, Symbols)
- **Unique character ratio bonus** (rewards entropy distribution)
- **Repeated adjacent character penalty** (e.g., `aaa`, `111`)
- **Sequential pattern penalty** (e.g., `abc`, `123`, `qwerty`)

> **Disclaimer:** Entropy and strength ratings are theoretical estimates. Real-world password security also depends on master password isolation, MFA, and target system hashing mechanisms (e.g. Argon2id, bcrypt).

---

## 🚫 Ambiguous Character Exclusion

When the **"Exclude Ambiguous Characters"** setting is enabled, glyphs that are visually confusing in monospaced or proportional fonts are stripped:

| Category | Excluded Characters | Reason |
| :--- | :--- | :--- |
| **Digits & Letters** | `0`, `O`, `o` | Zero vs capital letter O vs lowercase o |
| **Digits & Letters** | `1`, `l`, `I`, `\|` | Number one vs lowercase L vs uppercase i vs vertical pipe |
| **Punctuation** | `` ` ``, `'`, `"` | Backtick vs single quote vs double quote |
| **Separators** | `;`, `:`, `\` | Semicolon vs colon vs backslash |

---

## 🛡️ Session-Only Privacy & Security

This project adheres to strict Zero-Persistence principles:
- ❌ **No Hardcoded Credentials**
- ❌ **No Passwords in File Logs or JSON**
- ❌ **No Network / Cloud Calls**
- ❌ **No Plaintext Passwords in Session History** (Only timestamps, lengths, and entropy metrics are retained in RAM)
- 🧹 **Clipboard Auto-Clear:** Cleanses the OS clipboard after 45 seconds to protect against background snooping.

---

## 🛠️ Technologies Used

- **Language:** Python 3.8+
- **GUI Framework:** Tkinter & `ttk` with custom canvas rendering
- **Security Engine:** `secrets` (PEP 506 CSPRNG)
- **Math & Utilities:** `math`, `re`, `string`, `dataclasses`, `datetime`
- **Testing:** `unittest` + `ast` automated security linter

---

## 🚀 Installation & How to Run

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- Standard Tkinter support (included with standard Python installers for Windows/macOS; on Ubuntu/Debian: `sudo apt install python3-tk`).

### 2. Run Desktop GUI (Default Mode)
```bash
cd Python-Task3-RandomPasswordGenerator
python main.py
```

### 3. Run Interactive CLI Mode
```bash
python main.py --cli
```

---

## 📂 Project Structure

```
Python-Task3-RandomPasswordGenerator/
│
├── main.py                     # Main application (Engine, UI, CLI, & Analyzer)
├── test_password_generator.py  # Unit tests & cryptographic security assertions
├── test_gui.py                 # Tkinter GUI automated test suite
├── requirements.txt            # Zero-dependency specification
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git ignore rules
└── screenshots/                # UI showcase assets & documentation guide
    └── README.md
```

---

## 🧪 Automated Testing Suite

The project includes an automated test suite verifying all 18 evaluation criteria:

```bash
# Run Core Cryptographic & Security Unit Tests
python test_password_generator.py

# Run GUI Widget & Interaction Tests
python test_gui.py
```

### Test Coverage Highlights:
- ✅ **Test 1:** Length = 8 with guaranteed 4-category representation.
- ✅ **Test 2:** Pure lowercase pool generation.
- ✅ **Test 3:** Mixed case validation.
- ✅ **Test 4:** Numbers + symbols validation.
- ✅ **Test 5:** Ambiguous character complete exclusion across 25+ iterations.
- ✅ **Test 6-9:** Length boundary (min 8, max 128) and empty selection validation.
- ✅ **Test 10:** Multi-generation statistical independence.
- ✅ **Test 11:** Fisher-Yates shuffle preservation.
- ✅ **Test 12-13:** Entropy calculations and strength scoring boundaries.
- ✅ **Test 14-15:** Session history zero-plaintext storage assertions.
- ✅ **Test 16:** AST-based codebase security inspection (guaranteeing zero insecure `random` calls).
- ✅ **GUI Tests:** Visibility masking toggle, preset buttons, clipboard copy, clear state reset.

---

## 🔮 Future Enhancements

- [ ] Export generation audit reports in anonymized CSV format.
- [ ] Integration with local HaveIBeenPwned k-Anonymity SHA-1 hash lookup.
- [ ] Custom passphrase generation (EFF Diceware wordlists).
- [ ] Export encrypted password files using AES-256-GCM / PBKDF2.

---

## 👨‍💻 Author & Acknowledgements
- **Developer:** [@Balasujith2007](https://github.com/Balasujith2007)
- **Organization:** [Oasis Infobyte (OIBSIP)](https://oasisinfobyte.com/)
- **Repository:** [Balasujith2007/OIBSIP](https://github.com/Balasujith2007/OIBSIP)
