"""
=============================================================================
 Oasis Infobyte SIP — Python Programming Internship
 Task 2: BMI (Body Mass Index) Calculator
 
 Description:
 A modern, interactive, and beginner-friendly Body Mass Index (BMI)
 calculator application supporting both Metric (kg/cm) and Imperial (lb/in)
 systems, real-time input validation, category classification, session
 history, and health recommendations.
=============================================================================
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

APP_TITLE = "Oasis Infobyte — BMI Calculator"
APP_VERSION = "2.0.0"

# Category Definitions (Thresholds & Metadata)
CATEGORY_UNDERWEIGHT = "Underweight"
CATEGORY_NORMAL = "Normal weight"
CATEGORY_OVERWEIGHT = "Overweight"
CATEGORY_OBESITY = "Obesity"

# Category Color Scheme (Modern, High-Contrast UI Badges)
CATEGORY_COLORS = {
    CATEGORY_UNDERWEIGHT: {"bg": "#E0F2FE", "fg": "#0369A1", "badge": "#0284C7"},
    CATEGORY_NORMAL:      {"bg": "#DCFCE7", "fg": "#15803D", "badge": "#16A34A"},
    CATEGORY_OVERWEIGHT:  {"bg": "#FEF3C7", "fg": "#B45309", "badge": "#D97706"},
    CATEGORY_OBESITY:     {"bg": "#FEE2E2", "fg": "#B91C1C", "badge": "#DC2626"},
}

HEALTH_DISCLAIMER = (
    "⚠️ Disclaimer: BMI is a general screening measure and does not replace "
    "professional medical advice, diagnosis, or personalized care."
)


# =============================================================================
# CORE BMI CALCULATION ENGINE (MODULAR LOGIC)
# =============================================================================

def calculate_bmi_metric(weight_kg: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index (BMI) using Metric units.
    
    Formula:
        height_m = height_cm / 100
        BMI = weight_kg / (height_m ^ 2)
        
    Args:
        weight_kg: Body weight in kilograms.
        height_cm: Body height in centimeters.
        
    Returns:
        float: Calculated BMI rounded to 2 decimal places.
        
    Raises:
        ValueError: If height_cm or weight_kg <= 0.
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Height and weight must be greater than zero.")
    
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def calculate_bmi_imperial(weight_lb: float, height_in: float) -> float:
    """
    Calculate Body Mass Index (BMI) using Imperial units.
    
    Formula:
        BMI = (weight_lb / (height_in ^ 2)) * 703
        
    Args:
        weight_lb: Body weight in pounds.
        height_in: Body height in inches.
        
    Returns:
        float: Calculated BMI rounded to 2 decimal places.
        
    Raises:
        ValueError: If height_in or weight_lb <= 0.
    """
    if height_in <= 0 or weight_lb <= 0:
        raise ValueError("Height and weight must be greater than zero.")
    
    bmi = (weight_lb / (height_in ** 2)) * 703.0
    return round(bmi, 2)


def get_bmi_category(bmi: float) -> Tuple[str, str, str]:
    """
    Determine the standard WHO adult BMI classification category.
    
    Categories:
        - BMI < 18.5: Underweight
        - 18.5 <= BMI <= 24.9: Normal weight
        - 25.0 <= BMI <= 29.9: Overweight
        - BMI >= 30.0: Obesity
        
    Args:
        bmi: Calculated BMI value.
        
    Returns:
        Tuple[str, str, str]: (Category Name, Summary Advice, Category Hex Color)
    """
    if bmi < 18.5:
        category = CATEGORY_UNDERWEIGHT
        advice = "Consider consulting a healthcare provider about balanced nutrition."
    elif 18.5 <= bmi <= 24.9:
        category = CATEGORY_NORMAL
        advice = "Great job! Maintain your balanced diet and regular physical activity."
    elif 25.0 <= bmi <= 29.9:
        category = CATEGORY_OVERWEIGHT
        advice = "Engaging in regular exercise and a balanced diet can help reach a normal BMI."
    else:
        category = CATEGORY_OBESITY
        advice = "Consult a certified healthcare specialist or dietitian for guidance."
        
    color = CATEGORY_COLORS[category]["badge"]
    return category, advice, color


def calculate_healthy_weight_range(height_val: float, unit_system: str) -> Tuple[float, float]:
    """
    Calculate the recommended healthy weight range (BMI 18.5 to 24.9) for a given height.
    
    Args:
        height_val: Height in cm (Metric) or inches (Imperial).
        unit_system: "Metric" or "Imperial".
        
    Returns:
        Tuple[float, float]: (Min Healthy Weight, Max Healthy Weight)
    """
    if height_val <= 0:
        return 0.0, 0.0
    
    if unit_system == "Metric":
        height_m = height_val / 100.0
        min_wt = 18.5 * (height_m ** 2)
        max_wt = 24.9 * (height_m ** 2)
        return round(min_wt, 1), round(max_wt, 1)
    else:
        min_wt = (18.5 * (height_val ** 2)) / 703.0
        max_wt = (24.9 * (height_val ** 2)) / 703.0
        return round(min_wt, 1), round(max_wt, 1)


def validate_input(
    height_str: str,
    weight_str: str,
    unit_system: str
) -> Tuple[bool, Optional[float], Optional[float], str]:
    """
    Validate height and weight string inputs according to unit bounds and realism.
    
    Args:
        height_str: Raw height input string.
        weight_str: Raw weight input string.
        unit_system: "Metric" or "Imperial".
        
    Returns:
        Tuple[bool, Optional[float], Optional[float], str]:
            (is_valid, height_float, weight_float, error_message)
    """
    # 1. Empty Check
    height_str = height_str.strip()
    weight_str = weight_str.strip()
    
    if not height_str and not weight_str:
        return False, None, None, "Please enter your height and weight."
    if not height_str:
        return False, None, None, "Please enter your height."
    if not weight_str:
        return False, None, None, "Please enter your weight."
        
    # 2. Number Conversion Check
    try:
        height = float(height_str)
    except ValueError:
        return False, None, None, "Height must be a valid number (e.g. 175 or 68)."
        
    try:
        weight = float(weight_str)
    except ValueError:
        return False, None, None, "Weight must be a valid number (e.g. 70 or 154)."
        
    # 3. Positive Non-Zero Check
    if height <= 0:
        return False, None, None, "Height must be greater than zero."
    if weight <= 0:
        return False, None, None, "Weight must be greater than zero."
        
    # 4. Realistic Range Sanity Checks
    if unit_system == "Metric":
        if height < 40 or height > 280:
            return False, None, None, "Please enter a realistic height between 40 cm and 280 cm."
        if weight < 10 or weight > 500:
            return False, None, None, "Please enter a realistic weight between 10 kg and 500 kg."
    else:
        if height < 15 or height > 110:
            return False, None, None, "Please enter a realistic height between 15 in and 110 in."
        if weight < 20 or weight > 1100:
            return False, None, None, "Please enter a realistic weight between 20 lb and 1100 lb."
            
    return True, height, weight, ""


# =============================================================================
# GRAPHICAL USER INTERFACE (TKINTER)
# =============================================================================

class BMICalculatorApp:
    """
    Professional Tkinter GUI for Oasis Infobyte BMI Calculator.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("800x680")
        self.root.minsize(720, 620)
        
        # Session History Storage (in-memory)
        self.history: List[Dict[str, Any]] = []
        
        # Styling Configuration
        self._setup_theme()
        
        # Build UI Components
        self._build_ui()
        
        # Set Default State
        self.unit_var.set("Metric")
        self._on_unit_change()

    def _setup_theme(self):
        """Configure clean modern colors and ttk widget styles."""
        self.root.configure(bg="#F8FAFC")  # Slate 50 background
        
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Custom TTK Styling
        style.configure("Main.TFrame", background="#F8FAFC")
        style.configure("Card.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)
        style.configure("Header.TLabel", background="#0F172A", foreground="#FFFFFF", font=("Segoe UI", 16, "bold"))
        style.configure("SubHeader.TLabel", background="#0F172A", foreground="#94A3B8", font=("Segoe UI", 9))
        
        style.configure("FieldLabel.TLabel", background="#FFFFFF", foreground="#334155", font=("Segoe UI", 10, "bold"))
        style.configure("UnitHint.TLabel", background="#FFFFFF", foreground="#64748B", font=("Segoe UI", 9, "italic"))
        
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background="#2563EB", foreground="#FFFFFF")
        style.map("Primary.TButton", background=[("active", "#1D4ED8")])
        
        style.configure("Secondary.TButton", font=("Segoe UI", 10), background="#E2E8F0", foreground="#334155")
        style.map("Secondary.TButton", background=[("active", "#CBD5E1")])

    def _build_ui(self):
        """Construct all UI sections and layout grids."""
        # Top Header Banner
        header_frame = tk.Frame(self.root, bg="#0F172A", pady=14, padx=20)
        header_frame.pack(fill="x", side="top")
        
        title_lbl = tk.Label(
            header_frame,
            text="⚖️ Oasis Infobyte — BMI Calculator",
            font=("Segoe UI", 16, "bold"),
            bg="#0F172A",
            fg="#F8FAFC"
        )
        title_lbl.pack(anchor="w")
        
        sub_lbl = tk.Label(
            header_frame,
            text="Python Programming Internship • Task 2 • Advanced Tier",
            font=("Segoe UI", 9),
            bg="#0F172A",
            fg="#94A3B8"
        )
        sub_lbl.pack(anchor="w")

        # Main Scrollable / Padded Body
        body_container = tk.Frame(self.root, bg="#F8FAFC", padx=20, pady=16)
        body_container.pack(fill="both", expand=True)

        # Left Column: Input Form & Result Card
        left_col = tk.Frame(body_container, bg="#F8FAFC")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Right Column: Session History
        right_col = tk.Frame(body_container, bg="#F8FAFC", width=300)
        right_col.pack(side="right", fill="both", expand=False, padx=(10, 0))

        # -------------------------------------------------------------
        # 1. INPUT CARD
        # -------------------------------------------------------------
        input_card = tk.LabelFrame(
            left_col,
            text=" ⚙️ Input Parameters ",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#1E293B",
            padx=16,
            pady=12,
            relief="solid",
            bd=1
        )
        input_card.pack(fill="x", pady=(0, 12))

        # Unit System Selection
        unit_lbl = tk.Label(input_card, text="Unit System:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#334155")
        unit_lbl.grid(row=0, column=0, sticky="w", pady=6)
        
        self.unit_var = tk.StringVar(value="Metric")
        unit_frame = tk.Frame(input_card, bg="#FFFFFF")
        unit_frame.grid(row=0, column=1, columnspan=2, sticky="w", pady=6)

        r_metric = tk.Radiobutton(
            unit_frame, text="Metric (cm / kg)", variable=self.unit_var, value="Metric",
            command=self._on_unit_change, font=("Segoe UI", 9), bg="#FFFFFF", activebackground="#FFFFFF"
        )
        r_metric.pack(side="left", padx=(0, 10))

        r_imperial = tk.Radiobutton(
            unit_frame, text="Imperial (in / lb)", variable=self.unit_var, value="Imperial",
            command=self._on_unit_change, font=("Segoe UI", 9), bg="#FFFFFF", activebackground="#FFFFFF"
        )
        r_imperial.pack(side="left")

        # Height Entry
        self.height_label = tk.Label(input_card, text="Height (cm):", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#334155")
        self.height_label.grid(row=1, column=0, sticky="w", pady=6)

        self.height_entry = ttk.Entry(input_card, font=("Segoe UI", 11), width=16)
        self.height_entry.grid(row=1, column=1, sticky="w", pady=6)
        self.height_entry.focus()
        self.height_entry.bind("<Return>", lambda e: self.calculate_result())

        self.height_hint = tk.Label(input_card, text="e.g. 175 cm", font=("Segoe UI", 9, "italic"), bg="#FFFFFF", fg="#94A3B8")
        self.height_hint.grid(row=1, column=2, sticky="w", padx=8)

        # Weight Entry
        self.weight_label = tk.Label(input_card, text="Weight (kg):", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#334155")
        self.weight_label.grid(row=2, column=0, sticky="w", pady=6)

        self.weight_entry = ttk.Entry(input_card, font=("Segoe UI", 11), width=16)
        self.weight_entry.grid(row=2, column=1, sticky="w", pady=6)
        self.weight_entry.bind("<Return>", lambda e: self.calculate_result())

        self.weight_hint = tk.Label(input_card, text="e.g. 70 kg", font=("Segoe UI", 9, "italic"), bg="#FFFFFF", fg="#94A3B8")
        self.weight_hint.grid(row=2, column=2, sticky="w", padx=8)

        # Buttons Row
        btn_frame = tk.Frame(input_card, bg="#FFFFFF", pady=8)
        btn_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))

        calc_btn = tk.Button(
            btn_frame,
            text="⚡ Calculate BMI",
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.calculate_result
        )
        calc_btn.pack(side="left", padx=(0, 10))

        clear_btn = tk.Button(
            btn_frame,
            text="🔄 Clear Form",
            font=("Segoe UI", 10),
            bg="#F1F5F9",
            fg="#475569",
            activebackground="#E2E8F0",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.clear_form
        )
        clear_btn.pack(side="left")

        # Inline Error Message Label
        self.error_label = tk.Label(input_card, text="", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#DC2626", wraplength=350)
        self.error_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # -------------------------------------------------------------
        # 2. RESULT CARD
        # -------------------------------------------------------------
        self.result_card = tk.LabelFrame(
            left_col,
            text=" 📊 BMI Calculation Result ",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#1E293B",
            padx=16,
            pady=12,
            relief="solid",
            bd=1
        )
        self.result_card.pack(fill="both", expand=True)

        self.res_placeholder = tk.Label(
            self.result_card,
            text="Enter your height and weight above,\nthen click 'Calculate BMI'.",
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            fg="#94A3B8",
            pady=24
        )
        self.res_placeholder.pack()

        self.res_content_frame = tk.Frame(self.result_card, bg="#FFFFFF")

        # Top row: BMI Value and Badge
        top_res_row = tk.Frame(self.res_content_frame, bg="#FFFFFF")
        top_res_row.pack(fill="x", pady=(0, 8))

        tk.Label(top_res_row, text="BMI Value:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#64748B").pack(anchor="w")
        
        self.bmi_display_val = tk.Label(
            top_res_row,
            text="--",
            font=("Segoe UI", 28, "bold"),
            bg="#FFFFFF",
            fg="#0F172A"
        )
        self.bmi_display_val.pack(anchor="w")

        # Category Badge
        self.category_badge = tk.Label(
            top_res_row,
            text="Normal weight",
            font=("Segoe UI", 11, "bold"),
            bg="#DCFCE7",
            fg="#15803D",
            padx=12,
            pady=4
        )
        self.category_badge.pack(anchor="w", pady=(2, 6))

        # Advice & Healthy Range
        self.advice_label = tk.Label(
            self.res_content_frame,
            text="",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            fg="#334155",
            wraplength=380,
            justify="left"
        )
        self.advice_label.pack(anchor="w", pady=(0, 4))

        self.healthy_range_label = tk.Label(
            self.res_content_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#2563EB",
            wraplength=380,
            justify="left"
        )
        self.healthy_range_label.pack(anchor="w")

        # -------------------------------------------------------------
        # 3. RIGHT COLUMN: SESSION HISTORY
        # -------------------------------------------------------------
        history_card = tk.LabelFrame(
            right_col,
            text=" 🕒 Session History ",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#1E293B",
            padx=10,
            pady=10,
            relief="solid",
            bd=1
        )
        history_card.pack(fill="both", expand=True)

        history_scroll = ttk.Scrollbar(history_card)
        history_scroll.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(
            history_card,
            font=("Segoe UI", 9),
            bg="#F8FAFC",
            fg="#1E293B",
            selectbackground="#E2E8F0",
            selectforeground="#0F172A",
            yscrollcommand=history_scroll.set,
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.history_listbox.pack(fill="both", expand=True)
        history_scroll.config(command=self.history_listbox.yview)

        clear_hist_btn = tk.Button(
            history_card,
            text="🗑️ Clear History",
            font=("Segoe UI", 9),
            bg="#F1F5F9",
            fg="#64748B",
            activebackground="#E2E8F0",
            relief="flat",
            pady=4,
            cursor="hand2",
            command=self.clear_history
        )
        clear_hist_btn.pack(fill="x", pady=(8, 0))

        # -------------------------------------------------------------
        # 4. FOOTER: HEALTH DISCLAIMER
        # -------------------------------------------------------------
        footer_frame = tk.Frame(self.root, bg="#F1F5F9", padx=16, pady=8)
        footer_frame.pack(fill="x", side="bottom")

        disclaimer_lbl = tk.Label(
            footer_frame,
            text=HEALTH_DISCLAIMER,
            font=("Segoe UI", 8),
            bg="#F1F5F9",
            fg="#64748B",
            wraplength=740,
            justify="center"
        )
        disclaimer_lbl.pack()

    # =========================================================================
    # EVENT HANDLERS & USER INTERACTIONS
    # =========================================================================

    def _on_unit_change(self):
        """Update entry labels and placeholder hints when switching units."""
        unit = self.unit_var.get()
        if unit == "Metric":
            self.height_label.config(text="Height (cm):")
            self.height_hint.config(text="e.g. 175 cm")
            self.weight_label.config(text="Weight (kg):")
            self.weight_hint.config(text="e.g. 70 kg")
        else:
            self.height_label.config(text="Height (in):")
            self.height_hint.config(text="e.g. 68 in (5'8\")")
            self.weight_label.config(text="Weight (lb):")
            self.weight_hint.config(text="e.g. 154 lb")
        
        # Clear inline error when switching unit
        self.error_label.config(text="")

    def calculate_result(self):
        """Handle calculation button click, input validation, and display."""
        self.error_label.config(text="")
        unit = self.unit_var.get()
        h_raw = self.height_entry.get()
        w_raw = self.weight_entry.get()

        is_valid, height, weight, err_msg = validate_input(h_raw, w_raw, unit)
        if not is_valid:
            self.error_label.config(text=f"❌ {err_msg}")
            messagebox.showwarning("Input Validation Error", err_msg)
            return

        try:
            if unit == "Metric":
                bmi = calculate_bmi_metric(weight, height)
                h_unit, w_unit = "cm", "kg"
            else:
                bmi = calculate_bmi_imperial(weight, height)
                h_unit, w_unit = "in", "lb"
                
            category, advice, color_hex = get_bmi_category(bmi)
            min_healthy_wt, max_healthy_wt = calculate_healthy_weight_range(height, unit)

            # Display Result
            self._display_result(bmi, category, advice, min_healthy_wt, max_healthy_wt, w_unit)

            # Add to Session History
            self.add_to_history(bmi, category, height, weight, unit, h_unit, w_unit)

        except Exception as ex:
            self.error_label.config(text=f"Calculation Error: {str(ex)}")
            messagebox.showerror("Error", f"An unexpected calculation error occurred: {str(ex)}")

    def _display_result(
        self,
        bmi: float,
        category: str,
        advice: str,
        min_wt: float,
        max_wt: float,
        w_unit: str
    ):
        """Render the calculated BMI and category inside the result card."""
        self.res_placeholder.pack_forget()
        self.res_content_frame.pack(fill="both", expand=True)

        self.bmi_display_val.config(text=f"{bmi:.1f}  (exact: {bmi:.2f})")
        
        # Color styling based on category
        cat_style = CATEGORY_COLORS.get(category, {"bg": "#F1F5F9", "fg": "#0F172A", "badge": "#2563EB"})
        self.category_badge.config(
            text=f"● {category}",
            bg=cat_style["bg"],
            fg=cat_style["fg"]
        )

        self.advice_label.config(text=f"💡 Advice: {advice}")
        self.healthy_range_label.config(
            text=f"🎯 Target Healthy Weight (BMI 18.5 - 24.9): {min_wt} - {max_wt} {w_unit}"
        )

    def add_to_history(
        self,
        bmi: float,
        category: str,
        height: float,
        weight: float,
        unit: str,
        h_unit: str,
        w_unit: str
    ):
        """Append calculation to session history listbox."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "bmi": bmi,
            "category": category,
            "height": f"{height} {h_unit}",
            "weight": f"{weight} {w_unit}",
            "unit": unit
        }
        self.history.insert(0, entry)
        
        # Listbox Format
        hist_text = f"[{timestamp}] BMI {bmi:.1f} ({category}) | {weight}{w_unit}, {height}{h_unit}"
        self.history_listbox.insert(0, hist_text)

    def clear_form(self):
        """Reset inputs, error status, and return result card to placeholder."""
        self.height_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.error_label.config(text="")
        
        self.res_content_frame.pack_forget()
        self.res_placeholder.pack(pady=24)
        self.height_entry.focus()

    def clear_history(self):
        """Clear the in-memory session history listbox."""
        self.history.clear()
        self.history_listbox.delete(0, tk.END)


# =============================================================================
# CLI / TERMINAL FALLBACK INTERFACE
# =============================================================================

def run_cli_mode():
    """Interactive command-line interface for terminal or headless environments."""
    print("=" * 60)
    print("       OASIS INFOBYTE — BMI CALCULATOR (CLI MODE)       ")
    print("=" * 60)
    print("Select Unit System:")
    print("1. Metric (Centimeters / Kilograms)")
    print("2. Imperial (Inches / Pounds)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    unit_system = "Metric" if choice != "2" else "Imperial"
    h_unit = "cm" if unit_system == "Metric" else "in"
    w_unit = "kg" if unit_system == "Metric" else "lb"
    
    print(f"\n[Selected: {unit_system} System]")
    h_str = input(f"Enter height ({h_unit}): ").strip()
    w_str = input(f"Enter weight ({w_unit}): ").strip()
    
    is_valid, height, weight, err = validate_input(h_str, w_str, unit_system)
    if not is_valid:
        print(f"\n❌ Validation Error: {err}")
        return
        
    if unit_system == "Metric":
        bmi = calculate_bmi_metric(weight, height)
    else:
        bmi = calculate_bmi_imperial(weight, height)
        
    category, advice, _ = get_bmi_category(bmi)
    min_wt, max_wt = calculate_healthy_weight_range(height, unit_system)
    
    print("\n" + "-" * 40)
    print(f"📊 BMI Result: {bmi:.1f} (Exact: {bmi:.2f})")
    print(f"🏷️  Category:   {category}")
    print(f"💡 Advice:     {advice}")
    print(f"🎯 Ideal Wt:   {min_wt} - {max_wt} {w_unit}")
    print("-" * 40)
    print(HEALTH_DISCLAIMER)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Application launcher with automatic GUI / CLI fallback."""
    if "--cli" in sys.argv:
        run_cli_mode()
        return

    try:
        root = tk.Tk()
        app = BMICalculatorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"[Note] Tkinter graphical interface not initialized ({e}). Falling back to CLI...")
        run_cli_mode()


if __name__ == "__main__":
    main()
