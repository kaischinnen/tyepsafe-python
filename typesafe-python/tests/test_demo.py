import unittest
from unittest.mock import Mock, patch

from demo import run_match
from main import JevLib


class TestRunMatch(unittest.TestCase):
    def test_returns_and_prints_actual_team_name(self):
        jevlib = Mock(spec=JevLib)
        jevlib.match.return_value = "Returns Team"

        with patch("builtins.print") as print_mock:
            team = run_match(jevlib)

        self.assertEqual(team, "Returns Team")
        print_mock.assert_called_once_with("Route to: Returns Team")


if __name__ == "__main__":
    unittest.main()
