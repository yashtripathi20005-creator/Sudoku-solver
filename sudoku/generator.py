"""
Sudoku puzzle generator for creating puzzles with varying difficulty.
"""

import random
import copy
from typing import List, Tuple, Optional
from .sudoku import Sudoku


class SudokuGenerator:
    """Generates Sudoku puzzles with various difficulty levels."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the generator.
        
        Args:
            seed: Optional random seed for reproducible puzzles.
        """
        if seed is not None:
            random.seed(seed)
    
    def generate_solution(self) -> List[List[int]]:
        """
        Generate a complete valid Sudoku solution.
        
        Returns:
            9x9 grid with all cells filled.
        """
        board = [[0 for _ in range(9)] for _ in range(9)]
        self._solve(board)
        return board
    
    def _solve(self, board: List[List[int]]) -> bool:
        """Recursive backtracking solver for generation."""
        empty = self._find_empty(board)
        if not empty:
            return True
        
        row, col = empty
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for num in numbers:
            if self._is_valid_move(board, row, col, num):
                board[row][col] = num
                if self._solve(board):
                    return True
                board[row][col] = 0
        
        return False
    
    def _find_empty(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find an empty cell in the board."""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def _is_valid_move(self, board: List[List[int]], row: int, col: int, 
                       num: int) -> bool:
        """Check if a move is valid."""
        # Check row
        if num in board[row]:
            return False
        
        # Check column
        for i in range(9):
            if board[i][col] == num:
                return False
        
        # Check box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if board[box_row + i][box_col + j] == num:
                    return False
        
        return True
    
    def create_puzzle(self, difficulty: str = "medium") -> Tuple[Sudoku, Sudoku]:
        """
        Create a new puzzle with the given difficulty.
        
        Args:
            difficulty: 'easy', 'medium', 'hard', or 'expert'
            
        Returns:
            Tuple of (puzzle, solution) as Sudoku objects.
        """
        # Difficulty levels: number of cells to remove
        difficulty_map = {
            'easy': 30,
            'medium': 45,
            'hard': 52,
            'expert': 58
        }
        cells_to_remove = difficulty_map.get(difficulty.lower(), 45)
        
        # Generate a complete solution
        solution_grid = self.generate_solution()
        puzzle_grid = [row[:] for row in solution_grid]
        
        # Remove cells
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for idx, (row, col) in enumerate(cells):
            if idx >= cells_to_remove:
                break
            
            # Try removing this cell
            temp = puzzle_grid[row][col]
            puzzle_grid[row][col] = 0
            
            # Check if puzzle still has unique solution
            sudoku = Sudoku(puzzle_grid)
            if not sudoku.has_unique_solution():
                puzzle_grid[row][col] = temp
        
        # Ensure we removed enough cells
        removed = sum(1 for row in puzzle_grid for cell in row if cell == 0)
        if removed < cells_to_remove:
            # Add more removals if needed
            for row, col in cells:
                if removed >= cells_to_remove:
                    break
                if puzzle_grid[row][col] != 0:
                    temp = puzzle_grid[row][col]
                    puzzle_grid[row][col] = 0
                    sudoku = Sudoku(puzzle_grid)
                    if sudoku.has_unique_solution():
                        removed += 1
                    else:
                        puzzle_grid[row][col] = temp
        
        return Sudoku(puzzle_grid), Sudoku(solution_grid)
    
    def create_from_template(self, template: List[List[int]]) -> Sudoku:
        """
        Create a puzzle from a template grid.
        
        Args:
            template: 9x9 grid with 0 for empty cells.
            
        Returns:
            Sudoku puzzle object.
        """
        return Sudoku(template)
