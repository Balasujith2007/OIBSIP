#!/usr/bin/env python3
"""
===============================================================================
OIBSIP — Python Programming Internship
Task 3: Advanced Random Password Generator
===============================================================================
Description:
    A professional, cryptographically secure desktop Random Password Generator
    built with Python and Tkinter. Generates unpredictable, high-entropy
    passwords using Python's `secrets` CSPRNG module.

Key Features:
    - Cryptographically secure generation via `secrets` module
    - Guaranteed representation of every selected character category
    - Cryptographic Fisher-Yates shuffling (`secrets.randbelow`)
    - Configurable length (8 - 128 characters)
    - Independent character set toggles (Uppercase, Lowercase, Numbers, Symbols)
    - Ambiguous character exclusion option (e.g., 0/O, 1/l/I)
    - Password strength analysis with factor breakdown & visual meter
    - Theoretical entropy estimation (in bits)
    - Secure one-click clipboard copying with auto-clear timer support
    - Mask/unmask visibility toggle
    - Session-only metadata history (NEVER stores plaintext passwords)
    - Dual mode: Modern Desktop GUI & CLI interface

Author: Balasujith2007 (OIBSIP Intern)
===============================================================================
"""

import math
import re
import secrets
import string
import sys
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Dict, List, Optional, Set, Tuple


# =============================================================================
# CONSTANTS & CHARACTER SET DEFINITIONS
# =============================================================================

# Base Character Sets
CHARSET_UPPERCASE: str = string.ascii_uppercase  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
CHARSET_LOWERCASE: str = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
CHARSET_NUMBERS: str = string.digits             # '0123456789'
CHARSET_SYMBOLS: str = "!@#$%^&*()-_=+[]{};:,.<>?/|~"

# Ambiguous characters set: visually easily confused glyphs
AMBIGUOUS_CHARACTERS: Set[str] = {
    '0', 'O', 'o',
    '1', 'l', 'I', '|',
    '`', "'", '"',
    ';', ':',
    '\\'
}

# Minimum and Maximum permitted password lengths
MIN_PASSWORD_LENGTH: int = 8
MAX_PASSWORD_LENGTH: int = 128
DEFAULT_PASSWORD_LENGTH: int = 16


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class GeneratorConfig:
    """Immutable configuration specifying password generation parameters."""
    length: int = DEFAULT_PASSWORD_LENGTH
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_numbers: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = False


@dataclass(frozen=True)
class StrengthEvaluation:
    """Detailed evaluation of password strength and theoretical entropy."""
    score: int                     # 0 - 100
    category: str                  # 'Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong'
    color: str                     # Hex color code for UI meter
    estimated_entropy_bits: float  # Shannon/pool entropy in bits
    pool_size: int                 # Size of character pool used
    checklist: List[Tuple[str, bool]]  # (Description, IsSatisfied)
    recommendation: str            # Actionable improvement advice


@dataclass(frozen=True)
class SessionHistoryRecord:
    """
    Session-only metadata record for a generation event.
    CRITICAL SECURITY RULE: Plaintext passwords are NEVER stored in history!
    """
    timestamp: str
    length: int
    categories_used: str
    entropy_bits: float
    strength_category: str


# =============================================================================
# CORE PASSWORD GENERATOR ENGINE
# =============================================================================

class PasswordGeneratorEngine:
    """
    Cryptographically secure password generator engine using Python's `secrets` module.
    Never uses `random.choice()`, `random.randint()`, or `random.shuffle()`.
    """

    @staticmethod
    def filter_ambiguous(charset: str, exclude_ambiguous: bool) -> str:
        """Removes ambiguous characters from a charset if requested."""
        if not exclude_ambiguous:
            return charset
        return "".join(ch for ch in charset if ch not in AMBIGUOUS_CHARACTERS)

    @classmethod
    def get_character_pools(cls, config: GeneratorConfig) -> Dict[str, str]:
        """
        Builds the active character pools based on configuration.
        Returns a dictionary mapping category names to their respective character strings.
        """
        pools: Dict[str, str] = {}

        if config.use_uppercase:
            filtered = cls.filter_ambiguous(CHARSET_UPPERCASE, config.exclude_ambiguous)
            if filtered:
                pools["uppercase"] = filtered

        if config.use_lowercase:
            filtered = cls.filter_ambiguous(CHARSET_LOWERCASE, config.exclude_ambiguous)
            if filtered:
                pools["lowercase"] = filtered

        if config.use_numbers:
            filtered = cls.filter_ambiguous(CHARSET_NUMBERS, config.exclude_ambiguous)
            if filtered:
                pools["numbers"] = filtered

        if config.use_symbols:
            filtered = cls.filter_ambiguous(CHARSET_SYMBOLS, config.exclude_ambiguous)
            if filtered:
                pools["symbols"] = filtered

        return pools

    @classmethod
    def validate_config(cls, config: GeneratorConfig) -> Tuple[bool, Optional[str]]:
        """
        Validates the configuration parameters.
        Returns (is_valid, error_message).
        """
        if not isinstance(config.length, int):
            return False, "Password length must be an integer."

        if config.length < MIN_PASSWORD_LENGTH:
            return False, f"Password length must be at least {MIN_PASSWORD_LENGTH} characters."

        if config.length > MAX_PASSWORD_LENGTH:
            return False, f"Password length cannot exceed {MAX_PASSWORD_LENGTH} characters."

        if not (config.use_uppercase or config.use_lowercase or config.use_numbers or config.use_symbols):
            return False, "Please select at least one character type (Uppercase, Lowercase, Numbers, or Symbols)."

        pools = cls.get_character_pools(config)
        if not pools:
            return False, "Selected character sets are empty after applying ambiguous character exclusion."

        return True, None

    @staticmethod
    def secure_shuffle(items: List[str]) -> List[str]:
        """
        Performs an in-place Fisher-Yates shuffle using cryptographically secure `secrets.randbelow`.
        Eliminates any deterministic or positional bias.
        """
        shuffled = list(items)
        n = len(shuffled)
        for i in range(n - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        return shuffled

    @classmethod
    def generate_password(cls, config: GeneratorConfig) -> str:
        """
        Generates a cryptographically secure random password complying with the config.

        Guarantees:
        1. At least one character is included from EVERY selected active character pool.
        2. Remaining characters are chosen uniformly with `secrets.choice()` from the combined pool.
        3. All characters are shuffled securely using Fisher-Yates with `secrets.randbelow()`.
        """
        is_valid, error_msg = cls.validate_config(config)
        if not is_valid:
            raise ValueError(error_msg or "Invalid generator configuration.")

        pools = cls.get_character_pools(config)
        password_chars: List[str] = []

        # 1. Guarantee at least one character from each selected category
        for category_name, charset in pools.items():
            password_chars.append(secrets.choice(charset))

        # 2. Build the combined active pool
        combined_pool = "".join(pools.values())

        # 3. Securely sample the remaining required characters
        remaining_count = config.length - len(password_chars)
        for _ in range(remaining_count):
            password_chars.append(secrets.choice(combined_pool))

        # 4. Cryptographically shuffle to prevent guaranteed characters from staying at the front
        final_chars = cls.secure_shuffle(password_chars)

        return "".join(final_chars)


# =============================================================================
# STRENGTH & ENTROPY ANALYZER
# =============================================================================

class PasswordStrengthAnalyzer:
    """
    Evaluates password complexity, detects weak patterns, and calculates
    theoretical pool entropy in bits.
    """

    @staticmethod
    def calculate_pool_size(password: str) -> int:
        """Calculates the effective character pool size based on character classes present."""
        pool_size = 0
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_symbol = any(c in CHARSET_SYMBOLS for c in password)

        if has_upper:
            pool_size += len(string.ascii_uppercase)
        if has_lower:
            pool_size += len(string.ascii_lowercase)
        if has_digit:
            pool_size += len(string.digits)
        if has_symbol:
            pool_size += len(CHARSET_SYMBOLS)

        return max(pool_size, 1)

    @classmethod
    def calculate_entropy(cls, password: str, custom_pool_size: Optional[int] = None) -> float:
        """
        Calculates theoretical entropy in bits:
        H ~ L * log2(R)
        where L is length and R is pool size.
        """
        if not password:
            return 0.0

        pool_size = custom_pool_size if custom_pool_size is not None else cls.calculate_pool_size(password)
        if pool_size <= 1:
            return 0.0

        entropy = len(password) * math.log2(pool_size)
        return round(entropy, 1)

    @classmethod
    def evaluate(cls, password: str, active_pool_size: Optional[int] = None) -> StrengthEvaluation:
        """
        Performs a comprehensive evaluation of password strength and returns a StrengthEvaluation.
        """
        if not password:
            return StrengthEvaluation(
                score=0,
                category="Very Weak",
                color="#94a3b8",
                estimated_entropy_bits=0.0,
                pool_size=0,
                checklist=[],
                recommendation="Enter or generate a password to inspect strength."
            )

        length = len(password)
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_symbol = bool(re.search(r'[^A-Za-z0-9]', password))

        # Base scoring calculation
        score = 0

        # Length score (up to 45 pts)
        if length >= 20:
            score += 45
        elif length >= 16:
            score += 35
        elif length >= 12:
            score += 25
        elif length >= 8:
            score += 15
        else:
            score += max(0, length * 2)

        # Character diversity (up to 40 pts, 10 pts each)
        category_count = sum([has_upper, has_lower, has_digit, has_symbol])
        score += category_count * 10

        # Unique character ratio bonus (up to 15 pts)
        unique_ratio = len(set(password)) / length
        score += int(unique_ratio * 15)

        # Penalty for consecutive repeated characters (e.g. 'aaa', '111')
        repeated_pairs = len(re.findall(r'(.)\1', password))
        score -= repeated_pairs * 5

        # Penalty for common sequential runs (e.g., 'abc', '123', 'qwerty')
        lower_pwd = password.lower()
        sequential_patterns = ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', '123', '234', '345', '456', '567', '678', '789', 'qwe', 'asd', 'zxc']
        for pattern in sequential_patterns:
            if pattern in lower_pwd:
                score -= 10

        score = max(5, min(100, score))

        # Determine Category & Color
        if score >= 85 and length >= 14 and category_count >= 3:
            category = "Very Strong"
            color = "#10b981"  # Emerald
            recommendation = "Excellent! Highly resilient against brute-force and dictionary attacks."
        elif score >= 65 and length >= 12 and category_count >= 2:
            category = "Strong"
            color = "#22c55e"  # Green
            recommendation = "Great security posture. Suitable for sensitive and production accounts."
        elif score >= 45:
            category = "Moderate"
            color = "#eab308"  # Amber / Yellow
            recommendation = "Decent strength. Consider increasing length (>=14) or adding symbols for critical systems."
        elif score >= 25:
            category = "Weak"
            color = "#f97316"  # Orange
            recommendation = "Vulnerable to modern cracking dictionaries. Increase length and character diversity."
        else:
            category = "Very Weak"
            color = "#ef4444"  # Red
            recommendation = "High security risk! Do not use this password for any account."

        # Pool size & Entropy
        pool_size = active_pool_size if active_pool_size is not None else cls.calculate_pool_size(password)
        entropy = cls.calculate_entropy(password, pool_size)

        # Checklist for user inspection
        checklist: List[Tuple[str, bool]] = [
            (f"Length ≥ 12 characters ({length})", length >= 12),
            ("Contains Uppercase Letters (A-Z)", has_upper),
            ("Contains Lowercase Letters (a-z)", has_lower),
            ("Contains Numbers (0-9)", has_digit),
            ("Contains Special Symbols (!@#$...)", has_symbol),
            ("High Character Variety (No consecutive duplicates)", repeated_pairs == 0),
        ]

        return StrengthEvaluation(
            score=score,
            category=category,
            color=color,
            estimated_entropy_bits=entropy,
            pool_size=pool_size,
            checklist=checklist,
            recommendation=recommendation
        )


# =============================================================================
# SESSION HISTORY MANAGER (METADATA ONLY)
# =============================================================================

class SessionHistoryManager:
    """
    Maintains an in-memory, session-only audit trail of generation metadata.
    STRICT SECURITY: Never holds plaintext passwords in memory records.
    """

    def __init__(self, max_entries: int = 15):
        self.max_entries: int = max_entries
        self._records: List[SessionHistoryRecord] = []

    def record_generation(self, config: GeneratorConfig, evaluation: StrengthEvaluation) -> SessionHistoryRecord:
        """Creates and stores a metadata-only history entry."""
        cats: List[str] = []
        if config.use_uppercase:
            cats.append("Upper")
        if config.use_lowercase:
            cats.append("Lower")
        if config.use_numbers:
            cats.append("Digits")
        if config.use_symbols:
            cats.append("Symbols")

        record = SessionHistoryRecord(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            length=config.length,
            categories_used="+".join(cats) or "None",
            entropy_bits=evaluation.estimated_entropy_bits,
            strength_category=evaluation.category
        )

        self._records.insert(0, record)
        if len(self._records) > self.max_entries:
            self._records.pop()

        return record

    def get_records(self) -> List[SessionHistoryRecord]:
        """Returns a copy of session records."""
        return list(self._records)

    def clear(self) -> None:
        """Clears all session metadata."""
        self._records.clear()


# =============================================================================
# TKINTER MODERN DESKTOP GUI
# =============================================================================

class PasswordGeneratorApp:
    """
    Modern Tkinter desktop graphical user interface for the Random Password Generator.
    Designed with a sleek dark theme, responsive layout, real-time strength visualizer,
    and comprehensive configuration controls.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Secure Random Password Generator — OIBSIP Task 3")
        self.root.geometry("640x780")
        self.root.minsize(580, 700)

        # UI Color Palette (Modern Slate / Dark Theme)
        self.colors = {
            "bg_dark": "#0f172a",       # Slate 900
            "bg_card": "#1e293b",       # Slate 800
            "bg_input": "#334155",      # Slate 700
            "border": "#475569",        # Slate 600
            "text_light": "#f8fafc",    # Slate 50
            "text_muted": "#94a3b8",    # Slate 400
            "accent_primary": "#3b82f6", # Blue 500
            "accent_hover": "#2563eb",  # Blue 600
            "accent_success": "#10b981",# Emerald 500
            "accent_danger": "#ef4444", # Red 500
            "accent_purple": "#8b5cf6"  # Violet 500
        }

        self.root.configure(bg=self.colors["bg_dark"])

        # Engine & Session Management
        self.history_mgr = SessionHistoryManager(max_entries=10)
        self.current_password: str = ""
        self.is_password_visible: bool = False
        self.clipboard_clear_job: Optional[str] = None

        # Variables
        self.length_var = tk.IntVar(value=DEFAULT_PASSWORD_LENGTH)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.num_var = tk.BooleanVar(value=True)
        self.sym_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)
        self.auto_clear_clip_var = tk.BooleanVar(value=True)

        self._configure_styles()
        self._build_ui()
        self._generate_password_action()

    def _configure_styles(self) -> None:
        """Sets up ttk styles for polished controls."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=self.colors["bg_dark"], foreground=self.colors["text_light"], font=("Segoe UI", 10))
        style.configure("TCheckbutton", background=self.colors["bg_card"], foreground=self.colors["text_light"], font=("Segoe UI", 10))
        style.map("TCheckbutton", background=[("active", self.colors["bg_card"])], foreground=[("active", self.colors["text_light"])])

        style.configure("TScale", background=self.colors["bg_card"], troughcolor=self.colors["bg_input"])

    def _build_ui(self) -> None:
        """Constructs the complete layout hierarchy."""
        main_container = tk.Frame(self.root, bg=self.colors["bg_dark"], padx=18, pady=14)
        main_container.pack(fill="both", expand=True)

        # Header Section
        header_frame = tk.Frame(main_container, bg=self.colors["bg_dark"])
        header_frame.pack(fill="x", pady=(0, 10))

        title_lbl = tk.Label(
            header_frame,
            text="🔐 Secure Password Generator",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_light"]
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header_frame,
            text="CSPRNG Cryptographically Secure Generation • OASIS INFOBYTE SIP",
            font=("Segoe UI", 9),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_muted"]
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Generated Password Display Card
        self._build_display_card(main_container)

        # Configuration Options Card
        self._build_options_card(main_container)

        # Strength & Entropy Analysis Card
        self._build_strength_card(main_container)

        # Session History Card
        self._build_history_card(main_container)

    def _build_display_card(self, parent: tk.Widget) -> None:
        """Constructs the primary password display and action button panel."""
        card = tk.Frame(parent, bg=self.colors["bg_card"], bd=1, relief="solid", padx=14, pady=12)
        card.pack(fill="x", pady=(0, 10))

        lbl_row = tk.Frame(card, bg=self.colors["bg_card"])
        lbl_row.pack(fill="x", pady=(0, 4))

        tk.Label(
            lbl_row,
            text="GENERATED PASSWORD",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["text_muted"]
        ).pack(side="left")

        self.status_feedback_lbl = tk.Label(
            lbl_row,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["accent_success"]
        )
        self.status_feedback_lbl.pack(side="right")

        # Password Entry / Display Field
        entry_frame = tk.Frame(card, bg=self.colors["bg_input"], bd=1, relief="flat", padx=6, pady=4)
        entry_frame.pack(fill="x", pady=(0, 10))

        self.password_entry = tk.Entry(
            entry_frame,
            font=("Consolas", 14, "bold"),
            bg=self.colors["bg_input"],
            fg=self.colors["text_light"],
            insertbackground=self.colors["text_light"],
            relief="flat",
            justify="center"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(4, 6))
        self.password_entry.bind("<Key>", lambda e: "break")  # Read-only interaction

        # Visibility toggle button (Eye icon)
        self.btn_visibility = tk.Button(
            entry_frame,
            text="👁 Show",
            font=("Segoe UI", 9),
            bg=self.colors["bg_card"],
            fg=self.colors["text_light"],
            activebackground=self.colors["border"],
            activeforeground=self.colors["text_light"],
            relief="flat",
            cursor="hand2",
            padx=8,
            command=self._toggle_visibility
        )
        self.btn_visibility.pack(side="right")

        # Primary Action Buttons
        btn_row = tk.Frame(card, bg=self.colors["bg_card"])
        btn_row.pack(fill="x")

        self.btn_generate = tk.Button(
            btn_row,
            text="⚡ Generate New",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent_primary"],
            fg="#ffffff",
            activebackground=self.colors["accent_hover"],
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=self._generate_password_action
        )
        self.btn_generate.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_copy = tk.Button(
            btn_row,
            text="📋 Copy",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_input"],
            fg=self.colors["text_light"],
            activebackground=self.colors["border"],
            activeforeground=self.colors["text_light"],
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=self._copy_to_clipboard
        )
        self.btn_copy.pack(side="left", fill="x", expand=True, padx=4)

        self.btn_clear = tk.Button(
            btn_row,
            text="🧹 Clear",
            font=("Segoe UI", 10),
            bg=self.colors["bg_input"],
            fg=self.colors["accent_danger"],
            activebackground=self.colors["border"],
            activeforeground=self.colors["accent_danger"],
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self._clear_interface
        )
        self.btn_clear.pack(side="left", padx=(4, 0))

    def _build_options_card(self, parent: tk.Widget) -> None:
        """Constructs length selection and character options controls."""
        card = tk.Frame(parent, bg=self.colors["bg_card"], bd=1, relief="solid", padx=14, pady=10)
        card.pack(fill="x", pady=(0, 10))

        # Title
        tk.Label(
            card,
            text="CONFIGURATION & CHARACTER TYPES",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["text_muted"]
        ).pack(anchor="w", pady=(0, 6))

        # Length Slider & Numeric Entry Row
        len_row = tk.Frame(card, bg=self.colors["bg_card"])
        len_row.pack(fill="x", pady=(0, 8))

        tk.Label(
            len_row,
            text="Length:",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["text_light"]
        ).pack(side="left")

        self.length_spinbox = tk.Spinbox(
            len_row,
            from_=MIN_PASSWORD_LENGTH,
            to=MAX_PASSWORD_LENGTH,
            textvariable=self.length_var,
            width=5,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_input"],
            fg=self.colors["text_light"],
            buttonbackground=self.colors["bg_input"],
            relief="flat",
            command=self._on_config_change
        )
        self.length_spinbox.pack(side="left", padx=(8, 12))
        self.length_spinbox.bind("<Return>", lambda e: self._on_config_change())
        self.length_spinbox.bind("<FocusOut>", lambda e: self._on_config_change())

        self.length_scale = ttk.Scale(
            len_row,
            from_=MIN_PASSWORD_LENGTH,
            to=MAX_PASSWORD_LENGTH,
            variable=self.length_var,
            orient="horizontal",
            command=lambda v: self._sync_scale(v)
        )
        self.length_scale.pack(side="left", fill="x", expand=True)

        # Quick preset buttons (12, 16, 24, 32, 64)
        preset_frame = tk.Frame(card, bg=self.colors["bg_card"])
        preset_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            preset_frame,
            text="Presets:",
            font=("Segoe UI", 8),
            bg=self.colors["bg_card"],
            fg=self.colors["text_muted"]
        ).pack(side="left", padx=(0, 6))

        for size in [8, 12, 16, 20, 32, 64]:
            btn = tk.Button(
                preset_frame,
                text=str(size),
                font=("Segoe UI", 8),
                bg=self.colors["bg_input"],
                fg=self.colors["text_light"],
                relief="flat",
                cursor="hand2",
                padx=5,
                pady=1,
                command=lambda s=size: self._set_length_preset(s)
            )
            btn.pack(side="left", padx=2)

        # Checkboxes grid
        grid_frame = tk.Frame(card, bg=self.colors["bg_card"])
        grid_frame.pack(fill="x", pady=(0, 4))

        cb_upper = ttk.Checkbutton(
            grid_frame,
            text="Uppercase (A-Z)",
            variable=self.upper_var,
            command=self._on_config_change
        )
        cb_upper.grid(row=0, column=0, sticky="w", padx=(0, 16), pady=2)

        cb_lower = ttk.Checkbutton(
            grid_frame,
            text="Lowercase (a-z)",
            variable=self.lower_var,
            command=self._on_config_change
        )
        cb_lower.grid(row=0, column=1, sticky="w", pady=2)

        cb_num = ttk.Checkbutton(
            grid_frame,
            text="Numbers (0-9)",
            variable=self.num_var,
            command=self._on_config_change
        )
        cb_num.grid(row=1, column=0, sticky="w", padx=(0, 16), pady=2)

        cb_sym = ttk.Checkbutton(
            grid_frame,
            text="Symbols (!@#$...)",
            variable=self.sym_var,
            command=self._on_config_change
        )
        cb_sym.grid(row=1, column=1, sticky="w", pady=2)

        # Ambiguous characters checkbox
        cb_ambig = ttk.Checkbutton(
            card,
            text="Exclude Ambiguous Characters (e.g. 0/O, 1/l/I, |)",
            variable=self.ambiguous_var,
            command=self._on_config_change
        )
        cb_ambig.pack(anchor="w", pady=(4, 0))

    def _build_strength_card(self, parent: tk.Widget) -> None:
        """Constructs the real-time strength evaluation, entropy, and factor checklist."""
        card = tk.Frame(parent, bg=self.colors["bg_card"], bd=1, relief="solid", padx=14, pady=10)
        card.pack(fill="x", pady=(0, 10))

        # Header with Strength Badge & Entropy
        header_row = tk.Frame(card, bg=self.colors["bg_card"])
        header_row.pack(fill="x", pady=(0, 4))

        tk.Label(
            header_row,
            text="STRENGTH & ESTIMATED ENTROPY",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["text_muted"]
        ).pack(side="left")

        self.entropy_lbl = tk.Label(
            header_row,
            text="Entropy: ~0.0 bits",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["accent_purple"]
        )
        self.entropy_lbl.pack(side="right")

        # Strength Meter Canvas
        meter_row = tk.Frame(card, bg=self.colors["bg_card"])
        meter_row.pack(fill="x", pady=(2, 6))

        self.strength_lbl = tk.Label(
            meter_row,
            text="Strength: Strong",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["accent_success"]
        )
        self.strength_lbl.pack(side="left", padx=(0, 10))

        self.meter_canvas = tk.Canvas(
            meter_row,
            height=10,
            bg=self.colors["bg_input"],
            highlightthickness=0,
            bd=0
        )
        self.meter_canvas.pack(side="left", fill="x", expand=True)

        # Metrics Details Row (Pool Size, Types Count, Shannon Entropy)
        self.metrics_lbl = tk.Label(
            card,
            text="Pool Size: 0 • Active Categories: 0 • Calculated Bit-Strength: 0.0 bits",
            font=("Segoe UI", 8),
            bg=self.colors["bg_card"],
            fg=self.colors["text_muted"]
        )
        self.metrics_lbl.pack(anchor="w", pady=(0, 4))

        # Recommendation Text
        self.recommendation_lbl = tk.Label(
            card,
            text="",
            font=("Segoe UI", 8, "italic"),
            bg=self.colors["bg_card"],
            fg=self.colors["text_light"],
            wraplength=550,
            justify="left"
        )
        self.recommendation_lbl.pack(anchor="w")

    def _build_history_card(self, parent: tk.Widget) -> None:
        """Constructs the session-only audit history view."""
        card = tk.Frame(parent, bg=self.colors["bg_card"], bd=1, relief="solid", padx=14, pady=8)
        card.pack(fill="both", expand=True)

        header_row = tk.Frame(card, bg=self.colors["bg_card"])
        header_row.pack(fill="x", pady=(0, 4))

        tk.Label(
            header_row,
            text="SESSION GENERATION HISTORY (METADATA ONLY)",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["text_muted"]
        ).pack(side="left")

        btn_clear_hist = tk.Button(
            header_row,
            text="Clear History",
            font=("Segoe UI", 8),
            bg=self.colors["bg_input"],
            fg=self.colors["text_muted"],
            activebackground=self.colors["border"],
            activeforeground=self.colors["text_light"],
            relief="flat",
            cursor="hand2",
            padx=4,
            command=self._clear_history
        )
        btn_clear_hist.pack(side="right")

        # History Treeview
        tree_frame = tk.Frame(card, bg=self.colors["bg_input"])
        tree_frame.pack(fill="both", expand=True)

        columns = ("time", "length", "types", "entropy", "strength")
        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=4,
            selectmode="none"
        )

        self.history_tree.heading("time", text="Time")
        self.history_tree.heading("length", text="Length")
        self.history_tree.heading("types", text="Categories")
        self.history_tree.heading("entropy", text="Entropy")
        self.history_tree.heading("strength", text="Rating")

        self.history_tree.column("time", width=70, anchor="center")
        self.history_tree.column("length", width=60, anchor="center")
        self.history_tree.column("types", width=160, anchor="center")
        self.history_tree.column("entropy", width=90, anchor="center")
        self.history_tree.column("strength", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # =========================================================================
    # EVENT HANDLERS & LOGIC
    # =========================================================================

    def _sync_scale(self, val_str: str) -> None:
        """Synchronizes the integer length variable when the scale slider moves."""
        try:
            val = int(float(val_str))
            self.length_var.set(val)
        except (ValueError, TypeError):
            pass

    def _set_length_preset(self, size: int) -> None:
        """Applies a preset length value and generates a new password."""
        self.length_var.set(size)
        self._generate_password_action()

    def _on_config_change(self) -> None:
        """Invoked when user modifies length or checkboxes."""
        self._generate_password_action()

    def _get_current_config(self) -> GeneratorConfig:
        """Extracts the current GUI configuration parameters into an immutable dataclass."""
        try:
            length = int(self.length_var.get())
        except (ValueError, tk.TclError):
            length = DEFAULT_PASSWORD_LENGTH

        return GeneratorConfig(
            length=length,
            use_uppercase=self.upper_var.get(),
            use_lowercase=self.lower_var.get(),
            use_numbers=self.num_var.get(),
            use_symbols=self.sym_var.get(),
            exclude_ambiguous=self.ambiguous_var.get()
        )

    def _generate_password_action(self) -> None:
        """Generates a new secure password and refreshes UI components."""
        config = self._get_current_config()
        is_valid, error_msg = PasswordGeneratorEngine.validate_config(config)

        if not is_valid:
            messagebox.showwarning("Configuration Error", error_msg or "Invalid configuration.")
            return

        try:
            self.current_password = PasswordGeneratorEngine.generate_password(config)
            self._update_display()
            self._update_strength_display(config)

            # Record session metadata
            evaluation = PasswordStrengthAnalyzer.evaluate(
                self.current_password,
                sum(len(p) for p in PasswordGeneratorEngine.get_character_pools(config).values())
            )
            self.history_mgr.record_generation(config, evaluation)
            self._refresh_history_tree()

        except Exception as e:
            messagebox.showerror("Generation Error", f"An unexpected error occurred: {str(e)}")

    def _update_display(self) -> None:
        """Updates the password entry field honoring the visibility toggle."""
        self.password_entry.delete(0, tk.END)
        if self.is_password_visible:
            self.password_entry.insert(0, self.current_password)
            self.btn_visibility.configure(text="🔒 Hide")
        else:
            self.password_entry.insert(0, "•" * len(self.current_password))
            self.btn_visibility.configure(text="👁 Show")

    def _toggle_visibility(self) -> None:
        """Toggles masking on/off."""
        if not self.current_password:
            return
        self.is_password_visible = not self.is_password_visible
        self._update_display()

    def _update_strength_display(self, config: GeneratorConfig) -> None:
        """Renders the strength meter bar, entropy estimate, and metrics."""
        pools = PasswordGeneratorEngine.get_character_pools(config)
        total_pool_size = sum(len(p) for p in pools.values())
        evaluation = PasswordStrengthAnalyzer.evaluate(self.current_password, total_pool_size)

        # Update labels
        self.strength_lbl.configure(text=f"Strength: {evaluation.category}", fg=evaluation.color)
        self.entropy_lbl.configure(text=f"Estimated Entropy: ~{evaluation.estimated_entropy_bits} bits")
        self.metrics_lbl.configure(
            text=f"Pool Size: {total_pool_size} chars • Active Categories: {len(pools)}/4 • "
                 f"Length: {len(self.current_password)}"
        )
        self.recommendation_lbl.configure(text=evaluation.recommendation)

        # Draw meter bar on canvas
        self.root.update_idletasks()
        w = self.meter_canvas.winfo_width()
        if w <= 1:
            w = 200
        h = self.meter_canvas.winfo_height()
        if h <= 1:
            h = 10

        self.meter_canvas.delete("all")
        fill_width = int((evaluation.score / 100.0) * w)

        # Draw background bar
        self.meter_canvas.create_rectangle(0, 0, w, h, fill=self.colors["bg_input"], width=0)
        # Draw active meter bar
        if fill_width > 0:
            self.meter_canvas.create_rectangle(0, 0, fill_width, h, fill=evaluation.color, width=0)

    def _copy_to_clipboard(self) -> None:
        """Copies the active password to system clipboard and sets a temporary notification."""
        if not self.current_password:
            messagebox.showinfo("Clipboard", "No password generated to copy.")
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_password)
            self.root.update()

            self.status_feedback_lbl.configure(text="✓ Copied to clipboard!")
            self.root.after(3000, lambda: self.status_feedback_lbl.configure(text=""))

            # Optional: auto-clear clipboard after 45 seconds for extra security
            if self.clipboard_clear_job:
                self.root.after_cancel(self.clipboard_clear_job)
            self.clipboard_clear_job = self.root.after(45000, self._auto_clear_clipboard)

        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {e}")

    def _auto_clear_clipboard(self) -> None:
        """Clears clipboard after timeout if it still contains the generated password."""
        try:
            current_clip = self.root.clipboard_get()
            if current_clip == self.current_password:
                self.root.clipboard_clear()
        except Exception:
            pass

    def _clear_interface(self) -> None:
        """Clears the displayed password and resets the interface state securely."""
        self.current_password = ""
        self.password_entry.delete(0, tk.END)
        self.status_feedback_lbl.configure(text="")
        self.strength_lbl.configure(text="Strength: Cleared", fg=self.colors["text_muted"])
        self.entropy_lbl.configure(text="Entropy: ~0.0 bits")
        self.metrics_lbl.configure(text="Pool Size: 0 • Active Categories: 0 • Length: 0")
        self.recommendation_lbl.configure(text="Ready to generate a new password.")
        self.meter_canvas.delete("all")

    def _refresh_history_tree(self) -> None:
        """Renders the in-memory metadata records into the Treeview."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for rec in self.history_mgr.get_records():
            self.history_tree.insert(
                "",
                "end",
                values=(rec.timestamp, f"{rec.length} chars", rec.categories_used, f"{rec.entropy_bits} bits", rec.strength_category)
            )

    def _clear_history(self) -> None:
        """Empties the session metadata history."""
        self.history_mgr.clear()
        self._refresh_history_tree()


# =============================================================================
# CLI INTERFACE (OPTIONAL DUAL MODE)
# =============================================================================

def run_cli_mode() -> None:
    """Provides a clean, interactive command-line interface for terminal environments."""
    print("=" * 60)
    print("  OIBSIP TASK 3 -- SECURE RANDOM PASSWORD GENERATOR (CLI)")
    print("=" * 60)
    print("Cryptographically secure generation via Python `secrets` CSPRNG.\n")

    try:
        raw_len = input(f"Enter password length [{MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH}, default 16]: ").strip()
        length = int(raw_len) if raw_len else DEFAULT_PASSWORD_LENGTH

        use_upper = input("Include Uppercase letters (A-Z)? [Y/n]: ").strip().lower() != 'n'
        use_lower = input("Include Lowercase letters (a-z)? [Y/n]: ").strip().lower() != 'n'
        use_num = input("Include Numbers (0-9)? [Y/n]: ").strip().lower() != 'n'
        use_sym = input("Include Symbols (!@#$...)? [Y/n]: ").strip().lower() != 'n'
        exclude_ambig = input("Exclude Ambiguous Characters (0/O, 1/l/I)? [y/N]: ").strip().lower() == 'y'

        config = GeneratorConfig(
            length=length,
            use_uppercase=use_upper,
            use_lowercase=use_lower,
            use_numbers=use_num,
            use_symbols=use_sym,
            exclude_ambiguous=exclude_ambig
        )

        is_valid, err = PasswordGeneratorEngine.validate_config(config)
        if not is_valid:
            print(f"\n[!] Configuration Error: {err}")
            return

        password = PasswordGeneratorEngine.generate_password(config)
        pools = PasswordGeneratorEngine.get_character_pools(config)
        total_pool_size = sum(len(p) for p in pools.values())
        evaluation = PasswordStrengthAnalyzer.evaluate(password, total_pool_size)

        print("\n" + "-" * 60)
        print(f"Generated Password : {password}")
        print(f"Password Length    : {len(password)} characters")
        print(f"Pool Size          : {total_pool_size} characters")
        print(f"Estimated Entropy  : ~{evaluation.estimated_entropy_bits} bits")
        print(f"Strength Rating    : {evaluation.category} ({evaluation.score}/100)")
        print(f"Advice             : {evaluation.recommendation}")
        print("-" * 60)

    except (ValueError, KeyboardInterrupt) as e:
        print(f"\n[!] Error / Interrupted: {e}")


# =============================================================================
# APPLICATION ENTRYPOINT
# =============================================================================

def main() -> None:
    """Main execution router (GUI or CLI based on arguments or environment)."""
    if "--cli" in sys.argv or "-c" in sys.argv:
        run_cli_mode()
    else:
        try:
            root = tk.Tk()
            app = PasswordGeneratorApp(root)
            root.mainloop()
        except tk.TclError:
            # Fallback to CLI if headless / display-less environment
            print("[*] Display not available or Tkinter failed. Launching CLI mode...")
            run_cli_mode()


if __name__ == "__main__":
    main()
