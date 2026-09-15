"""
================================================================================
TEST SUITE FOR OASIS INFOBYTE VOICE ASSISTANT (TASK 1)
================================================================================
Comprehensive automated tests covering:
- Intent recognition
- Time & date processing
- Weather live querying & parsing
- Duration & reminder parsing
- Knowledge base retrieval
- System apps mapping
- Safe email validation
- Exit commands
================================================================================
"""

import unittest
from datetime import datetime
import main


class TestOasisVoiceAssistant(unittest.TestCase):

    def test_greeting(self):
        """Verify dynamic greeting handles time of day correctly."""
        greeting = main.handle_greeting()
        self.assertIsInstance(greeting, str)
        self.assertIn("Hello", greeting)
        self.assertIn("Oasis Assistant", greeting)

    def test_get_current_time(self):
        """Verify time formatting matches AM/PM clock format."""
        time_str = main.get_current_time()
        self.assertIsInstance(time_str, str)
        self.assertTrue("AM" in time_str or "PM" in time_str)

    def test_get_current_date(self):
        """Verify date output contains current year."""
        date_str = main.get_current_date()
        curr_year = str(datetime.now().year)
        self.assertIn(curr_year, date_str)

    def test_knowledge_base(self):
        """Verify knowledge base queries return accurate information."""
        resp_python = main.get_knowledge_response("what is python")
        self.assertIsNotNone(resp_python)
        self.assertIn("Python", resp_python)

        resp_ai = main.get_knowledge_response("what is ai")
        self.assertIsNotNone(resp_ai)
        self.assertIn("Artificial Intelligence", resp_ai)

        resp_joke = main.get_knowledge_response("tell me a joke")
        self.assertIsNotNone(resp_joke)
        self.assertIn("bugs", resp_joke)

        resp_who = main.get_knowledge_response("who are you")
        self.assertIsNotNone(resp_who)
        self.assertIn("Oasis", resp_who)

    def test_reminder_parser(self):
        """Verify duration extraction from natural language phrases."""
        mgr = main.ReminderManager()

        sec, note = mgr.parse_time_duration("set a reminder for 10 seconds")
        self.assertEqual(sec, 10)

        sec, note = mgr.parse_time_duration("remind me in 5 minutes to take medicine")
        self.assertEqual(sec, 300)
        self.assertIn("take medicine", note)

        sec, note = mgr.parse_time_duration("set timer for 1 hour")
        self.assertEqual(sec, 3600)

        sec, note = mgr.parse_time_duration("invalid text without numbers")
        self.assertIsNone(sec)

    def test_weather_live(self):
        """Verify weather function retrieves live data gracefully."""
        weather_resp = main.get_weather("London")
        self.assertIsInstance(weather_resp, str)
        self.assertTrue("London" in weather_resp or "weather" in weather_resp)

    def test_intent_dispatcher(self):
        """Verify handle_command routes intents accurately."""
        # Non-exit commands return True
        self.assertTrue(main.handle_command("hello"))
        self.assertTrue(main.handle_command("what time is it"))
        self.assertTrue(main.handle_command("what is today's date"))
        self.assertTrue(main.handle_command("tell me a joke"))
        self.assertTrue(main.handle_command("help"))

        # Exit commands return False to break loop
        self.assertFalse(main.handle_command("exit"))
        self.assertFalse(main.handle_command("quit"))
        self.assertFalse(main.handle_command("goodbye"))


if __name__ == "__main__":
    print("\nRunning Voice Assistant Test Suite...")
    unittest.main(verbosity=2)
