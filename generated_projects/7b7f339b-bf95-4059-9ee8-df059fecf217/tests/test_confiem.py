"""
Tests for confiem
"""

import pytest
from unittest.mock import patch
from confiem.core import confirm, confirm_yes_no, confirm_with_options


class TestConfirm:
    
    @patch('builtins.input', return_value='yes')
    def test_confirm_yes(self, mock_input):
        result = confirm("Test?")
        assert result is True
    
    @patch('builtins.input', return_value='no')
    def test_confirm_no(self, mock_input):
        result = confirm("Test?")
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_confirm_default_true(self, mock_input):
        result = confirm("Test?", default=True)
        assert result is True
    
    @patch('builtins.input', return_value='')
    def test_confirm_default_false(self, mock_input):
        result = confirm("Test?", default=False)
        assert result is False
    
    @patch('builtins.input', return_value='Y')
    def test_confirm_case_insensitive(self, mock_input):
        result = confirm("Test?", case_sensitive=False)
        assert result is True
    
    @patch('builtins.input', return_value='custom_yes')
    def test_confirm_custom_values(self, mock_input):
        result = confirm("Test?", yes_values=['custom_yes'], no_values=['custom_no'])
        assert result is True


class TestConfirmWithOptions:
    
    @patch('builtins.input', return_value='1')
    def test_select_by_number(self, mock_input):
        options = ['Option A', 'Option B', 'Option C']
        result = confirm_with_options("Choose:", options)
        assert result == 'Option A'
    
    @patch('builtins.input', return_value='opt')
    def test_select_by_partial_string(self, mock_input):
        options = ['Option A', 'Different B']
        result = confirm_with_options("Choose:", options)
        assert result == 'Option A'
    
    @patch('builtins.input', return_value='')
    def test_select_default(self, mock_input):
        options = ['Option A', 'Option B']
        result = confirm_with_options("Choose:", options, default=1)
        assert result == 'Option B'
    
    def test_empty_options_raises_error(self):
        with pytest.raises(ValueError):
            confirm_with_options("Choose:", [])


if __name__ == "__main__":
    pytest.main([__file__])