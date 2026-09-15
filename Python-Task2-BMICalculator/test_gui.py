"""
Verification script testing Tkinter GUI component behavior programmatically.
"""
import unittest
import tkinter as tk
from main import BMICalculatorApp, CATEGORY_NORMAL, CATEGORY_UNDERWEIGHT, CATEGORY_OVERWEIGHT, CATEGORY_OBESITY

class TestBMIGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide root during headless test
        self.app = BMICalculatorApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_gui_metric_calculation(self):
        # Set Metric
        self.app.unit_var.set("Metric")
        self.app._on_unit_change()

        # Enter height 175, weight 70
        self.app.height_entry.insert(0, "175")
        self.app.weight_entry.insert(0, "70")

        self.app.calculate_result()

        # Check Result Frame is active
        self.assertIn("22.9", self.app.bmi_display_val.cget("text"))
        self.assertIn(CATEGORY_NORMAL, self.app.category_badge.cget("text"))
        self.assertEqual(len(self.app.history), 1)
        self.assertEqual(self.app.history[0]["category"], CATEGORY_NORMAL)

    def test_gui_imperial_calculation(self):
        # Set Imperial
        self.app.unit_var.set("Imperial")
        self.app._on_unit_change()

        # Enter height 68, weight 154
        self.app.height_entry.insert(0, "68")
        self.app.weight_entry.insert(0, "154")

        self.app.calculate_result()

        self.assertIn("23.4", self.app.bmi_display_val.cget("text"))
        self.assertIn(CATEGORY_NORMAL, self.app.category_badge.cget("text"))
        self.assertEqual(len(self.app.history), 1)

    def test_gui_clear_form(self):
        self.app.height_entry.insert(0, "175")
        self.app.weight_entry.insert(0, "70")
        self.app.calculate_result()

        # Clear form
        self.app.clear_form()

        self.assertEqual(self.app.height_entry.get(), "")
        self.assertEqual(self.app.weight_entry.get(), "")
        self.assertEqual(self.app.error_label.cget("text"), "")

    def test_gui_clear_history(self):
        self.app.height_entry.insert(0, "175")
        self.app.weight_entry.insert(0, "70")
        self.app.calculate_result()
        self.assertEqual(len(self.app.history), 1)

        self.app.clear_history()
        self.assertEqual(len(self.app.history), 0)
        self.assertEqual(self.app.history_listbox.size(), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
