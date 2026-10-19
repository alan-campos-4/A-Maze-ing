from enum import Enum
from typing_extensions import Self


class Direction(Enum):
    """Directions

    Contains the possible directions to travel within the dimensions
    of the maze.
    """
    WEST = 0
    SOUTH = 1
    EAST = 2
    NORTH = 3

    def get_movement(self) -> tuple[int, int]:
        """Return the displacement of each direction."""
        if self.value == 0:
            return (-1, 0)
        elif self.value == 1:
            return (0, +1)
        elif self.value == 2:
            return (+1, 0)
        else:
            return (0, -1)

    def opposite(self) -> Self:
        """Return the opposite direction."""
        di: int = self.value + 2
        if di > 3:
            di -= 4
        return Direction(di)

    def next(self) -> Self:
        """Return the next direction clockwise."""
        di = self.value + 1
        if di > 3:
            di = 0
        return Direction(di)
