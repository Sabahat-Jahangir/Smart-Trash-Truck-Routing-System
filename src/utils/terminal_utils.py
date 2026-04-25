import os
import shutil

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_size():
    """Get the terminal size."""
    columns, rows = shutil.get_terminal_size()
    return columns, rows

def center_text(text):
    """Center text in terminal."""
    columns, _ = get_terminal_size()
    return text.center(columns)

def create_centered_menu(options):
    """Create a centered menu with options."""
    columns, _ = get_terminal_size()
    menu_width = max(len(option) for option in options) + 4
    padding = (columns - menu_width) // 2
    
    centered_options = []
    for option in options:
        centered_line = " " * padding + option + " " * (columns - len(option) - padding)
        centered_options.append(centered_line)
    
    return centered_options 