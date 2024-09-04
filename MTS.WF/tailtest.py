import time
from typing import Iterator
import os

KEYWORDS = {
    "MSN_START": "Script [Info]: ThemedSquadOverlay.lua: Lobby::Host_StartMatch",
    "MSN_END1": "Script [Info]: TopMenu.lua: Abort",
    "MSN_END2": "Script [Info]: EndOfMatch.lua",
    "IN_ORBITER": "Game successfully connected to: /Lotus/Levels/Proc/PlayerShip/",
    "TILE_LOAD": "Game [Info]: Added streaming layer",
    "MSN_SELECTED": "Script [Info]: ThemedSquadOverlay.lua: Pending mission:",
    "MSN_UNSELECTED": "Script [Info]: ThemedSquadOverlay.lua: ResetSquadMission",
    "GAME_CLOSED": "Sys [Info]: Main Shutdown Complete."
}

def follow(file, sleep_sec=0.1) -> Iterator[str]:
    """ Yield each line from a file as they are written.
    `sleep_sec` is the time to sleep after empty reads. """
    line = ''
    while True:
        tmp = file.readline()
        if tmp is not None and tmp != "":
            line += tmp
            if line.endswith("\n"):
                yield line
                line = ''
        elif sleep_sec:
            time.sleep(sleep_sec)


if __name__ == '__main__':
    with open(os.getenv('LOCALAPPDATA') + r'\Warframe\EE.log', 'r', encoding='utf-8') as file:
        for line in follow(file):
            if KEYWORDS["GAME_CLOSED"] in line:
                print(line)
            elif KEYWORDS["IN_ORBITER"] in line:
                print(line)
            elif KEYWORDS["TILE_LOAD"] in line:
                print(line)
            elif KEYWORDS["MSN_START"] in line:
                print(line)
            elif KEYWORDS["MSN_END1"] in line:
                print(line)
            elif KEYWORDS["MSN_END2"] in line:
                print(line)
            elif KEYWORDS["MSN_SELECTED"] in line:
                print(line)
            elif KEYWORDS["MSN_UNSELECTED"] in line:
                print(line)