"""
Filename: main.py
Author: Reuben James
Date: 05-08-2025
Description: Utility script to move a large upload of Nikon RAW images into folders organised destination/YYYY/MM/DD
"""

import datetime
import shutil
from pathlib import Path
from stat import S_ISREG, ST_MODE, ST_MTIME
import os
import time
from collections import defaultdict
from tqdm import tqdm

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}

print(
"""
------------------------------------------------------------------------------------------------------------------------
| Moves all NEF files from a single folder to a specified location in an date-organised folder, YYYY -> MM -> DD       |
|                                                                                                                      | 
| This does not use EXIF data to find chronological order, rather modified time. This works on windows, but may behave | 
| differently across different operating systems. Test on small data sets first, and backup files before use.          | 
|                                                                                                                      | 
| Any existing edits that are not applied directly to the RAW files (e.g. any from NX Studio or in-camera settings     | 
| including noise reduction) will be lost. Run this before editing files. If files are already edited use NX Studio to | 
| move files.                                                                                                          |
|                                                                                                                      | 
| Destination path must be the directory which contains the year directories, not a year directory.                    |  
------------------------------------------------------------------------------------------------------------------------
""")

src = input("Absolute source path: ")
dest = input("Absolute destination path: ")

move_start = datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d %H.%M.%S")
# Add operation time to avoid folder name collisions with previous moves

# Get all files and paths
data = (os.path.join(src, fn) for fn in os.listdir(src))
data = ((os.stat(path), path) for path in data)
data = ((stat[ST_MTIME], path) for stat, path in data if S_ISREG(stat[ST_MODE]))

# Store in dictionary as file moving will be slow
changes = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # {year: {month: {day: [[source, destination]]}}
total_items = 0

for cdate, path in data:
    date = time.gmtime(cdate)
    name = os.path.basename(path)
    file_dest = Path(dest) / str(date.tm_year) / f"{date.tm_mon:02d}" / f"{date.tm_mday:02d} - MOVED {move_start}"

    if os.path.splitext(name)[1].lower() in VIDEO_EXTENSIONS:
        file_dest /= "Videos"

    file_dest /= name

    changes[date.tm_year][date.tm_mon][date.tm_mday].append([path, file_dest])
    total_items += 1

errors = list()

# Use dictionary to move files
with tqdm(total=total_items, desc="Moving files", unit="file") as progress_bar:
    for year in changes:
        for mon in changes[year]:
            for day in changes[year][mon]:
                for file_src, file_dest in changes[year][mon][day]:
                    progress_bar.set_description(f"Moving {os.path.basename(file_src)}")

                    try:
                        shutil.move(file_src, file_dest)
                    except FileNotFoundError:  # Folder is not created
                        folder = os.path.dirname(file_dest)
                        os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                        shutil.move(file_src, file_dest)
                    except Exception as e:  # Prevent failure of subsequent files
                        errors.append((file_src, file_dest, e))

                    progress_bar.update(1)
    progress_bar.set_description(f"Moved files")

# Process errors
if len(errors):
    print(f"Errors occurred moving {len(errors)} files. Review the following files manually:")
    for source, destination, error in errors:
        print(f"\t{source} -> {destination}\t {error}")