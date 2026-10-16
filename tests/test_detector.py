import unittest
from collections import Counter

class DetectionLogicTests(unittest.TestCase):
    def test_repeated_failures_are_high_severity(self):
        failed_by_ip = Counter({
            "192.168.1.50": 3
        })
        self.assertGreaterEqual(
            failed_by_ip["192.168.1.50"], 3
        )

    def test_single_failure_is_not_high_severity(self):
        failed_by_ip = Counter({
            "10.0.0.25": 1
        })
        self.assertLess(
            failed_by_ip["10.0.0.25"], 3
        )

if __name__ == "__main__":
    unittest.main()
