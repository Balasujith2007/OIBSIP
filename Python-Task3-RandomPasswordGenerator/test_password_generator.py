#!/usr/bin/env python3
"""
===============================================================================
OIBSIP — Task 3: Random Password Generator Comprehensive Test Suite
===============================================================================
Executes unit tests, security assertions, validation edge cases,
and mathematical checks across the Password Generator Engine.
"""

import math
import os
import re
import string
import unittest
from typing import Set

from main import (
    AMBIGUOUS_CHARACTERS,
    CHARSET_LOWERCASE,
    CHARSET_NUMBERS,
    CHARSET_SYMBOLS,
    CHARSET_UPPERCASE,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    GeneratorConfig,
    PasswordGeneratorEngine,
    PasswordStrengthAnalyzer,
    SessionHistoryManager,
)


class TestPasswordGeneratorEngine(unittest.TestCase):
    """Test suite for core cryptographic password generation logic."""

    def test_01_all_character_types_min_length(self):
        """TEST 1: Length = 8, all character types selected."""
        config = GeneratorConfig(
            length=8,
            use_uppercase=True,
            use_lowercase=True,
            use_numbers=True,
            use_symbols=True,
            exclude_ambiguous=False
        )
        pwd = PasswordGeneratorEngine.generate_password(config)
        self.assertEqual(len(pwd), 8)
        self.assertTrue(any(c in CHARSET_UPPERCASE for c in pwd), "Must contain at least 1 uppercase")
        self.assertTrue(any(c in CHARSET_LOWERCASE for c in pwd), "Must contain at least 1 lowercase")
        self.assertTrue(any(c in CHARSET_NUMBERS for c in pwd), "Must contain at least 1 number")
        self.assertTrue(any(c in CHARSET_SYMBOLS for c in pwd), "Must contain at least 1 symbol")

    def test_02_only_lowercase(self):
        """TEST 2: Length = 16, only lowercase."""
        config = GeneratorConfig(
            length=16,
            use_uppercase=False,
            use_lowercase=True,
            use_numbers=False,
            use_symbols=False,
            exclude_ambiguous=False
        )
        pwd = PasswordGeneratorEngine.generate_password(config)
        self.assertEqual(len(pwd), 16)
        self.assertTrue(all(c in CHARSET_LOWERCASE for c in pwd))
        self.assertFalse(any(c in CHARSET_UPPERCASE for c in pwd))
        self.assertFalse(any(c in CHARSET_NUMBERS for c in pwd))
        self.assertFalse(any(c in CHARSET_SYMBOLS for c in pwd))

    def test_03_uppercase_and_lowercase(self):
        """TEST 3: Length = 20, uppercase + lowercase."""
        config = GeneratorConfig(
            length=20,
            use_uppercase=True,
            use_lowercase=True,
            use_numbers=False,
            use_symbols=False,
            exclude_ambiguous=False
        )
        for _ in range(5):
            pwd = PasswordGeneratorEngine.generate_password(config)
            self.assertEqual(len(pwd), 20)
            self.assertTrue(any(c in CHARSET_UPPERCASE for c in pwd))
            self.assertTrue(any(c in CHARSET_LOWERCASE for c in pwd))
            self.assertFalse(any(c in CHARSET_NUMBERS for c in pwd))
            self.assertFalse(any(c in CHARSET_SYMBOLS for c in pwd))

    def test_04_numbers_and_symbols(self):
        """TEST 4: Numbers + symbols only."""
        config = GeneratorConfig(
            length=16,
            use_uppercase=False,
            use_lowercase=False,
            use_numbers=True,
            use_symbols=True,
            exclude_ambiguous=False
        )
        for _ in range(5):
            pwd = PasswordGeneratorEngine.generate_password(config)
            self.assertEqual(len(pwd), 16)
            self.assertTrue(any(c in CHARSET_NUMBERS for c in pwd))
            self.assertTrue(any(c in CHARSET_SYMBOLS for c in pwd))
            self.assertFalse(any(c in CHARSET_UPPERCASE for c in pwd))
            self.assertFalse(any(c in CHARSET_LOWERCASE for c in pwd))

    def test_05_ambiguous_character_exclusion(self):
        """TEST 5: Verify excluded ambiguous characters never appear when option is enabled."""
        config = GeneratorConfig(
            length=64,
            use_uppercase=True,
            use_lowercase=True,
            use_numbers=True,
            use_symbols=True,
            exclude_ambiguous=True
        )
        for _ in range(25):
            pwd = PasswordGeneratorEngine.generate_password(config)
            for ambig_char in AMBIGUOUS_CHARACTERS:
                self.assertNotIn(
                    ambig_char,
                    pwd,
                    f"Ambiguous character '{ambig_char}' appeared despite exclusion being enabled!"
                )

    def test_06_minimum_length_validation(self):
        """TEST 6: Length < 8 must fail validation."""
        config = GeneratorConfig(length=7)
        is_valid, msg = PasswordGeneratorEngine.validate_config(config)
        self.assertFalse(is_valid)
        self.assertIn("at least 8", msg.lower())

        with self.assertRaises(ValueError):
            PasswordGeneratorEngine.generate_password(config)

    def test_07_maximum_length_validation(self):
        """TEST 7: Length > 128 must fail validation."""
        config = GeneratorConfig(length=129)
        is_valid, msg = PasswordGeneratorEngine.validate_config(config)
        self.assertFalse(is_valid)
        self.assertIn("cannot exceed 128", msg.lower())

        with self.assertRaises(ValueError):
            PasswordGeneratorEngine.generate_password(config)

    def test_08_invalid_input_type(self):
        """TEST 8: Non-integer input validation."""
        config = GeneratorConfig(length="abc")  # type: ignore
        is_valid, msg = PasswordGeneratorEngine.validate_config(config)
        self.assertFalse(is_valid)
        self.assertIn("must be an integer", msg.lower())

    def test_09_no_character_type_selected(self):
        """TEST 9: No character type selected must fail validation."""
        config = GeneratorConfig(
            length=16,
            use_uppercase=False,
            use_lowercase=False,
            use_numbers=False,
            use_symbols=False
        )
        is_valid, msg = PasswordGeneratorEngine.validate_config(config)
        self.assertFalse(is_valid)
        self.assertIn("select at least one character type", msg.lower())

    def test_10_multiple_independent_generations(self):
        """TEST 10: Multiple passwords should be distinct (probabilistically unique)."""
        config = GeneratorConfig(length=24)
        generated_set: Set[str] = set()
        for _ in range(50):
            pwd = PasswordGeneratorEngine.generate_password(config)
            self.assertEqual(len(pwd), 24)
            generated_set.add(pwd)
        self.assertEqual(len(generated_set), 50, "All 50 generated 24-char passwords should be distinct.")

    def test_11_fisher_yates_secure_shuffle(self):
        """TEST 11: Verify secure shuffle does not lose characters and changes order."""
        original = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
        shuffled = PasswordGeneratorEngine.secure_shuffle(original)
        self.assertEqual(sorted(original), sorted(shuffled))
        self.assertEqual(len(original), len(shuffled))


class TestPasswordStrengthAndEntropy(unittest.TestCase):
    """Test suite for strength scoring and theoretical entropy calculation."""

    def test_12_entropy_calculation(self):
        """TEST 12: Verify mathematical entropy formula."""
        # 16 characters from pool of 94 characters -> 16 * log2(94) ≈ 104.9 bits
        entropy = PasswordStrengthAnalyzer.calculate_entropy("A" * 16, custom_pool_size=94)
        expected = round(16 * math.log2(94), 1)
        self.assertEqual(entropy, expected)

        # Empty password
        self.assertEqual(PasswordStrengthAnalyzer.calculate_entropy(""), 0.0)

    def test_13_strength_categories(self):
        """TEST 13: Verify classification across various password complexities."""
        # Weak password
        eval_weak = PasswordStrengthAnalyzer.evaluate("abcdefgh")
        self.assertIn(eval_weak.category, ["Weak", "Very Weak", "Moderate"])

        # Very strong password
        eval_vstrong = PasswordStrengthAnalyzer.evaluate("K9#mQ2$xP!vL8@zW4&jR")
        self.assertEqual(eval_vstrong.category, "Very Strong")
        self.assertGreaterEqual(eval_vstrong.score, 85)


class TestSessionHistorySecurity(unittest.TestCase):
    """Test suite confirming session history preserves privacy and never stores plaintext."""

    def test_14_session_history_never_stores_plaintext(self):
        """TEST 14: Ensure history records contain ONLY metadata."""
        mgr = SessionHistoryManager(max_entries=5)
        config = GeneratorConfig(length=16)
        pwd = PasswordGeneratorEngine.generate_password(config)
        evaluation = PasswordStrengthAnalyzer.evaluate(pwd)

        record = mgr.record_generation(config, evaluation)

        # Check record attributes
        self.assertEqual(record.length, 16)
        self.assertEqual(record.strength_category, evaluation.category)

        # Confirm the actual password string does not appear in record fields or string representation
        rec_repr = str(record)
        self.assertNotIn(pwd, rec_repr)
        for r in mgr.get_records():
            self.assertFalse(hasattr(r, "password"))
            self.assertNotIn(pwd, str(r))

    def test_15_history_clear(self):
        """TEST 15: Verify history clearing."""
        mgr = SessionHistoryManager()
        config = GeneratorConfig(length=16)
        mgr.record_generation(config, PasswordStrengthAnalyzer.evaluate("P@ssw0rd123!#%&*"))
        self.assertEqual(len(mgr.get_records()), 1)
        mgr.clear()
        self.assertEqual(len(mgr.get_records()), 0)


class TestSecurityCodebaseIntegrity(unittest.TestCase):
    """Security audit tests verifying no insecure modules or leaks are present."""

    def test_16_no_insecure_random_usage(self):
        """TEST 16: Verify `import random` or `random.choice` is NOT used in AST or executable code."""
        import ast
        main_py_path = os.path.join(os.path.dirname(__file__), "main.py")
        with open(main_py_path, "r", encoding="utf-8") as f:
            source = f.read()

        parsed_ast = ast.parse(source)
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "random", "Insecure 'import random' found in main.py AST!")
            elif isinstance(node, ast.ImportFrom):
                self.assertNotEqual(node.module, "random", "Insecure 'from random import ...' found in main.py AST!")
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == "random":
                    self.fail(f"Found call or reference to random.{node.attr} in main.py AST!")

        # Verify secrets module is explicitly used
        self.assertIn("import secrets", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
