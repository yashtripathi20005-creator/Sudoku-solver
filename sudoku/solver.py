"""
Advanced Sudoku solving algorithms including backtracking and human strategies.
"""

import copy
from typing import List, Optional, Tuple
from .sudoku import Sudoku


class SudokuSolver:
    """Contains various algorithms to solve Sudoku puzzles."""
    
    def __init__(self, sudoku: Sudoku):
        """
        Initialize the solver with a Sudoku puzzle.
        
        Args:
            sudoku: Sudoku object to solve.
        """
        self.original = sudoku
        self.grid = [row[:] for row in sudoku.grid]
        self.solution = None
        self.steps = []  # For tracking solution steps
    
    def solve(self, method: str = "backtracking") -> Optional[Sudoku]:
        """
        Solve the puzzle using the specified method.
        
        Args:
            method: 'backtracking', 'human', or 'hybrid'
            
        Returns:
            Solved Sudoku object or None if no solution.
        """
        if method == "backtracking":
            self.grid = [row[:] for row in self.original.grid]
            if self._backtracking_solve():
                return Sudoku(self.grid)
        
        elif method == "human":
            self.grid = [row[:] for row in self.original.grid]
            if self._human_solve():
                return Sudoku(self.grid)
        
        elif method == "hybrid":
            self.grid = [row[:] for row in self.original.grid]
            if self._hybrid_solve():
                return Sudoku(self.grid)
        
        return None
    
    def _backtracking_solve(self) -> bool:
        """
        Basic backtracking algorithm to solve the puzzle.
        
        Returns:
            True if solved, False otherwise.
        """
        # Find empty cell
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    # Try all possible numbers
                    for num in range(1, 10):
                        if self._is_valid_move(i, j, num):
                            self.grid[i][j] = num
                            if self._backtracking_solve():
                                return True
                            self.grid[i][j] = 0
                    return False
        return True
    
    def _human_solve(self) -> bool:
        """
        Use human-like strategies (naked singles, hidden singles, etc.)
        
        Returns:
            True if solved, False otherwise.
        """
        iterations = 0
        while iterations < 100:  # Prevent infinite loops
            progress = False
            
            # 1. Naked Singles
            for i in range(9):
                for j in range(9):
                    if self.grid[i][j] == 0:
                        possible = self._get_possible_values(i, j)
                        if len(possible) == 1:
                            self.grid[i][j] = possible[0]
                            progress = True
            
            # 2. Hidden Singles
            if not progress:
                progress = self._find_hidden_singles()
            
            # 3. Naked Pairs/Triples (simplified version)
            if not progress:
                progress = self._find_naked_pairs()
            
            # Check if solved
            if all(self.grid[i][j] != 0 for i in range(9) for j in range(9)):
                return True
            
            if not progress:
                # If stuck, use backtracking for the remaining cells
                return self._backtracking_solve()
            
            iterations += 1
        
        return False
    
    def _hybrid_solve(self) -> bool:
        """
        Hybrid approach: use human strategies first, then backtracking.
        
        Returns:
            True if solved, False otherwise.
        """
        # Try human strategies first
        if self._human_solve():
            return True
        
        # If still not solved, apply backtracking from current state
        return self._backtracking_solve()
    
    def _is_valid_move(self, row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid."""
        # Check row
        if num in self.grid[row]:
            return False
        
        # Check column
        for i in range(9):
            if self.grid[i][col] == num:
                return False
        
        # Check box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if self.grid[box_row + i][box_col + j] == num:
                    return False
        
        return True
    
    def _get_possible_values(self, row: int, col: int) -> List[int]:
        """Get all possible values for a cell."""
        used = set()
        used.update(self.grid[row])
        for i in range(9):
            used.add(self.grid[i][col])
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                used.add(self.grid[box_row + i][box_col + j])
        return [num for num in range(1, 10) if num not in used]
    
    def _find_hidden_singles(self) -> bool:
        """
        Find hidden singles (numbers that can only go in one cell in a unit).
        
        Returns:
            True if any progress was made.
        """
        progress = False
        
        # Check rows
        for row in range(9):
            for num in range(1, 10):
                if num in self.grid[row]:
                    continue
                possible_cols = []
                for col in range(9):
                    if self.grid[row][col] == 0 and self._is_valid_move(row, col, num):
                        possible_cols.append(col)
                if len(possible_cols) == 1:
                    self.grid[row][possible_cols[0]] = num
                    progress = True
        
        # Check columns
        for col in range(9):
            for num in range(1, 10):
                if any(self.grid[row][col] == num for row in range(9)):
                    continue
                possible_rows = []
                for row in range(9):
                    if self.grid[row][col] == 0 and self._is_valid_move(row, col, num):
                        possible_rows.append(row)
                if len(possible_rows) == 1:
                    self.grid[possible_rows[0]][col] = num
                    progress = True
        
        # Check boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                for num in range(1, 10):
                    possible_cells = []
                    for i in range(3):
                        for j in range(3):
                            row, col = box_row + i, box_col + j
                            if self.grid[row][col] == 0 and self._is_valid_move(row, col, num):
                                possible_cells.append((row, col))
                    if len(possible_cells) == 1:
                        row, col = possible_cells[0]
                        self.grid[row][col] = num
                        progress = True
        
        return progress
    
    def _find_naked_pairs(self) -> bool:
        """
        Find and eliminate naked pairs in rows, columns, and boxes.
        
        Returns:
            True if any progress was made.
        """
        progress = False
        
        # Check each unit (row, column, box)
        for unit_type in ['row', 'col', 'box']:
            for unit_idx in range(9):
                cells = []
                if unit_type == 'row':
                    cells = [(unit_idx, j) for j in range(9) if self.grid[unit_idx][j] == 0]
                elif unit_type == 'col':
                    cells = [(i, unit_idx) for i in range(9) if self.grid[i][unit_idx] == 0]
                else:  # box
                    box_row, box_col = (unit_idx // 3) * 3, (unit_idx % 3) * 3
                    cells = [(box_row + i, box_col + j) 
                            for i in range(3) for j in range(3) 
                            if self.grid[box_row + i][box_col + j] == 0]
                
                if len(cells) < 2:
                    continue
                
                # Find naked pairs
                for i in range(len(cells)):
                    for j in range(i + 1, len(cells)):
                        r1, c1 = cells[i]
                        r2, c2 = cells[j]
                        vals1 = set(self._get_possible_values(r1, c1))
                        vals2 = set(self._get_possible_values(r2, c2))
                        
                        if len(vals1) == 2 and vals1 == vals2:
                            # Eliminate these values from other cells in the unit
                            for r, c in cells:
                                if (r, c) != (r1, c1) and (r, c) != (r2, c2):
                                    if any(v in self._get_possible_values(r, c) for v in vals1):
                                        # Remove these values
                                        for v in vals1:
                                            if self.grid[r][c] == 0:
                                                # Check if this is a valid elimination
                                                old_possible = self._get_possible_values(r, c)
                                                if v in old_possible:
                                                    # We can't directly remove values without a more complex structure
                                                    # This is a placeholder for a more sophisticated implementation
                                                    pass
        return progress
    
    def get_solution_count(self, limit: int = 2) -> int:
        """
        Count the number of solutions (limited to avoid infinite loops).
        
        Args:
            limit: Maximum number of solutions to find.
            
        Returns:
            Number of solutions found (capped at limit).
        """
        return self._count_solutions(limit)
    
    def _count_solutions(self, limit: int = 2) -> int:
        """Recursive solution counter."""
        # Find empty cell
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    count = 0
                    for num in range(1, 10):
                        if self._is_valid_move(i, j, num):
                            self.grid[i][j] = num
                            count += self._count_solutions(limit - count)
                            if count >= limit:
                                self.grid[i][j] = 0
                                return count
                            self.grid[i][j] = 0
                    return count
        return 1
