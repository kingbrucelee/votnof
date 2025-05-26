import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
from src.utils import file_operations

# Mock file path
MOCK_WATCHED_PRINTS_FILE = "data/test_watched_prints.json"


class TestFileOperations(unittest.TestCase):

    def setUp(self):
        """Set up for each test, ensuring a clean state for watched_prints."""
        file_operations.watched_prints.clear()

    @patch("src.utils.file_operations.WATCHED_PRINTS_FILE", MOCK_WATCHED_PRINTS_FILE)
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_load_watched_prints_existing_file(
        self, mock_json_load, mock_file_open, mock_os_path_exists
    ):
        """Test loading watched prints from an existing file."""
        mock_os_path_exists.return_value = True
        loaded_data = {"123": {"print_a": "2023-01-01"}}
        mock_json_load.return_value = loaded_data

        result = file_operations.load_watched_prints()

        mock_os_path_exists.assert_called_once_with(MOCK_WATCHED_PRINTS_FILE)
        mock_file_open.assert_called_once_with(MOCK_WATCHED_PRINTS_FILE, "r")
        mock_json_load.assert_called_once()
        self.assertEqual(result, loaded_data)
        self.assertEqual(file_operations.watched_prints, loaded_data)

    @patch("src.utils.file_operations.WATCHED_PRINTS_FILE", MOCK_WATCHED_PRINTS_FILE)
    @patch("os.path.exists")
    def test_load_watched_prints_no_file(self, mock_os_path_exists):
        """Test loading watched prints when no file exists."""
        mock_os_path_exists.return_value = False

        result = file_operations.load_watched_prints()

        mock_os_path_exists.assert_called_once_with(MOCK_WATCHED_PRINTS_FILE)
        self.assertEqual(result, {})
        self.assertEqual(file_operations.watched_prints, {})

    @patch("src.utils.file_operations.WATCHED_PRINTS_FILE", MOCK_WATCHED_PRINTS_FILE)
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_watched_prints(
        self, mock_json_dump, mock_file_open, mock_os_makedirs
    ):
        """Test saving watched prints to a file."""
        initial_data = {"456": {"print_b": "2023-02-01"}}
        file_operations.watched_prints.update(initial_data)

        file_operations.save_watched_prints()

        mock_os_makedirs.assert_called_once_with(
            os.path.dirname(MOCK_WATCHED_PRINTS_FILE), exist_ok=True
        )
        mock_file_open.assert_called_once_with(MOCK_WATCHED_PRINTS_FILE, "w")
        mock_json_dump.assert_called_once_with(initial_data, mock_file_open())

    @patch("src.utils.file_operations.load_watched_prints")
    def test_get_watched_prints_empty_and_loads(self, mock_load_watched_prints):
        """Test get_watched_prints when watched_prints is empty, ensuring it calls load."""
        loaded_data = {"user1": {"p1": "date1"}}

        def side_effect_load():
            file_operations.watched_prints.update(loaded_data)
            return loaded_data

        mock_load_watched_prints.side_effect = side_effect_load

        result = file_operations.get_watched_prints()

        mock_load_watched_prints.assert_called_once()
        self.assertEqual(result, loaded_data)
        self.assertEqual(file_operations.watched_prints, loaded_data)

    @patch("src.utils.file_operations.load_watched_prints")
    def test_get_watched_prints_not_empty(self, mock_load_watched_prints):
        """Test get_watched_prints when watched_prints is already populated."""
        initial_data = {"user2": {"p2": "date2"}}
        file_operations.watched_prints.update(initial_data)

        result = file_operations.get_watched_prints()

        mock_load_watched_prints.assert_not_called()
        self.assertEqual(result, initial_data)
        self.assertEqual(file_operations.watched_prints, initial_data)

    @patch("src.utils.file_operations.save_watched_prints")
    def test_add_watched_print_new_user_new_print(self, mock_save_watched_prints):
        """Test adding a new watched print for a new user."""
        user_id = 1
        print_nr = "print_c"
        change_date = "2023-03-01"

        file_operations.add_watched_print(user_id, print_nr, change_date)

        self.assertEqual(
            file_operations.watched_prints, {"1": {"print_c": "2023-03-01"}}
        )
        mock_save_watched_prints.assert_called_once()

    @patch("src.utils.file_operations.save_watched_prints")
    def test_add_watched_print_existing_user_new_print(self, mock_save_watched_prints):
        """Test adding a new watched print for an existing user."""
        file_operations.watched_prints.update({"1": {"print_c": "2023-03-01"}})
        user_id = 1
        print_nr = "print_d"
        change_date = "2023-04-01"

        file_operations.add_watched_print(user_id, print_nr, change_date)

        self.assertEqual(
            file_operations.watched_prints,
            {"1": {"print_c": "2023-03-01", "print_d": "2023-04-01"}},
        )
        mock_save_watched_prints.assert_called_once()

    @patch("src.utils.file_operations.save_watched_prints")
    def test_remove_watched_print_success(self, mock_save_watched_prints):
        """Test removing an existing watched print successfully."""
        initial_data = {"1": {"print_e": "2023-05-01", "print_f": "2023-06-01"}}
        file_operations.watched_prints.update(initial_data)
        user_id = 1
        print_nr = "print_e"

        file_operations.remove_watched_print(user_id, print_nr)

        expected_data = {"1": {"print_f": "2023-06-01"}}
        self.assertEqual(file_operations.watched_prints, expected_data)
        mock_save_watched_prints.assert_called_once()

    @patch("src.utils.file_operations.save_watched_prints")
    def test_remove_watched_print_user_not_found(self, mock_save_watched_prints):
        """Test removing a print when the user is not found."""
        initial_data = {"2": {"print_g": "2023-07-01"}}
        file_operations.watched_prints.update(initial_data)
        user_id = 1
        print_nr = "print_e"

        file_operations.remove_watched_print(user_id, print_nr)

        self.assertEqual(file_operations.watched_prints, initial_data)
        mock_save_watched_prints.assert_not_called()

    @patch("src.utils.file_operations.save_watched_prints")
    def test_remove_watched_print_print_not_found(self, mock_save_watched_prints):
        """Test removing a print when the print number is not found for the user."""
        initial_data = {"1": {"print_e": "2023-05-01"}}
        file_operations.watched_prints.update(initial_data)
        user_id = 1
        print_nr = "print_h"

        file_operations.remove_watched_print(user_id, print_nr)

        self.assertEqual(file_operations.watched_prints, initial_data)
        mock_save_watched_prints.assert_not_called()

    @patch("src.utils.file_operations.save_watched_prints")
    def test_update_print_change_date_success(self, mock_save_watched_prints):
        """Test updating the change date for an existing watched print."""
        initial_data = {"1": {"print_i": "2023-09-01"}}
        file_operations.watched_prints.update(initial_data)
        user_id = 1
        print_nr = "print_i"
        new_date = "2023-10-01"

        file_operations.update_print_change_date(user_id, print_nr, new_date)

        expected_data = {"1": {"print_i": "2023-10-01"}}
        self.assertEqual(file_operations.watched_prints, expected_data)
        mock_save_watched_prints.assert_called_once()

    @patch("src.utils.file_operations.save_watched_prints")
    def test_update_print_change_date_user_not_found(self, mock_save_watched_prints):
        """Test updating date when user is not found."""
        initial_data = {"2": {"print_j": "2023-11-01"}}
        file_operations.watched_prints.update(initial_data)
        user_id = 1
        print_nr = "print_i"
        new_date = "2023-10-01"

        file_operations.update_print_change_date(user_id, print_nr, new_date)

        self.assertEqual(file_operations.watched_prints, initial_data)
        mock_save_watched_prints.assert_not_called()

    @patch("src.utils.file_operations.save_watched_prints")
    def test_update_print_change_date_print_not_found(self, mock_save_watched_prints):
        """Test updating date when print number is not found for the user."""
        initial_data = {"1": {"print_i": "2023-09-01"}}
        file_operations.watched_prints.update(initial_data)
        user_id = 1
        print_nr = "print_k"
        new_date = "2023-10-01"

        file_operations.update_print_change_date(user_id, print_nr, new_date)

        self.assertEqual(file_operations.watched_prints, initial_data)
        mock_save_watched_prints.assert_not_called()

    # Modified tests for get_user_watched_prints
    def test_get_user_watched_prints_existing_user(self):
        """Test retrieving watched prints for an existing user."""
        file_operations.watched_prints.update(
            {"1": {"print_l": "2023-12-01", "print_m": "2024-01-01"}}
        )
        user_id = 1

        result = file_operations.get_user_watched_prints(user_id)

        self.assertEqual(result, {"print_l": "2023-12-01", "print_m": "2024-01-01"})
        self.assertEqual(
            file_operations.watched_prints,
            {"1": {"print_l": "2023-12-01", "print_m": "2024-01-01"}},
        )

    def test_get_user_watched_prints_non_existing_user(self):
        """Test retrieving watched prints for a non-existing user."""
        file_operations.watched_prints.update({"2": {"print_n": "2024-02-01"}})
        user_id = 1

        result = file_operations.get_user_watched_prints(user_id)

        self.assertEqual(result, {})
        self.assertEqual(
            file_operations.watched_prints, {"2": {"print_n": "2024-02-01"}}
        )


if __name__ == "__main__":
    unittest.main()
