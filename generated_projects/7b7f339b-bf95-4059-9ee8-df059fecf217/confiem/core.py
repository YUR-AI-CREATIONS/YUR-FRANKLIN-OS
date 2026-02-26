"""
Core confirmation functions
"""

import sys
from typing import List, Optional, Union


def confirm(
    message: str = "Do you want to continue?",
    default: Optional[bool] = None,
    yes_values: List[str] = None,
    no_values: List[str] = None,
    case_sensitive: bool = False
) -> bool:
    """
    Get user confirmation with customizable yes/no values.
    
    Args:
        message: The confirmation message to display
        default: Default value if user just presses enter (True/False/None)
        yes_values: List of strings that represent "yes"
        no_values: List of strings that represent "no"
        case_sensitive: Whether the input should be case sensitive
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    if yes_values is None:
        yes_values = ['y', 'yes', 'true', '1']
    if no_values is None:
        no_values = ['n', 'no', 'false', '0']
    
    # Prepare the prompt suffix
    if default is True:
        suffix = " [Y/n]: "
    elif default is False:
        suffix = " [y/N]: "
    else:
        suffix = " [y/n]: "
    
    while True:
        try:
            response = input(message + suffix).strip()
            
            if not response:
                if default is not None:
                    return default
                else:
                    print("Please enter a valid response.")
                    continue
            
            if not case_sensitive:
                response = response.lower()
                yes_values = [v.lower() for v in yes_values]
                no_values = [v.lower() for v in no_values]
            
            if response in yes_values:
                return True
            elif response in no_values:
                return False
            else:
                valid_options = yes_values + no_values
                print(f"Please enter one of: {', '.join(valid_options)}")
                
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return False


def confirm_yes_no(message: str = "Continue?", default: Optional[bool] = None) -> bool:
    """
    Simple yes/no confirmation.
    
    Args:
        message: The confirmation message
        default: Default value if user just presses enter
    
    Returns:
        bool: True for yes, False for no
    """
    return confirm(message, default)


def confirm_with_options(
    message: str,
    options: List[str],
    default: Optional[int] = None,
    case_sensitive: bool = False
) -> str:
    """
    Get user confirmation from a list of options.
    
    Args:
        message: The confirmation message
        options: List of available options
        default: Index of default option (0-based)
        case_sensitive: Whether matching should be case sensitive
    
    Returns:
        str: The selected option
    """
    if not options:
        raise ValueError("Options list cannot be empty")
    
    # Display options
    print(message)
    for i, option in enumerate(options):
        prefix = f"  {i + 1}. "
        if default is not None and i == default:
            prefix += f"[{option}]"
        else:
            prefix += option
        print(prefix)
    
    while True:
        try:
            if default is not None:
                prompt = f"Choose (1-{len(options)}) [{default + 1}]: "
            else:
                prompt = f"Choose (1-{len(options)}): "
            
            response = input(prompt).strip()
            
            if not response and default is not None:
                return options[default]
            
            # Try to parse as number
            try:
                choice_num = int(response)
                if 1 <= choice_num <= len(options):
                    return options[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
                    continue
            except ValueError:
                pass
            
            # Try to match by string
            if not case_sensitive:
                response = response.lower()
                search_options = [(opt.lower(), opt) for opt in options]
            else:
                search_options = [(opt, opt) for opt in options]
            
            matches = [original for search, original in search_options if search.startswith(response)]
            
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"Ambiguous choice. Matches: {', '.join(matches)}")
            else:
                print("Invalid choice. Please try again.")
                
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(1)