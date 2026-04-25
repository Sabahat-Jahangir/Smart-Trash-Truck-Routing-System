import os
import sys
from colorama import init, Fore, Back, Style
from termcolor import colored
import time
from src.menu_system import MenuSystem
from src.utils.terminal_utils import clear_screen, center_text

def main():
    init()  # Initialize colorama
    menu_system = MenuSystem()
    
    while True:
        clear_screen()
        print("\n" * 2)
        print(center_text("╔══════════════════════════════════════════╗"))
        print(center_text("║     Smart Trash Truck Routing System     ║"))
        print(center_text("╚══════════════════════════════════════════╝"))
        print("\n")
        
        menu_system.display_main_menu()
        
        choice = input("\nEnter your choice (or 'q' to quit): ").strip().lower()
        
        if choice == 'q':
            print(center_text("Thank you for using Smart Trash Truck Routing System!"))
            time.sleep(1.5)
            sys.exit(0)
            
        menu_system.handle_main_menu_choice(choice)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        sys.exit(0) 