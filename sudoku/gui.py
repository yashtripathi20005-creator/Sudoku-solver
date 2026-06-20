"""
Graphical user interface for the Sudoku game using Tkinter.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Tuple, List
from .sudoku import Sudoku
from .generator import SudokuGenerator
from .solver import SudokuSolver


class SudokuGUI:
    """Main GUI application for Sudoku."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title("Sudoku")
        self.root.resizable(False, False)
        
        # Game state
        self.sudoku: Optional[Sudoku] = None
        self.solution: Optional[Sudoku] = None
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.cells: List[List[tk.Entry]] = []
        self.generator = SudokuGenerator()
        
        # Variables
        self.difficulty_var = tk.StringVar(value="medium")
        self.mode_var = tk.StringVar(value="play")
        
        self._create_widgets()
        self._new_game()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Sudoku", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Game board frame
        board_frame = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        board_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Create 9x9 grid of Entry widgets
        self.cells = []
        for i in range(9):
            row_cells = []
            for j in range(9):
                # Entry size
                cell = tk.Entry(board_frame, width=2, font=("Arial", 20, "bold"),
                               justify="center", relief=tk.FLAT, bd=1)
                
                # Add borders for 3x3 boxes
                if i % 3 == 0:
                    cell.config(highlightthickness=2, highlightcolor="black")
                if j % 3 == 0:
                    cell.config(highlightthickness=2, highlightcolor="black")
                
                cell.grid(row=i, column=j, padx=1, pady=1, ipady=5)
                cell.bind("<KeyRelease>", lambda e, r=i, c=j: self._on_cell_change(r, c))
                cell.bind("<Button-1>", lambda e, r=i, c=j: self._select_cell(r, c))
                
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Buttons
        ttk.Button(control_frame, text="New Game", command=self._new_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Check", command=self._check_puzzle).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Hint", command=self._give_hint).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Solve", command=self._solve_puzzle).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear", command=self._clear_cell).pack(side=tk.LEFT, padx=5)
        
        # Difficulty selection
        difficulty_frame = ttk.Frame(main_frame)
        difficulty_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Label(difficulty_frame, text="Difficulty:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(difficulty_frame, text="Easy", variable=self.difficulty_var, 
                       value="easy").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(difficulty_frame, text="Medium", variable=self.difficulty_var, 
                       value="medium").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(difficulty_frame, text="Hard", variable=self.difficulty_var, 
                       value="hard").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(difficulty_frame, text="Expert", variable=self.difficulty_var, 
                       value="expert").pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _new_game(self):
        """Start a new game with the selected difficulty."""
        difficulty = self.difficulty_var.get()
        
        try:
            puzzle, solution = self.generator.create_puzzle(difficulty)
            self.sudoku = puzzle
            self.solution = solution
            self._update_board()
            self.selected_cell = None
            self.status_var.set(f"New {difficulty} puzzle created")
            
            # Update cell colors
            for i in range(9):
                for j in range(9):
                    if puzzle.fixed_cells[i][j]:
                        self.cells[i][j].config(fg="black", disabledbackground="#f0f0f0")
                    else:
                        self.cells[i][j].config(fg="blue", disabledbackground="white")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create puzzle: {e}")
    
    def _update_board(self):
        """Update the board display from the Sudoku object."""
        if not self.sudoku:
            return
        
        for i in range(9):
            for j in range(9):
                value = self.sudoku.grid[i][j]
                self.cells[i][j].config(state="normal")
                if value != 0:
                    self.cells[i][j].delete(0, tk.END)
                    self.cells[i][j].insert(0, str(value))
                    
                    # Color fixed cells differently
                    if self.sudoku.fixed_cells[i][j]:
                        self.cells[i][j].config(fg="black", disabledbackground="#f0f0f0")
                    else:
                        self.cells[i][j].config(fg="blue", disabledbackground="white")
                else:
                    self.cells[i][j].delete(0, tk.END)
                    self.cells[i][j].config(fg="blue", disabledbackground="white")
                
                # Disable fixed cells
                if self.sudoku.fixed_cells[i][j]:
                    self.cells[i][j].config(state="disabled")
                else:
                    self.cells[i][j].config(state="normal")
    
    def _on_cell_change(self, row: int, col: int):
        """Handle cell value changes."""
        if not self.sudoku or self.sudoku.fixed_cells[row][col]:
            return
        
        entry = self.cells[row][col]
        value = entry.get().strip()
        
        if value == "":
            self.sudoku.clear_cell(row, col)
            return
        
        try:
            num = int(value)
            if 1 <= num <= 9:
                if self.sudoku.set_cell(row, col, num):
                    self._update_board()
                    if self.sudoku.is_solved():
                        self.status_var.set("Congratulations! Puzzle solved!")
                        messagebox.showinfo("Congratulations", "Puzzle solved!")
                else:
                    entry.delete(0, tk.END)
                    if num != 0:
                        self.status_var.set(f"Invalid move: {num} at ({row+1}, {col+1})")
            else:
                entry.delete(0, tk.END)
                self.status_var.set("Please enter a number between 1 and 9")
        except ValueError:
            entry.delete(0, tk.END)
            if value != "":
                self.status_var.set("Please enter a valid number")
    
    def _select_cell(self, row: int, col: int):
        """Handle cell selection."""
        self.selected_cell = (row, col)
        
        # Clear previous selection highlighting
        for i in range(9):
            for j in range(9):
                self.cells[i][j].config(bg="white")
        
        # Highlight selected cell
        if self.sudoku and not self.sudoku.fixed_cells[row][col]:
            self.cells[row][col].config(bg="#ffff99")
            
            # Highlight same number
            value = self.sudoku.grid[row][col]
            if value != 0:
                for i in range(9):
                    for j in range(9):
                        if self.sudoku.grid[i][j] == value and not self.sudoku.fixed_cells[i][j]:
                            self.cells[i][j].config(bg="#e0f0e0")
    
    def _check_puzzle(self):
        """Check if the current puzzle is correct."""
        if not self.sudoku:
            return
        
        if self.sudoku.is_valid():
            if self.sudoku.is_solved():
                self.status_var.set("Puzzle is solved correctly!")
                messagebox.showinfo("Success", "Puzzle is solved correctly!")
            else:
                self.status_var.set("No conflicts found, but puzzle is not complete")
        else:
            self.status_var.set("Invalid puzzle: conflicts detected!")
            messagebox.showwarning("Invalid", "Invalid puzzle: conflicts detected!")
    
    def _give_hint(self):
        """Give a hint for the next move."""
        if not self.sudoku:
            return
        
        hint = self.sudoku.get_hint()
        if hint:
            row, col, value = hint
            self.cells[row][col].delete(0, tk.END)
            self.cells[row][col].insert(0, str(value))
            self.sudoku.grid[row][col] = value
            self.cells[row][col].config(fg="green")
            self.status_var.set(f"Hint: Cell ({row+1}, {col+1}) should be {value}")
        else:
            self.status_var.set("No hints available")
    
    def _solve_puzzle(self):
        """Solve the puzzle using the solver."""
        if not self.sudoku:
            return
        
        # Confirm with user
        if not messagebox.askyesno("Solve", "Do you want to see the solution?"):
            return
        
        solver = SudokuSolver(self.sudoku)
        solved = solver.solve("hybrid")
        
        if solved:
            self.sudoku = solved
            self._update_board()
            self.status_var.set("Puzzle solved!")
        else:
            self.status_var.set("No solution found for this puzzle")
    
    def _clear_cell(self):
        """Clear the selected cell."""
        if not self.sudoku or not self.selected_cell:
            return
        
        row, col = self.selected_cell
        if not self.sudoku.fixed_cells[row][col]:
            self.sudoku.clear_cell(row, col)
            self._update_board()
            self.status_var.set(f"Cleared cell ({row+1}, {col+1})")
