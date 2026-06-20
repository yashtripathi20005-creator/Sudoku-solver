"""
Entry point for the Sudoku game.
"""

import sys
import tkinter as tk
from .gui import SudokuGUI


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
