"""
Command line interface for confiem
"""

import argparse
import sys
from typing import List

from .core import confirm, confirm_with_options


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Confiem - Interactive confirmation utility",
        prog="confiem"
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        default="Do you want to continue?",
        help="Confirmation message to display"
    )
    
    parser.add_argument(
        "--default",
        choices=["yes", "no"],
        help="Default choice if user presses enter"
    )
    
    parser.add_argument(
        "--options",
        nargs="+",
        help="List of options to choose from"
    )
    
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Make input case sensitive"
    )
    
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if answer is no/false"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="confiem 1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        if args.options:
            # Multi-option mode
            result = confirm_with_options(
                args.message,
                args.options,
                case_sensitive=args.case_sensitive
            )
            print(f"Selected: {result}")
        else:
            # Yes/no mode
            default_bool = None
            if args.default == "yes":
                default_bool = True
            elif args.default == "no":
                default_bool = False
            
            result = confirm(
                args.message,
                default=default_bool,
                case_sensitive=args.case_sensitive
            )
            
            if result:
                print("Confirmed: Yes")
                sys.exit(0)
            else:
                print("Confirmed: No")
                if args.exit_code:
                    sys.exit(1)
                else:
                    sys.exit(0)
                    
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(130)  # Standard exit code for Ctrl+C


if __name__ == "__main__":
    main()