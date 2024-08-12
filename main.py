from typing import List

import tkinter as tk
import os
import signal
import time
import urllib
import urllib.error
import urllib.request


def get_tiledata(max_retries=5, delay=2):
    # just so the url doesnt look long
    base_url = "gist.githubusercontent.com"
    gist_id = "b6347940fde557cc081853d3d254f449"
    file_id = "d1a57b3e8d8c7bb19eb7cac3d07d15a0ab61d245"
    file_name = "WFTC_Tilesets.txt"

    url = f"https://{base_url}/UnKnownnPasta/{gist_id}/raw/{file_id}/{file_name}"

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url) as response:
                text_data = response.read().decode('utf-8')
                return text_data.split("\n")
        except urllib.error.HTTPError as e:
            print(f"Failed to retrieve Tileset Data: {e}\n\nRetrying in {delay}s...")
            time.sleep(delay)
        except urllib.error.URLError as e:
            print(f"URL Error: {e}\n\nRetrying in {delay}s...")
            time.sleep(delay)

    print("Failed to retrieve data after several attempts.")
    return []


class WFTCOverlay(tk.Toplevel):
    def __init__(self, root, log_file):
        super().__init__(root)

        # -- Pre-req.
        self.possible_roots = get_tiledata()
        self.log_file = log_file
        self.max_width = int(self.winfo_screenwidth() // 2.4)

        # -- Overlay and label properties
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)
        self.attributes("-transparentcolor", self['bg'])
        self.geometry(f"{self.max_width}x{300}+0+0")

        self.label = tk.Label(self, text="Loading..", font=("Helvetica", 10, "normal"), fg="white",
                              wraplength=self.max_width, justify="left")
        self.label.place(x=3, y=3)

        # -- stuff
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.read_logs()


    # -- Updating label text based on log file
    def update_label(self, label_text):
        base_label_text = "~~ Tile Checker v1\n"

        self.label.config(text=f"{base_label_text}{label_text}")


    # -- Scanning log file
    def read_logs(self):
        try:
            keyword = "TacticalAreaMap"
            recent_lines = []
            highest_time = None

            with open(self.log_file, "r") as file:
                lines = file.readlines()

                if lines[-1].find("Shutdown") != -1:
                    self.update("Game not Active.")
                    self.after(100, self.read_logs)
                    return None;

                for line in lines:
                    if keyword in line:
                        time_str = line.split()[0]
                        current_time = float(time_str)

                        if highest_time is None or current_time > highest_time:
                            highest_time = current_time
                            recent_lines = [line]
                        elif current_time == highest_time:
                            recent_lines.append(line)

            if recent_lines:
                self.determine_quality(recent_lines)

            self.after(100, self.read_logs)

        except FileNotFoundError:
            self.label.config(text=f"{self.base_label_text}Log file not found.")
            self.after(1000, self.read_logs)


    # -- Main function to determine quality of tileset
    def determine_quality(self, tacmaps: List[str]):
        extracted_tiles = []

        for map_entry in tacmaps:
            formatted_text = map_entry.split(" ")[4].split('/')

            if len(formatted_text) < 5:
                continue

            extracted_tiles.append(formatted_text[-2])

        if any(tile in self.possible_roots for tile in extracted_tiles):
            self.update_label("Good tile spawn found.")
        else:
            self.update_label("Bad tile spawns.")

    # -- Cleanup function for exiting program
    def on_close(self):
        self.after_cancel(self.read_logs)
        os.kill(os.getpid(), signal.SIGINT)

def main():
    root = tk.Tk()
    
    # -- Root window properties
    root.geometry("300x0")
    root.title("WFTC Overlay")
    root.overrideredirect(False)
    root.resizable(False, False)
    # root.withdraw()

    # -- Log file path
    log_file = os.getenv('LOCALAPPDATA') + r'\Warframe\EE.log'

    # -- Creating overlay
    overlay = WFTCOverlay(root, log_file)
    overlay.mainloop()

if __name__ == "__main__":
    main()
