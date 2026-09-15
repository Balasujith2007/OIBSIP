# ⚖️ Oasis Infobyte SIP — Python Task 2: BMI Calculator

A modern, interactive, and beginner-friendly **Body Mass Index (BMI) Calculator** built with Python and Tkinter. This application supports dual unit systems (**Metric** and **Imperial**), real-time input validation, WHO-standard adult category classification, dynamic health recommendations, and session-based calculation history.

---

## 📌 Oasis Infobyte SIP Task Information

- **Internship Domain:** Python Programming Internship
- **Task No:** 2
- **Project Title:** BMI Calculator (Advanced Tier)
- **Developer:** Oasis Infobyte Intern

---

## 🎯 Objective

The primary objective of this project is to build a reliable, user-friendly, and robust desktop BMI calculation tool that allows users to:
1. Enter height and weight in their preferred unit system.
2. Calculate and display accurate BMI values with appropriate precision.
3. Automatically determine the corresponding WHO BMI category.
4. View personalized health suggestions and target healthy weight ranges.
5. Validate all user inputs safely without crashing.
6. Keep an in-memory session history for comparative tracking.

---

## ✨ Features

- **Dual Unit System Support**:
  - **Metric System**: Height in centimeters ($\text{cm}$), Weight in kilograms ($\text{kg}$).
  - **Imperial System**: Height in inches ($\text{in}$), Weight in pounds ($\text{lb}$).
- **Instant Category Classification**: Categorizes BMI into Underweight, Normal weight, Overweight, or Obesity with high-contrast color badges.
- **Healthy Weight Range Calculation**: Dynamically computes the target normal weight range ($\text{BMI } 18.5 - 24.9$) for the user's specific height.
- **Robust Input Validation**:
  - Checks for empty inputs, alphabetic strings, special characters, negative values, and zero.
  - Realistic range sanity guards (e.g., height between $40\text{--}280\text{ cm}$ / $15\text{--}110\text{ in}$).
  - Inline error feedback and dialog alerts.
- **Session-Only BMI History**:
  - Automatically records timestamp, BMI value, category, height, weight, and unit system.
  - Includes a quick one-click "Clear History" button.
- **Form Reset / Clear**: One-click clear button resets all fields, error states, and result cards.
- **Dual Mode Interface**:
  - **GUI Mode**: Rich, modern desktop interface using Python's `tkinter` and `ttk`.
  - **CLI Fallback Mode**: Interactive terminal mode for headless systems or command-line enthusiasts (`python main.py --cli`).

---

## 📐 BMI Mathematical Formulas

### 1. Metric Units
$$\text{Height (m)} = \frac{\text{Height (cm)}}{100}$$
$$\text{BMI} = \frac{\text{Weight (kg)}}{(\text{Height (m)})^2}$$

### 2. Imperial Units
$$\text{BMI} = \frac{703 \times \text{Weight (lb)}}{(\text{Height (in)})^2}$$

---

## 🏷️ BMI Categories (WHO Standard)

| BMI Range | Category | Badge Color | Health Guidance |
|---|---|---|---|
| **Below 18.5** | **Underweight** | 🔵 Blue (`#0284C7`) | Consider consulting a healthcare provider about balanced nutrition. |
| **18.5 – 24.9** | **Normal weight** | 🟢 Green (`#16A34A`) | Great job! Maintain your balanced diet and regular physical activity. |
| **25.0 – 29.9** | **Overweight** | 🟠 Amber (`#D97706`) | Engaging in regular exercise and a balanced diet can help reach a normal BMI. |
| **30.0 and above** | **Obesity** | 🔴 Red (`#DC2626`) | Consult a certified healthcare specialist or dietitian for guidance. |

---

## 🛠️ Technologies Used

- **Programming Language:** Python 3.8+
- **GUI Framework:** Tkinter & `ttk` (Standard Library)
- **Testing Framework:** `unittest` (Standard Library)
- **External Dependencies:** None (100% pure standard library)

---

## 📂 Project Structure

```text
OIBSIP/
├── Python-Task1-VoiceAssistant/
│   └── ... (Task 1 Files)
│
└── Python-Task2-BMICalculator/
    ├── main.py                  # Main application (Tkinter GUI + Core Logic + CLI mode)
    ├── test_bmi_calculator.py   # Comprehensive unit test suite (17 test cases)
    ├── test_gui.py              # Automated GUI interaction test runner
    ├── requirements.txt         # Project dependency declaration
    ├── README.md                # Detailed project documentation
    └── screenshots/             # Application UI demonstration captures
```

---

## 🚀 Installation & Requirements

### System Requirements
- Python **3.8** or higher installed on Windows, macOS, or Linux.
- Tkinter installed (bundled standard with Windows and macOS Python distributions).

### Installation
1. Clone or navigate to the project directory:
   ```bash
   cd Python-Task2-BMICalculator
   ```
2. Verify Python version:
   ```bash
   python --version
   ```

---

## 💻 How to Run

### Run Graphical User Interface (Default):
```bash
python main.py
```

### Run Command-Line Interface (CLI Mode):
```bash
python main.py --cli
```

### Run Automated Unit Tests:
```bash
python test_bmi_calculator.py
```

### Run Automated GUI Tests:
```bash
python test_gui.py
```

---

## 📖 How to Use the GUI

1. **Select Unit System**: Choose either **Metric (cm / kg)** or **Imperial (in / lb)** using the radio buttons.
2. **Enter Height**: Input your height (e.g. `175` for cm or `68` for inches).
3. **Enter Weight**: Input your weight (e.g. `70` for kg or `154` for pounds).
4. **Calculate**: Click **⚡ Calculate BMI** (or press `Enter` on your keyboard).
5. **Review Result**:
   - The exact and rounded BMI score will appear with a color-coded category badge.
   - Read the actionable lifestyle guidance and recommended target weight range.
   - The calculation is automatically saved to the **Session History** panel on the right.
6. **Reset / Clear**: Click **🔄 Clear Form** to start a new calculation.

---

## 🧪 Example Calculations & Verified Test Cases

| Test Case | Unit System | Height | Weight | Calculated BMI | Category | Expected Outcome |
|---|---|---|---|---|---|---|
| **Test 1** | Metric | `175 cm` | `70 kg` | `22.9` (22.86) | **Normal weight** | ✅ Passed |
| **Test 2** | Metric | `170 cm` | `50 kg` | `17.3` (17.30) | **Underweight** | ✅ Passed |
| **Test 3** | Metric | `170 cm` | `80 kg` | `27.7` (27.68) | **Overweight** | ✅ Passed |
| **Test 4** | Metric | `170 cm` | `100 kg` | `34.6` (34.60) | **Obesity** | ✅ Passed |
| **Test 5** | Imperial | `68 in` | `154 lb` | `23.4` (23.41) | **Normal weight** | ✅ Passed |
| **Test 6** | Imperial | `66 in` | `100 lb` | `16.1` (16.14) | **Underweight** | ✅ Passed |
| **Test 7** | Imperial | `68 in` | `180 lb` | `27.4` (27.37) | **Overweight** | ✅ Passed |
| **Test 8** | Imperial | `66 in` | `220 lb` | `35.5` (35.51) | **Obesity** | ✅ Passed |

---

## 🛡️ Input Validation & Error Handling

The application protects against crashes through exhaustive validation checks:
- **Blank Fields**: Notifies user to enter height and weight.
- **Alphabetic / Non-numeric**: Prevents character inputs and highlights numeric format requirements.
- **Zero or Negative Numbers**: Rejects non-positive height/weight.
- **Extreme Outliers**: Alerts if values exceed realistic human thresholds ($40\text{--}280\text{ cm}$ / $10\text{--}500\text{ kg}$).

---

## 🕒 Session History

The session history records all calculations performed while the app remains open:
```text
[21:14:02] BMI 22.9 (Normal weight) | 70.0kg, 175.0cm
[21:14:15] BMI 27.7 (Overweight)    | 80.0kg, 170.0cm
[21:14:30] BMI 17.3 (Underweight)   | 50.0kg, 170.0cm
```
*Note: History is kept in memory during the runtime session and does not store personal health data permanently on disk.*

---

## ⚠️ Health Disclaimer

> **⚠️ Disclaimer:** Body Mass Index (BMI) is a general screening indicator and does not replace professional medical diagnosis, advice, or comprehensive body composition assessment (such as muscle vs. fat ratio). Always consult a certified healthcare professional for personalized medical guidance.

---

## 🔮 Future Improvements

- [ ] Export session history to CSV / PDF summary report.
- [ ] Add Waist-to-Height Ratio (WHtR) and Body Fat Percentage estimation calculators.
- [ ] Dark Mode toggle in GUI.
- [ ] Multi-language localization support.

---

## 📜 License

This project was developed for the **Oasis Infobyte Internship Program (OIBSIP)** under the Python Programming track.
