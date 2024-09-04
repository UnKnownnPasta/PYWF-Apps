"""
Warframe Tile Checker - Updated 22-08-24 //

Bug/Issue/Feature report @ https://github.com/UnKnownnPasta/WF-Tile-Checker
"""


import logging
import tkinter as tk
import os
import sys
import signal
import time
import ctypes
import urllib
import urllib.error
import urllib.request
import threading

#----------------- details

VERSION = "0.3"
logging.basicConfig(level=logging.INFO)
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

#----------------- overlay class

class Overlay(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        
        # - Pre req.
        self.good_tiles = get_tiledata()
        self.max_width = int(self.winfo_screenwidth() // 2.4)

        # check for env LOCALAPPDATA then gets EE.log
        self.LOGFILEPATH = define_logpath()

        # - Overlay details
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)
        self.attributes("-transparentcolor", self['bg'])
        self.geometry(f"{self.max_width}x{600}+0+0")
        make_clickthrough(self)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        signal.signal(signal.SIGINT, self.on_sigint)

        # - Label details
        self.ol_title = f"=== WF Tile Checker // ver {VERSION}"
        self.ol_error = "" # filled with errors if needed
        self.ol_array = []

        constructed_text = f"{self.ol_title}\n{self.ol_error}\n"
        self.ol = tk.Label(self, text=constructed_text, font=("Terminal", 11), fg="white",
                            wraplength=self.max_width, justify="left")
        self.ol.place(x=3, y=3)

        # - Mission details frame
        self.frame = tk.Frame(self)
        self.frame.place(y=80, x=3)

        # - start tail
        self.start_tail()


    def start_tail(self):
        self.log_thread  = threading.Thread(target=self.follow_logs)
        self.stop_event = threading.Event()
        self.log_thread.daemon = True
        self.log_thread.start()


    def ol_update_text(self, text):
        constructed_text = ""
        if self.ol_error:
            constructed_text = f"{self.ol_title}\n{self.ol_error}\n{text}"
        else:
            constructed_text = f"{self.ol_title}\n{text}"
        self.ol.config(text=constructed_text)


    def follow_logs(self):
        TacMap_Lines = []
        at_msn_start = False

        verdict_text = ""

        logging.info("Awaiting log file...")
        with open(self.LOGFILEPATH, 'r', encoding='utf-8') as file:
            if KEYWORDS["GAME_CLOSED"] in file.read():
                self.ol_update_text("Game closed. Reopen the app when it's back up.")
                self.stop_event.set()
                return;

            for line in self.follow(file):
                if self.stop_event.is_set():
                    break;

                # - check for keyword conditions
                if KEYWORDS["MSN_SELECTED"] in line and not at_msn_start:
                    verdict_text = "Mission queued."
                    continue
                elif KEYWORDS["MSN_START"] in line and not at_msn_start:
                    at_msn_start = True
                    continue
                elif (KEYWORDS["MSN_UNSELECTED"] in line or KEYWORDS["IN_ORBITER"] in line) and not at_msn_start:
                    verdict_text = "Currently in orbiter"
                    continue
                elif (KEYWORDS["MSN_END1"] in line or KEYWORDS["MSN_END2"] in line) and at_msn_start:
                    at_msn_start = False
                    verdict_text = "Mission ended."
                    self.clear_actl()
                    TacMap_Lines.clear()
                    continue
                elif at_msn_start:
                    verdict_text = "Mission started."
                    if KEYWORDS["TILE_LOAD"] in line:
                        TacMap_Lines.append(line)
                    continue

                # - check if tile load
                if TacMap_Lines:
                    self.check_tiles(TacMap_Lines)
                else:
                    self.ol_update_text(verdict_text)


    def clear_actl(self):
        if self.ol_array:
            for label in self.ol_array:
                label.destroy()
            self.ol_array.clear()


    def follow(self, file, sleep_sec=0.1):
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
                if self.stop_event.is_set(): 
                    break;
                else: 
                    time.sleep(sleep_sec)


    def check_tiles(self, TacMaps):
        self.clear_actl()

        accepted_tiles = []
        found_tiles = []

        for tile_1 in TacMaps:
            text = tile_1.split(" ")
            if len(text) < 6: continue
            thing = text[6].split("/")
            if len(thing) < 4: continue
            found_tiles.append(thing[4])
        
        for j, tile_0 in enumerate(found_tiles):
            if tile_0 in self.good_tiles:
                status = ""
                if j < 3: status = "Close"
                elif j >= 3 and j < 8: status = "Far"
                elif j >= 8: status = "Very far"

                accepted_tiles.append([status, tile_0])

        # display image + label
        for i, tile in enumerate(accepted_tiles):
            # Create an image object
            imgurl = f"./ppm/{tile[1]}.ppm"
            image = tk.PhotoImage(file=f"{imgurl}")
            img_label = tk.Label(self.frame, image=image)
            img_label.image = image
            img_label.grid(row=i, column=0, padx=10, pady=5)

            # Create the label
            text_label = tk.Label(self.frame, text=f"Location: {tile[0]}\nInternal: {tile[1]}", justify='left', font=("Terminal", 11), fg="white")
            text_label.grid(row=i, column=1, padx=10, pady=5, sticky="w")

            self.ol_array.extend([img_label, text_label])

        self.ol_update_text(f"Found {len(accepted_tiles)} good tile(s).")


    def on_close(self):
        logging.info("Closing App")
        self.stop_event.set()
        self.log_thread.join()
        sys.exit(0)


    def on_sigint(self, signum, frame):
        logging.warning("SIGINT received, closing App")
        self.on_close()


    def toggle_visibility(self):
        if self.state() == 'withdrawn':
            self.deiconify()
            return 'Visible'
        else:
            self.withdraw()
            return 'Hidden'

#----------------- main function

def main():
    root = tk.Tk()
    
    # -- Root window properties
    root.geometry("300x30")
    root.title("WFTC Overlay")
    root.overrideredirect(False)
    root.resizable(False, False)

    # -- Creating overlay
    overlay = Overlay(root)

    # -- Toggle Button to hide/show overlay
    def toggle_overlay():
        status = overlay.toggle_visibility()
        status_label.config(text=f"[ {status} ]")

    toggle_button = tk.Button(root, text="  Toggle Overlay  ", command=toggle_overlay, bd=0,
                              background="#24a0ed", activebackground="#237fb7")
    toggle_button.place(x=5, y=5)

    status_label = tk.Label(root, text="[ Visible ]", font=("Helvetica", 10, "normal"))
    status_label.place(x=99, y=5)

    # -- Start
    logging.info("App ready")
    root.mainloop()

#----------------- other

def make_clickthrough(item):
    hwnd = ctypes.windll.user32.GetParent(item.winfo_id())
    style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongPtrW(hwnd, -20, style | 0x80000 | 0x20)

def test_log_line(line):
    if not line:
        return False
    elif not line[0].isdigit():
        return False
    else:
        return True

def define_logpath():
    localenv = os.getenv('LOCALAPPDATA')

    if not localenv:
        tk.messagebox.showerror("Error", "App could not find EE.log, are you sure warframe is installed correctly?")
        sys.exit()
    else:
        return localenv + r'\Warframe\EE.log'

def fetch_url(url="", max_retries=5, delay=2):
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url) as response:
                text_data = response.read().decode('utf-8')

                return text_data
        except urllib.error.HTTPError as e:
            logging.warning(f"Failed to retrieve URL Data: {url}\n{e}\n{'' if attempt == 4 else f'Retrying in {delay}s...'}")
            time.sleep(delay)
        except urllib.error.URLError as e:
            logging.warning(f"URL Error: {e}\n{'' if attempt == 4 else f'Retrying in {delay}s...'}")
            time.sleep(delay)

    return ""

def get_tiledata():
    # pastebin of all good tilesets
    tile_data = fetch_url("https://pastebin.com/raw/u2jprqZ4")

    filtered_tile_data = []

    if not tile_data:
        logging.warning("Failed to fetch tile data.")
        return []

    for line in tile_data.split("\n"):
        if line != "\r" and not line.startswith("#"):
            filtered_tile_data.append(line.replace("\r", ""))

    logging.info(f"Fetched [{len(filtered_tile_data)}] tilesets")
    return filtered_tile_data

#----------------- start

if __name__ == "__main__":
    logging.info("Starting")
    main()