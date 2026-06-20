"""
Core Sudoku game logic including board management, validation, and solving.
"""

import copy
import random
from typing import List, Optional, Tuple


class Sudoku:
    """Main Sudoku class for game management and solving."""
    
    def __init__(self, grid: Optional[List[List[int]]] = None):
        """
        Initialize Sudoku board.
        
        Args:
            grid: 9x9 list of lists with 0 representing empty cells.
                  If None, creates an empty board.
        """
        if grid is None:
            self.grid = [[0 for _ in range(9)] for _ in range(9)]
        else:
            self.grid = [row[:] for row in grid]
        self.fixed_cells = [[bool(grid[i][j] != 0) for j in range(9)] for i in range(9)]
    
    def get_row(self, row: int) -> List[int]:
        """Get a row from the board."""
        return self.grid[row][:]
    
    def get_col(self, col: int) -> List[int]:
        """Get a column from the board."""
        return [self.grid[i][col] for i in range(9)]
    
    def get_box(self, row: int, col: int) -> List[int]:
        """Get a 3x3 box from the board."""
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        return [self.grid[box_row + i][box_col + j] 
                for i in range(3) for j in range(3)]
    
    def get_possible_values(self, row: int, col: int) -> List[int]:
        """
        Get all possible values for a cell using constraint propagation.
        
        Returns:
            List of valid numbers (1-9) for the cell.
        """
        if self.grid[row][col] != 0:
            return []
        
        used = set()
        used.update(self.get_row(row))
        used.update(self.get_col(col))
        used.update(self.get_box(row, col))
        
        return [num for num in range(1, 10) if num not in used]
    
    def is_valid(self) -> bool:
        """Check if the current board is valid (no conflicts)."""
        # Check rows
        for i in range(9):
            row = [num for num in self.get_row(i) if num != 0]
            if len(row) != len(set(row)):
                return False
        
        # Check columns
        for j in range(9):
            col = [num for num in self.get_col(j) if num != 0]
            if len(col) != len(set(col)):
                return False
        
        # Check boxes
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                box = [num for num in self.get_box(i, j) if num != 0]
                if len(box) != len(set(box)):
                    return False
        
        return True
    
    def is_solved(self) -> bool:
        """Check if the board is completely and correctly solved."""
        if any(0 in row for row in self.grid):
            return False
        return self.is_valid()
    
    def set_cell(self, row: int, col: int, value: int) -> bool:
        """
        Set a cell value if it's not fixed and the move is valid.
        
        Returns:
            True if successful, False otherwise.
        """
        if self.fixed_cells[row][col]:
            return False
        
        # Check if the move is valid
        old_value = self.grid[row][col]
        self.grid[row][col] = value
        
        if value != 0 and not self.is_valid():
            self.grid[row][col] = old_value
            return False
        
        return True
    
    def clear_cell(self, row: int, col: int) -> bool:
        """Clear a non-fixed cell."""
        if self.fixed_cells[row][col]:
            return False
        self.grid[row][col] = 0
        return True
    
    def get_hint(self) -> Optional[Tuple[int, int, int]]:
        """
        Find a cell with only one possible value and return it as a hint.
        
        Returns:
            Tuple of (row, col, value) or None if no hints available.
        """
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    possible = self.get_possible_values(i, j)
                    if len(possible) == 1:
                        return (i, j, possible[0])
        return None
    
    def count_solutions(self) -> int:
        """
        Count the number of solutions for the puzzle.
        (Limited to 2 to check uniqueness)
        
        Returns:
            0, 1, or 2 (2 means more than one solution).
        """
        # Find first empty cell
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    count = 0
                    for num in self.get_possible_values(i, j):
                        self.grid[i][j] = num
                        count += self.count_solutions()
                        if count >= 2:
                            self.grid[i][j] = 0
                            return 2
                        self.grid[i][j] = 0
                    return count
        return 1  # No empty cells found, it's a solution
    
    def has_unique_solution(self) -> bool:
        """Check if the puzzle has exactly one solution."""
        return self.count_solutions() == 1
    
    def __str__(self) -> str:
        """Return a string representation of the board."""
        result = []
        for i in range(9):
            if i % 3 == 0 and i != 0:
                result.append("-" * 21)
            row_str = []
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row_str.append("|")
                row_str.append(str(self.grid[i][j]) if self.grid[i][j] != 0 else ".")
            result.append(" ".join(row_str))
        return "\n".join(result)
