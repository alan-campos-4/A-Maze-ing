#!/usr/bin/python3

import sys
from maze_io import Config, Visualizer
from mazegen import MazeGenerator


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: file not found")
        exit()
    config: Config = Config()
    config.read_from_file(sys.argv[1])
    M = MazeGenerator(config.width, config.height, config.entry,
                      config.exit, config.perfect, config.seed)
    vis: Visualizer = Visualizer()
    M.generate()
    vis.run_visualizer(M)
    M.save(config.output_file)
