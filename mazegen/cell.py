from .movement import Direction


class Cell():
    """A cell of the maze.

    Contains its coordinate within the maze, the values of its walls
    (True if it exists) and whether it's part of the valid path.

    The walls are stored as a list of Direction objects, where a unique
    Direction value is found if a wall exists in that direction.

    Any cell can be converted to a hexadecimal value.
    """
    x: int
    y: int
    _walls: list[Direction]
    path: bool

    def __init__(self, px: int, py: int, value: bool) -> None:
        """Initialize the configuration with the given values.

        For the purposes of this project, all cells will be initialized
        as surrounded by walls on all sides."""
        self.x = px
        self.y = py
        self.path = False
        self._walls = [d for d in Direction]

    # ==============================
    # GET FUNCTIONS
    # ==============================

    def get_west(self) -> bool:
        """Return the wall value"""
        return (Direction.WEST in self._walls)

    def get_south(self) -> bool:
        """Return the wall value"""
        return (Direction.SOUTH in self._walls)

    def get_east(self) -> bool:
        """Return the wall value"""
        return (Direction.EAST in self._walls)

    def get_north(self) -> bool:
        """Return the wall value"""
        return (Direction.NORTH in self._walls)

    def get_walls(self) -> list[Direction]:
        """Return the directions of cell's walls where are true.

        Create a new list so as to not return a reference."""
        ls: list[Direction] = []
        for w in self._walls:
            ls.append(w)
        return ls

    def is_full(self) -> bool:
        """Returns whether all the wall values are true."""
        return (self.get_north() and self.get_south() and
                self.get_west() and self.get_east())

    # ==============================
    # ADDITIONAL FUNCTIONS
    # ==============================

    def break_wall(self, direction: Direction) -> None:
        """Break the wall in the direction given."""
        if direction in self._walls:
            self._walls.remove(direction)

    def bin_to_hex(self) -> str:
        """Returns a hexadecimal character based on the binary values."""
        d: int = int(self.get_west())
        c: int = int(self.get_south())
        b: int = int(self.get_east())
        a: int = int(self.get_north())
        num_value: int = (d * 8 + c * 4 + b * 2 + a * 1)
        if (0 <= num_value <= 9):
            return chr(num_value + 48)
        else:
            return chr(num_value + 87)
