import numpy as np
import numpy.typing as npt
from typing import TypeAlias, Any
import random
import heapq
from .cell import Cell
from .movement import Direction


"""Represents a position in the maze using x and y coordinates."""
Position: TypeAlias = tuple[int, int]


class MazeGenerator():
    """A maze generator.

    Contains the grid formed from Cells, the width and height of said grid,
    the entry and exit points, whether it's perfect or not,
    and the coordinates of its 42 pattern.

    Due to this maze having a fixed pattern at the centre, it cannot be
    smaller than 7 cells wide and 5 cells tall.

    The entry and exit positions must be different and within the maze bounds.

    All of the walls that aren't part of the outer border are two-sided;
    e.g.: the east wall at 4,5 must be the same as the west wall at 4,6.

    A maze is perfect when there is exactly one path between the entry
    and the exit.
    A maze being not perfect means that there is at least two independent
    routes between entry and exit.
    A braided maze is an imperfect maze with no dead-ends.

    Public functions:
    - __init__()
    - get_cell()
    - generate()
    - save()
    """
    grid: npt.NDArray[np.object_]
    width: int
    height: int
    entry_p: Position
    exit_p: Position
    perfect: bool
    seed: int
    enable_seed: bool
    ft_coords: list[Position]
    shortest_path: list[Position]

    def __init__(self, w: int, h: int, en: Position, ex: Position,
                 p: bool, s: int) -> None:
        """Initialize the configuration with the given values."""
        self.width = w
        self.height = h
        self.perfect = p
        self.seed = s
        self.enable_seed = (self.seed != 0)
        self.ft_coords = self.__get_ft_coords()
        self.entry_p = self.__validate_point(en, "Entry")
        self.exit_p = self.__validate_point(ex, "Exit")
        self.grid = self.__make_grid()
        self.shortest_path = []

    # ==============================
    # BUILDING FUNCTIONS
    # ==============================

    def __validate_point(self, point: Position, name: str) -> Position:
        """Ensure the given position is not where the pattern should be."""
        if not self.__is_ft_coord(point[0], point[1]):
            return point
        else:
            raise ValueError(f"{name} point cannot be a pattern position")

    def __make_grid(self) -> npt.NDArray[np.object_]:
        """
        Creates a new grid with alll cells' walls having the given value.
        """
        return np.array(
            [[Cell(i, j, True)
              for i in range(self.width)] for j in range(self.height)],
            dtype=object,
        )

    # ==============================
    # GET FUNCTIONS
    # ==============================

    def get_cell(self, x: int, y: int) -> Any:
        """Return the maze cell corresponding on the coordinates."""
        return self.grid[y, x]

    def is_valid_coord(self, x: int, y: int) -> bool:
        """Return whether the given coordinates are within maze bounds."""
        if x < 0 or y < 0:
            return False
        elif x > self.width - 1 or y > self.height - 1:
            return False
        return True

    def is_cell_full(self, x: int, y: int) -> bool:
        """Return whether the cell in the given coordinates is full."""
        if self.is_valid_coord(x, y):
            c: Cell = self.get_cell(x, y)
            if c.is_full():
                return True
        return False

    # ==============================
    # 42 PATTERN FUNCTIONS
    # ==============================

    def __is_ft_coord(self, x: int, y: int) -> bool:
        """
        Return whether the position given is one the 42 symbol should occupy.
        """
        for coord in self.ft_coords:
            cx, cy = coord
            if x == cx and y == cy:
                return True
        return False

    def __get_ft_coords(self) -> list[Position]:
        """
        Obtain the coordinates that the 42 symbol (#)
        will occupy in relation to the center (·) of the maze
        Due to the rounding, if the width is odd, the symbol will appear
        slightly to the right; and if the height is odd, slightly downwards
        """
        coordinates: list[Position] = []
        centre_x: int = int(self.width / 2)
        centre_y: int = int(self.height / 2)
        # Positions of 4
        coordinates.append((centre_x - 1, centre_y))
        coordinates.append((centre_x - 2, centre_y))
        coordinates.append((centre_x - 3, centre_y))
        coordinates.append((centre_x - 3, centre_y - 1))
        coordinates.append((centre_x - 3, centre_y - 2))
        coordinates.append((centre_x - 1, centre_y + 1))
        coordinates.append((centre_x - 1, centre_y + 2))
        # Positions of 2
        coordinates.append((centre_x + 1, centre_y - 2))
        coordinates.append((centre_x + 2, centre_y - 2))
        coordinates.append((centre_x + 3, centre_y - 2))
        coordinates.append((centre_x + 3, centre_y - 1))
        coordinates.append((centre_x + 1, centre_y))
        coordinates.append((centre_x + 2, centre_y))
        coordinates.append((centre_x + 3, centre_y))
        coordinates.append((centre_x + 1, centre_y + 1))
        coordinates.append((centre_x + 1, centre_y + 2))
        coordinates.append((centre_x + 2, centre_y + 2))
        coordinates.append((centre_x + 3, centre_y + 2))
        return coordinates

    # ==================================================
    #
    # MAZE GENERATION ALGORITHMS
    #
    # ==================================================

    # ==============================
    # UTIL FUNCTIONS
    # ==============================

    def __move(self, x: int, y: int, dirc: Direction) -> Position:
        """Return the coordinates of the cell moved to going from
        a start position towards a direction.

        Args:
            x, y:       the coordinates of the current cell
            direction:  the direction to move to

        Returns:
            the coordinates of cell moved to
        """
        movement = dirc.get_movement()
        return x + movement[0], y + movement[1]

    def __break_wall(self, x1: int, y1: int, dirc: Direction) -> Position:
        """Destroy the wall at the direction and position given.

        Both the cell at the given coordinates and the cell that shares
        the selected wall will be affected.

        Args:
            x1, y1:     the coordinates of current cell
            direction:  the direction of the wall to destroy

        Returns:
            the coordinates of the neighboring cell
        """
        x2, y2 = self.__move(x1, y1, dirc)
        if self.is_valid_coord(x2, y2):
            self.get_cell(x1, y1).break_wall(dirc)
            self.get_cell(x2, y2).break_wall(dirc.opposite())
            return x2, y2
        return x1, y1

    # ==================================================
    # PERFECT MAZE GENERATION (BACKTRACKING)
    # ==================================================

    def __perfect_maze(self, x: int, y: int) -> None:
        """Backtracker algorithm with perfect result.

        Travel throughout the grid, check possible directions to break walls
        and gradually build the maze. If there are no possible directions to
        travel towards, go back and check again.

        Args:
            x, y:   the starting coordinates, used to move throughout the maze.
        """

        def obtain_directions(x: int, y: int) -> list[Direction]:
            """Examine which directions it is possible to move towards
            given the current cell.

            A possible direction is one that doesn't exceed maze bounds,
            that hasn't been modified before (is still full), or that is
            not part of the 42 pattern.

            Args:
                x, y: the current coordinates

            Returns:
                A list with all possible directions to move towards at
                the current coordinates. It will have some combination of
                'N', 'S', 'W' or 'E', or be empty.
            """
            directions: list[Direction] = []
            for d in Direction:
                new_x, new_y = self.__move(x, y, d)
                if (self.is_cell_full(new_x, new_y) and
                        not self.__is_ft_coord(new_x, new_y)):
                    directions.append(d)
            return directions

        path: list[Direction] = []
        while True:
            pos_dirs: list[Direction] = obtain_directions(x, y)
            if len(pos_dirs) >= 1:
                direction: Direction = random.choice(pos_dirs)
                path.append(direction)
                x, y = self.__break_wall(x, y, direction)
            else:
                if len(path) > 1:
                    last_dir: Direction = path.pop()
                    x, y = self.__move(x, y, last_dir.opposite())
                else:
                    break

    # ==================================================
    # NON-PERFECT MAZE GENERATION (CUSTOM)
    # ==================================================

    def __imperfect_maze(self) -> None:
        """Iterative algorithm for converting a perfect maze
        to a non perfect one.

        Travels the entire maze looking for dead-ends (cells with 3 walls)
        and deletes a one of its walls (that isn't a border wall).
        This process excludes the two dead-ends created by the 2 pattern.
        """
        pos_walls: list[Direction] = []
        for x in range(self.width):
            for y in range(self.height):
                pos_walls = self.get_cell(x, y).get_walls()
                if len(pos_walls) == 3:
                    for d in pos_walls:
                        nx, ny = self.__move(x, y, d)
                        if (not self.is_valid_coord(nx, ny) or
                                self.is_cell_full(nx, ny) or
                                self.__is_ft_coord(nx, ny)):
                            pos_walls.remove(d)
                    if len(pos_walls) > 0:
                        di: Direction = random.choice(pos_walls)
                        self.__break_wall(x, y, di)

    # ==================================================
    #
    # MAZE SOLVER ALGORITHMS
    #
    # ==================================================

    def __find_shortest_path(self) -> None:
        """Find the shortest path between the maze entry and exit and
        assigns it to the attribute.
        """

        def heuristic(a: Position, b: Position) -> int:
            """Compute the Manhattan distance between two positions.

            The Manhattan distance is the sum of the absolute differences
            between the x and y coordinates.

            Args:
                a: The starting position.
                b: The target position.

            Returns:
                int: The Manhattan distance between the two positions.
            """
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(node: Position) -> list[Position]:
            """Return all reachable neighboring positions from a given node.

            Only adjacent cells that are not separated by a wall are included.

            Args:
                node: The current position in the maze.

            Returns:
                list[Position]: A list of adjacent positions that
                    can be reached.
            ... ... ...
            """
            neighbors: list[Position] = []
            cell: Cell = self.get_cell(node[0], node[1])
            if not cell.get_north() and node[1] > 0:
                neighbors.append((node[0], node[1] - 1))
            if not cell.get_south() and node[1] < self.height - 1:
                neighbors.append((node[0], node[1] + 1))
            if not cell.get_east() and node[0] < self.width - 1:
                neighbors.append((node[0] + 1, node[1]))
            if not cell.get_west() and node[0] > 0:
                neighbors.append((node[0] - 1, node[1]))
            return neighbors

        def reconstruct_path(parents: dict[Position, Position],
                             goal: Position) -> list[Position]:
            """Reconstruct the shortest path from the start to the goal.

            The path is rebuilt by following the parent relationship from
            the goal node back to the starting node.

            Args:
                parents: A mapping from each visited position to its
                    predecessor.
                goal: The destination position.

            Returns:
                list[Position]: The ordered path from the start position to
                    the goal.
            """
            path: list[Position] = []
            current: Position = goal
            while current in parents:
                path.append(current)
                current = parents[current]
            path.append(current)
            path.reverse()
            return path

        def a_star(start: Position, goal: Position) -> list[Position]:
            """Find the shortest path between two positions using
            the A* algorithm.

            The algorithm explores the maze using the Manhattan distance
            as its heuristic and returns the shortest path if one exists.

            Args:
                start: The starting position.
                goal: The destination position.

            Returns:
                list[Position]: The shortest path from ``start`` to ``goal``,
                or an empty list if no valid path exists.
            """
            open_list: list[tuple[int, Position]] = []
            closed_list: set[Position] = set()
            g_score: dict[Position, int] = {start: 0}
            parents: dict[Position, Position] = {}
            current_f = heuristic(start, goal)
            heapq.heappush(open_list, (current_f, start))
            while open_list:
                current_f, current_pos = heapq.heappop(open_list)
                if current_pos in closed_list:
                    continue
                if current_pos == goal:
                    return reconstruct_path(parents, goal)
                closed_list.add(current_pos)
                for neighbor in get_neighbors(current_pos):
                    if neighbor in closed_list:
                        continue
                    tentative_g = g_score[current_pos] + 1
                    if (neighbor not in g_score or
                            tentative_g < g_score[neighbor]):
                        parents[neighbor] = current_pos
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor, goal)
                        heapq.heappush(open_list, (f_score, neighbor))
            empty: list[Position] = []
            return empty

        self.shortest_path = a_star(self.entry_p, self.exit_p)

    # ==================================================
    #
    # PUBLIC FUNCTIONS
    #
    # ==================================================

    # ==============================
    # MAZE GENERATION AND SOLVING CALLER
    # ==============================

    def generate(self) -> None:
        if self.enable_seed:
            random.seed(self.seed)
        x, y = self.entry_p
        self.__perfect_maze(int(x), int(y))
        if not self.perfect:
            self.__imperfect_maze()
        self.__find_shortest_path()

    # ==============================
    # OUTPUT FILE CALLER
    # ==============================

    def save(self, filename: str) -> None:
        """Save the grid and attributes of the maze to the file."""

        def get_path_directions() -> list[str]:
            """
            Converts the coordinates of the path from start to the goal to
            a list of cardinal directions.

            Args:
                path: The list of coordinates passed
                    from the start position to the goal.

            Returns:
                A list of all the directions traveled in from
                the start to the goal.
            """
            dir_list: list[str] = []
            if self.shortest_path:
                size: int = len(self.shortest_path)
                initial_pos: Position = self.shortest_path[0]
                for i in range(1, size):
                    next_pos: Position = self.shortest_path[i]
                    diff_x: int = next_pos[0] - initial_pos[0]
                    diff_y: int = next_pos[1] - initial_pos[1]
                    if (diff_x == 0 and diff_y == -1):
                        dir_list.append("N")
                    elif (diff_x == 0 and diff_y == 1):
                        dir_list.append("S")
                    elif (diff_x == -1 and diff_y == 0):
                        dir_list.append("W")
                    elif (diff_x == 1 and diff_y == 0):
                        dir_list.append("E")
                    initial_pos = next_pos
            return dir_list

        with open(filename, 'w') as f:
            for row in self.grid:
                for c in row:
                    f.write(c.bin_to_hex())
                f.write('\n')
            f.write('\n')
            f.write(f"{self.entry_p[0]},{self.entry_p[1]}\n")
            f.write(f"{self.exit_p[0]},{self.exit_p[1]}\n")
            if self.shortest_path:
                dir_output: list[str] = get_path_directions()
                for di in dir_output:
                    f.write(f"{di}")
                f.write('\n')
