"""
=============================================================================
 Oasis Infobyte SIP — Python Programming Internship
 Task 2: BMI Calculator Automated Test Suite
=============================================================================
"""

import unittest
from main import (
    calculate_bmi_metric,
    calculate_bmi_imperial,
    get_bmi_category,
    calculate_healthy_weight_range,
    validate_input,
    CATEGORY_UNDERWEIGHT,
    CATEGORY_NORMAL,
    CATEGORY_OVERWEIGHT,
    CATEGORY_OBESITY
)


class TestBMICalculator(unittest.TestCase):
    """Unit tests for BMI calculations, categories, and input validation."""

    # -------------------------------------------------------------------------
    # 1. CORE FORMULA TESTS (METRIC)
    # -------------------------------------------------------------------------
    def test_metric_calculation_normal(self):
        """Test standard normal metric calculation (70kg, 175cm -> 22.86)."""
        bmi = calculate_bmi_metric(weight_kg=70, height_cm=175)
        self.assertAlmostEqual(bmi, 22.86, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_NORMAL)

    def test_metric_calculation_underweight(self):
        """Test underweight metric calculation (50kg, 170cm -> 17.30)."""
        bmi = calculate_bmi_metric(weight_kg=50, height_cm=170)
        self.assertAlmostEqual(bmi, 17.30, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_UNDERWEIGHT)

    def test_metric_calculation_overweight(self):
        """Test overweight metric calculation (80kg, 170cm -> 27.68)."""
        bmi = calculate_bmi_metric(weight_kg=80, height_cm=170)
        self.assertAlmostEqual(bmi, 27.68, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_OVERWEIGHT)

    def test_metric_calculation_obese(self):
        """Test obesity metric calculation (100kg, 170cm -> 34.60)."""
        bmi = calculate_bmi_metric(weight_kg=100, height_cm=170)
        self.assertAlmostEqual(bmi, 34.60, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_OBESITY)

    # -------------------------------------------------------------------------
    # 2. CORE FORMULA TESTS (IMPERIAL)
    # -------------------------------------------------------------------------
    def test_imperial_calculation_normal(self):
        """Test standard imperial calculation (154 lb, 68 in -> 23.41)."""
        bmi = calculate_bmi_imperial(weight_lb=154, height_in=68)
        self.assertAlmostEqual(bmi, 23.41, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_NORMAL)

    def test_imperial_calculation_underweight(self):
        """Test imperial underweight calculation (100 lb, 66 in -> 16.14)."""
        bmi = calculate_bmi_imperial(weight_lb=100, height_in=66)
        self.assertAlmostEqual(bmi, 16.14, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_UNDERWEIGHT)

    def test_imperial_calculation_overweight(self):
        """Test imperial overweight calculation (180 lb, 68 in -> 27.36)."""
        bmi = calculate_bmi_imperial(weight_lb=180, height_in=68)
        self.assertAlmostEqual(bmi, 27.37, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_OVERWEIGHT)

    def test_imperial_calculation_obese(self):
        """Test imperial obesity calculation (220 lb, 66 in -> 35.51)."""
        bmi = calculate_bmi_imperial(weight_lb=220, height_in=66)
        self.assertAlmostEqual(bmi, 35.51, places=2)
        category, _, _ = get_bmi_category(bmi)
        self.assertEqual(category, CATEGORY_OBESITY)

    # -------------------------------------------------------------------------
    # 3. CATEGORY BOUNDARY TESTS
    # -------------------------------------------------------------------------
    def test_category_boundaries(self):
        """Test boundary thresholds: 18.49, 18.5, 24.9, 25.0, 29.9, 30.0."""
        self.assertEqual(get_bmi_category(18.4)[0], CATEGORY_UNDERWEIGHT)
        self.assertEqual(get_bmi_category(18.5)[0], CATEGORY_NORMAL)
        self.assertEqual(get_bmi_category(24.9)[0], CATEGORY_NORMAL)
        self.assertEqual(get_bmi_category(25.0)[0], CATEGORY_OVERWEIGHT)
        self.assertEqual(get_bmi_category(29.9)[0], CATEGORY_OVERWEIGHT)
        self.assertEqual(get_bmi_category(30.0)[0], CATEGORY_OBESITY)
        self.assertEqual(get_bmi_category(42.5)[0], CATEGORY_OBESITY)

    # -------------------------------------------------------------------------
    # 4. INPUT VALIDATION TESTS
    # -------------------------------------------------------------------------
    def test_validate_valid_metric(self):
        valid, h, w, err = validate_input("175", "70", "Metric")
        self.assertTrue(valid)
        self.assertEqual(h, 175.0)
        self.assertEqual(w, 70.0)
        self.assertEqual(err, "")

    def test_validate_valid_imperial(self):
        valid, h, w, err = validate_input("68.5", "154.2", "Imperial")
        self.assertTrue(valid)
        self.assertEqual(h, 68.5)
        self.assertEqual(w, 154.2)
        self.assertEqual(err, "")

    def test_validate_empty_inputs(self):
        valid, _, _, err = validate_input("", "", "Metric")
        self.assertFalse(valid)
        self.assertIn("enter your height and weight", err)

        valid, _, _, err = validate_input("175", "", "Metric")
        self.assertFalse(valid)
        self.assertIn("enter your weight", err)

        valid, _, _, err = validate_input("", "70", "Metric")
        self.assertFalse(valid)
        self.assertIn("enter your height", err)

    def test_validate_alphabetic_inputs(self):
        valid, _, _, err = validate_input("abc", "70", "Metric")
        self.assertFalse(valid)
        self.assertIn("valid number", err)

        valid, _, _, err = validate_input("175", "xyz", "Metric")
        self.assertFalse(valid)
        self.assertIn("valid number", err)

    def test_validate_zero_and_negative(self):
        valid, _, _, err = validate_input("0", "70", "Metric")
        self.assertFalse(valid)
        self.assertIn("greater than zero", err)

        valid, _, _, err = validate_input("-175", "70", "Metric")
        self.assertFalse(valid)
        self.assertIn("greater than zero", err)

        valid, _, _, err = validate_input("175", "0", "Metric")
        self.assertFalse(valid)
        self.assertIn("greater than zero", err)

        valid, _, _, err = validate_input("175", "-50", "Metric")
        self.assertFalse(valid)
        self.assertIn("greater than zero", err)

    def test_validate_unrealistic_bounds(self):
        # Metric extremes
        valid, _, _, err = validate_input("350", "70", "Metric")
        self.assertFalse(valid)
        self.assertIn("realistic height", err)

        valid, _, _, err = validate_input("175", "800", "Metric")
        self.assertFalse(valid)
        self.assertIn("realistic weight", err)

        # Imperial extremes
        valid, _, _, err = validate_input("150", "150", "Imperial")
        self.assertFalse(valid)
        self.assertIn("realistic height", err)

        valid, _, _, err = validate_input("68", "1500", "Imperial")
        self.assertFalse(valid)
        self.assertIn("realistic weight", err)

    # -------------------------------------------------------------------------
    # 5. HEALTHY WEIGHT RANGE TESTS
    # -------------------------------------------------------------------------
    def test_healthy_weight_range_metric(self):
        min_wt, max_wt = calculate_healthy_weight_range(175, "Metric")
        # 1.75^2 = 3.0625. Min = 18.5 * 3.0625 = 56.66kg, Max = 24.9 * 3.0625 = 76.26kg
        self.assertAlmostEqual(min_wt, 56.7, places=1)
        self.assertAlmostEqual(max_wt, 76.3, places=1)

    def test_healthy_weight_range_imperial(self):
        min_wt, max_wt = calculate_healthy_weight_range(68, "Imperial")
        # 68^2 = 4624. Min = (18.5 * 4624)/703 = 121.7 lb, Max = (24.9 * 4624)/703 = 163.8 lb
        self.assertAlmostEqual(min_wt, 121.7, places=1)
        self.assertAlmostEqual(max_wt, 163.8, places=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
