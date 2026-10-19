from sys import exit
import os
import subprocess
import random
from mazegen import Cell, MazeGenerator


class Visualizer:
    """Provides a terminal-based interface for displaying and interacting
    with a maze.
    """
    show_path: bool
    wall_color: str
    ft_color: str
    reset_color: str

    def __init__(self) -> None:
        """Initialize the visualizer with default display settings."""
        self.show_path = False
        self.wall_color = "\033[35m"
        self.ft_color = "\033[43m"
        self.reset_color = "\033[0m"

    def run_visualizer(self, maze: MazeGenerator) -> None:
        """Run the interface to render interactively the maze

        Args:
            maze: The maze to render.

        Returns:
            None
        """
        self.__draw(maze)
        """while True:
            choice = self.__menu()
            maze = self.__handle_choice(choice, maze)
            self.__draw(maze)"""

    # ====================
    # Rendering Functions
    # ====================

    def __draw(self, maze: MazeGenerator) -> None:
        """Render the maze row by row.

        Args:
            maze: The maze to render.

        Returns:
            None
        """
        print(f"{self.wall_color}\nSeed mode: "
              f"{'enabled' if maze.enable_seed else 'disabled'}")
        for i in range(maze.height):
            # print upper
            self.__draw_horizontal(maze.grid[i], True)
            # print middle
            self.__draw_middle(maze.grid[i], maze)
            # print lower
        last_row = maze.grid[-1]
        self.__draw_horizontal(last_row, False)

    def __draw_horizontal(self, row: list[Cell], use_north: bool) -> None:
        """Draw the horizontal walls for a row of cells.

        Args:
            row: The row of cells to render.
            use_north: If True, draw the north walls; otherwise, draw the
                south walls.

        Returns:
            None
        """
        line: str = ""
        for c in row:
            line += f"{self.wall_color}+{self.reset_color}"
            if use_north:
                wall = c.get_north()
            else:
                wall = c.get_south()
            if wall:
                line += f"{self.wall_color}---{self.reset_color}"
            else:
                line += "   "
        print(line + f"{self.wall_color}+{self.reset_color}")

    def __get_cell_content(self, cell: Cell, maze: MazeGenerator) -> str:
        """Return the text representation of a cell's contents.

        The returned string depends on whether the cell is the maze entry,
        exit, part of the displayed shortest path, or a fully enclosed cell.

        Args:
            cell: The cell to render.
            maze: The maze containing the cell.

        Returns:
            str: The formatted string representing the cell's contents.
        """
        if (cell.x, cell.y) == maze.entry_p:
            return "\033[92m E \033[0m"
        if (cell.x, cell.y) == maze.exit_p:
            return "\033[91m X \033[0m"
        if self.show_path and cell.path:
            return (" · ")
        if (cell.is_full()):
            return f"{self.ft_color}   {self.reset_color}"
        return "   "

    def __draw_middle(self, row: list[Cell], maze: MazeGenerator) -> None:
        """Draw the middle section of a row, including cell
        contents and vertical walls.

        Args:
            row: The row of cells to render.
            maze: The maze containing the row.

        Returns:
            None
        """
        line = ""
        if row[0].get_west():
            line += f"{self.wall_color}|{self.reset_color}"
        else:
            line += " "
        for c in row:
            content = self.__get_cell_content(c, maze)
            line += content
            if c.get_east():
                line += f"{self.wall_color}|{self.reset_color}"
            else:
                line += " "
        print(line)

    # ====================
    # Interactive menu functions
    # ====================

    def __menu(self) -> str:
        """Display the interactive menu and return the user's choice.

        Returns:
            str: The selected menu option.
        """
        print("=== A-Maze-ing ===")
        print("1. Regenerate maze")
        print("2. Show/Hide path")
        print("3. Change wall color")
        print("4. Enable/Disable seed mode")
        print("5. Quit")
        return input("Choice? (1-5): ")

    def __handle_choice(self, choice: str,
                        maze: MazeGenerator) -> MazeGenerator:
        """Process a menu selection and perform the corresponding action.

        Args:
            choice: The menu option selected by the user.
            maze: The maze currently being displayed.

        Returns:
            maze to be displayed next (same or regenerated)
        """
        while choice not in ["1", "2", "3", "4", "5"]:
            clean_terminal()
            self.__draw(maze)
            print("Invalid option, try again:")
            choice = self.__menu()
        if choice == "1":
            return self.__regenerate_maze(maze)
        if choice == "2":
            self.__show_shortest_path(maze)
        if choice == "3":
            self.__change_wall_color(maze)
        if choice == "4":
            self.__toggle_seed_mode(maze)
            return self.__regenerate_maze(maze)
        if choice == "5":
            exit()
        return maze

    def __toggle_seed_mode(self, maze: MazeGenerator) -> None:
        """Toggle seed mode.

        When seed mode is enabled without a configured seed, generate
        a random seed that will be reused for future regenerations.
        """
        maze.enable_seed = not maze.enable_seed
        if maze.enable_seed and maze.seed == 0:
            maze.seed = random.randint(1, 2**32 - 1)

    def __regenerate_maze(self, maze: MazeGenerator) -> MazeGenerator:
        """Generate a new maze using the current maze configuration.
        Args:
            maze: The current maze whose configuration will be reused.
        Returns:
            MazeGenerator: A newly generated maze with the same configuration.
        """
        clean_terminal()
        M = MazeGenerator(
            maze.width,
            maze.height,
            maze.entry_p,
            maze.exit_p,
            maze.perfect,
            maze.seed
        )
        M.enable_seed = maze.enable_seed
        M.generate()
        if self.show_path:
            self.show_path = False
        return M

    def __show_shortest_path(self, maze: MazeGenerator) -> None:
        """Toggle the shortest path display and redraw the maze.

        If a valid path exists, all cells along the shortest path are marked
        and displayed when show_path is enabled.

        Args:
            maze: The maze in which to compute and display the shortest path.

        Returns:
            None
        """
        clean_terminal()
        self.show_path = not self.show_path
        if maze.shortest_path:
            for pos in maze.shortest_path:
                cell = maze.grid[pos[1]][pos[0]]
                cell.path = True
        else:
            print("Looks like there is no exit :/")

    def __change_wall_color(self, maze: MazeGenerator) -> None:
        """Select a new random wall color and redraw the maze.

        The new color is guaranteed to differ from the current one.

        Args:
            maze: The maze to redraw.

        Returns:
            None
        """
        colors: list[str] = ["\033[96m", "\033[32m", "\033[94m",
                             "\033[36m", "\033[95m"]
        prev_color: str = self.wall_color
        while (prev_color == self.wall_color):
            self.wall_color = random.choice(colors)
        self.__draw(maze)
        clean_terminal()


def clean_terminal() -> None:
    if os.name == 'nt':
        subprocess.run(['cls'], shell=True)
    else:
        subprocess.run(['clear'])
