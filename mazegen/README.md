*This project has been created as part of the 42 curriculum by paduarte and alvespin.*

# mazegen package

The maze generator and solver portion of the project.

<br>

## Parameters

In order to instantiate a MazeGenerator object, you will use these parameters.

#### Mandatory values

| Key     | Format |
|---------|--------|
| `WIDTH` | Positive integer above 9 |
| `HEIGHT` | Positive integer above 7 |
| `ENTRY / EXIT` | Positive integers forming coordinates like 0,0. Max value is width or height - 1. |
| `OUTPUT_FILE` | Where the results will be saved |
| `PERFECT` | Either True or False |

#### Optional values

| Key | Format |
|-----|--------|
| `SEED` | Positive integer. Change the seed of all randomization during the maze's generation |

<br>

## Output file

The `save()` function receives will write the structure and a solution to the maze to a file.

#### Result layout

```
b9157913d13953d55157    # Maze grid (hexadecimal)
aea956ac56c6d4553853
c3aa97af953fff956c3a
ba86a96fc7857fad13aa
...

0,0                     # Entry point
18,7                    # Exit point
SSESSWSESESENENENNE...  # Shortest path (N/E/S/W)
```

#### Wall enconding

```
                W S E N   Hex
      N         0 0 0 0    0    # All walls open
    +---+       0 0 0 1    1    # Only North closed
  W |   | E     0 0 1 0    2    # Only East closed
    +---+       0 1 1 0    6    # East and South closed
      S         1 0 1 1    b    # Only South open
                1 1 1 1    f    # All walls closed
```

<br>

## Usage

```bash
# Create a new virtual environment and install the package.
python3 -m venv .venv
source .venv/bin/activate
pip install mazegen-1.0.0-py3-none-any.whl
```

### Example

You can now use the module within a python file, like this:

```python
# Import the module
from mazegen import MazeGenerator

# Instantiate the generator, with a basic example input.
# In order: width, height, entry, exit, perfect and seed
M = MazeGenerator(15, 10, (0,0), (14,9), True, 0)
# Generate the maze and the solution.
M.generate()
# Save the maze and its parameters to a file.
M.save('maze.txt')
```

### Result

Content of the output file (maze.txt)
```
d39539555395553
96abaab956a93d2
c56ac6aad542c3a
9512f92afffa96a
a96afec057fea96
aad6fffafff96c3
ac5553fafd52d3a
c3d396fafff83aa
9692c17c53d6aaa
c56c7c5554556c6

0,0
14,9
ESWSEENNEESSENNEEEESWWSSSSSSSEESEEENNWNNENNENWNWSWNNEEEESSSSWSESSSS
```
