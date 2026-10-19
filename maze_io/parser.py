from sys import exit
from typing import Any
from mazegen import Position


class ConfigError(Exception):
    def __init__(self, message: str = "Unknown config error") -> None:
        self.message = message


class Config:
    """Stores and validates the maze configuration settings.

    This class contains all configurable parameters required to generate
    and display a maze, including its dimensions, random seed, entry and
    exit positions, and output file.
    """

    def __init__(self) -> None:
        self.seed: int = 0

    def __fill(self, data: dict[str, Any]) -> None:
        """Populate the configuration object with parsed values.

        Each key in the input dictionary is assigned to the corresponding
        attribute if it exists. Invalid attribute names are reported.

        Args:
            data: A dictionary containing configuration values.

        Returns:
            None
        """
        for key, value in data.items():
            if key == "width":
                self.width: int = value
            elif key == "height":
                self.height: int = value
            elif key == "seed":
                self.seed = value
            elif key == "perfect":
                self.perfect: bool = value
            elif key == "entry":
                self.entry: Position = assign_point(value,
                                                    self.width, self.height)
            elif key == "exit":
                self.exit: Position = assign_point(value,
                                                   self.width, self.height)
            elif key == "output_file":
                self.output_file: str = value
            else:
                raise ConfigError(f"'{key}' is not a valid"
                                  " attribute of Config")

    def __check_mandatory(self) -> None:
        """Check this instance has all mandatory config attributes.

        Raises:
            ConfigError: If one of the mandatory attributes is missing.
        """
        mandatory_atts = ['width', 'height', 'entry', 'exit', 'output_file',
                          'perfect']
        if not all(ma in list(self.__dict__.keys()) for ma in mandatory_atts):
            raise ConfigError("Some mandatory config attribute is missing")

    def __check_entry_exit(self) -> None:
        """Check ENTRY and EXIT as valid points.

        Assures both values are different and inside the maze.

        Raises:
            ConfigError if out of range or same exit and entry points
        """
        if self.entry == self.exit:
            raise ConfigError("Entry and Exit points cannot be equal")

    def read_from_file(self, filename: str) -> None:
        """Read configuration values from a file and populate a Config object.

        Blank lines and comments are ignored. Each valid configuration entry
        is parsed and stored in the provided configuration object.

        Args:
            filename: The path to the configuration file.

        Raises:
            Exception: Any exception raised while opening or reading the file
                is caught and printed.
        """
        try:
            config_data: dict[str, str] = {}
            with open(filename, encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line or line.startswith("#"):
                        continue
                    else:
                        try:
                            key, value = line.split("=", 1)
                            if key.startswith(" ") or key.endswith(" "):
                                raise ConfigError("Invalid syntax for config")
                            elif value.startswith(" ") or value.endswith(" "):
                                raise ConfigError("Invalid syntax for config")
                        except (ValueError, ConfigError):
                            print("Error: Invalid Syntax for config "
                                  f"data: '{line}'")
                            exit()
                        try:
                            parsed = parse_value(key, value)
                            config_data.update({key.lower(): parsed})
                        except ValueError:
                            print("Error: Invalid config data")
                            exit()
                validate_values(config_data)
                self.__fill(config_data)
                self.__check_mandatory()
                self.__check_entry_exit()
        except Exception as e:
            print(e)
            exit()


def parse_value(key: str, value: str) -> Any:
    """Convert a configuration value from string to its appropriate type.

    Integer, boolean, and coordinate values are parsed according to their
    corresponding configuration keys. All other values are returned as
    strings.

    Args:
        key: The configuration key.
        value: The configuration value as read from the file.

    Returns:
        The parsed value with the appropriate Python type.

    Raises:
        ConfigError: If the value of the 'PERFECT' option is not
            'True' or 'False'.
    """
    key = key.strip()
    value = value.strip()
    if key in ("WIDTH", "HEIGHT", "SEED"):
        return int(value)
    if key == "PERFECT":
        if value == "True":
            return True
        elif value == "False":
            return False
        raise ConfigError("PERFECT must be True or False")
    if key in ("ENTRY", "EXIT"):
        x, y = value.split(",")
        return (x, y)
    return value


def validate_values(data: dict[str, Any]) -> None:
    """Validates seed value and the maze dimensions to ensure they meet
    the minimum supported size.

    Args:
        data: A dictionary containing configuration keys and values.

    Raises:
        ValueError: If there is a non-valid value.
    """

    def validate_width_height(key: str, value: int) -> None:
        """Checks that the width or height is within the valid range.

        Args:
            key: The dictionary key, either 'width' or 'height'.
            value: The dictionary value.

        Raises:
            ValueError: If the value is not in the valid range.
        """
        min: int = 0
        if key == "width":
            min = 9
        else:
            min = 7
        if value < 0:
            raise ValueError(f"Maze {key} cannot be negative")
        if value < min:
            raise ValueError(f"Maze {key} should be {min} or a bigger value")
        if value > 42:
            raise ValueError(f"Maze {key} should be 42 or a smaller value")
        print(f"{key} validated")

    def validate_coordinate(key: str, x: str, limit: int) -> None:
        """Checks that the entry or exit is within the valid range.

        Args:
            key:    The dictionary key, either 'entry' or 'exit'.
            x:      The coordinate value, 'x' or 'y'.
            limit:  The limit of the coordiante value, 'width' or 'height'.

        Raises:
            ValueError: If the value is not in the valid range.
        """
        x1: int
        if x == "max":
            print("max found")
            x1 = limit
        else:
            try:
                x1 = int(x)
            except ValueError:
                raise ValueError(f"Invalid value for {key}")
            if x1 < 0:
                raise ValueError(f"{key} cannot be negative")
            elif x1 >= limit:
                raise ValueError(f"{key} exceeds maze bounds")
        print(f"{key} validated")

    for key, value in data.items():
        if key == "width" or key == "height":
            validate_width_height(key, value)
        if key == "entry" or key == "exit":
            x, y = value
            validate_coordinate(key, x, data['height'] - 1)
            validate_coordinate(key, y, data['width'] - 1)
        if key == "seed":
            if value < 1:
                raise ValueError("Seed value must be a positive number")
        if key == "output_file":
            if not value:
                raise ValueError("Output file name is empty")
    print("data validated")


def assign_point(value: tuple[str, str], h: int, w: int) -> tuple[int, int]:
    """Return the entry and exit values read to the Config object

    Args:
        value:  a tuple containing the x and y text read from the file.
        h:      the height of the maze.
        w:      the width of the maze.

    Returns:
        a corresponding tuple of integers.
    """

    def check_max(val: str, limit: int) -> int:
        """Return either the maximum value for the variable, or the
        correspoding integer"""
        if val == "max":
            return limit
        else:
            return int(val)

    x, y = value
    x1 = check_max(x, h - 1)
    y1 = check_max(y, w - 1)
    return x1, y1
