#!/usr/bin/env python3
"""
===============================================================================
OIBSIP — Task 3: Tkinter GUI Component & Action Test Suite
===============================================================================
Programmatically instantiates the Tkinter interface, simulates button clicks,
input manipulation, and verifies widget state updates and clipboard functions.
"""

import sys
import tkinter as tk
import unittest

from main import (
    DEFAULT_PASSWORD_LENGTH,
    GeneratorConfig,
    PasswordGeneratorApp,
    PasswordGeneratorEngine,
)


class TestTkinterGUI(unittest.TestCase):
    """Verifies GUI widgets, event handlers, and data bindings."""

    def setUp(self):
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Keep hidden during automated test runs
            self.app = PasswordGeneratorApp(self.root)
        except tk.TclError:
            self.skipTest("Tkinter display environment unavailable for GUI tests.")

    def tearDown(self):
        if hasattr(self, "root") and self.root:
            try:
                self.root.destroy()
            except Exception:
                pass

    def test_gui_initial_state(self):
        """Verify GUI loads with initial generated password and expected defaults."""
        self.assertEqual(self.app.length_var.get(), DEFAULT_PASSWORD_LENGTH)
        self.assertTrue(self.app.upper_var.get())
        self.assertTrue(self.app.lower_var.get())
        self.assertTrue(self.app.num_var.get())
        self.assertTrue(self.app.sym_var.get())
        self.assertFalse(self.app.ambiguous_var.get())
        self.assertEqual(len(self.app.current_password), DEFAULT_PASSWORD_LENGTH)

    def test_gui_visibility_toggle(self):
        """Verify password masking and unmasking."""
        self.assertFalse(self.app.is_password_visible)
        self.assertEqual(self.app.password_entry.get(), "•" * len(self.app.current_password))

        # Toggle to show
        self.app._toggle_visibility()
        self.assertTrue(self.app.is_password_visible)
        self.assertEqual(self.app.password_entry.get(), self.app.current_password)

        # Toggle to hide
        self.app._toggle_visibility()
        self.assertFalse(self.app.is_password_visible)
        self.assertEqual(self.app.password_entry.get(), "•" * len(self.app.current_password))

    def test_gui_length_preset_change(self):
        """Verify preset buttons update the password length and generate new password."""
        self.app._set_length_preset(32)
        self.assertEqual(self.app.length_var.get(), 32)
        self.assertEqual(len(self.app.current_password), 32)

    def test_gui_clear_action(self):
        """Verify clear button clears password entry and metrics."""
        self.app._clear_interface()
        self.assertEqual(self.app.current_password, "")
        self.assertEqual(self.app.password_entry.get(), "")
        self.assertIn("Cleared", self.app.strength_lbl.cget("text"))

    def test_gui_copy_to_clipboard(self):
        """Verify copy to clipboard action."""
        self.app._set_length_preset(24)
        active_pwd = self.app.current_password
        self.app._copy_to_clipboard()
        clipboard_content = self.root.clipboard_get()
        self.assertEqual(clipboard_content, active_pwd)
        self.assertEqual(self.app.status_feedback_lbl.cget("text"), "✓ Copied to clipboard!")

    def test_gui_history_integration(self):
        """Verify session history updates when passwords are generated."""
        self.app._set_length_preset(20)
        self.app._set_length_preset(28)
        records = self.app.history_mgr.get_records()
        self.assertGreaterEqual(len(records), 2)
        self.assertEqual(records[0].length, 28)
        self.assertEqual(records[1].length, 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
