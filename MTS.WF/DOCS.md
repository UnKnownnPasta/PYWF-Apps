# WF Tile Checker Documentation

The WF Tile Checker is a small program that monitors the WF game log for certain keywords related to the current mission. It will display the current mission information and the number of players in the mission.

## Currently Displayed Information

* Current mission name # TODO
* Quality of tilesets in the mission
* Relative location of tileset
* Number of players in the mission # TODO
* Mission type (e.g. Capture, Interception, etc.) # TODO
* Mission location (e.g. Mercury, Venus, etc.) # TODO
* Mission objective (e.g. Capture the enemy ship, etc.) # TODO

## How it Works

The program uses the WF game log (EE.log) to determine the current mission information. It searches for certain keywords in the log file and uses that information to display the mission details.

## Requirements

* Python 3.6 or higher must be installed

## Installation

1. Download the latest release of the program from the [releases page](https://github.com/UnKnownnPasta/WF-Tile-Checker/releases).
2. Extract the zip file to a directory of your choice.
3. Run the program by double-clicking on `MissionTileChecker.py`.

## Configuration

As of now, only overlay toggling is available.