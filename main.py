"""
Filename: main.py
Author: Reuben James
Date: 05-08-2025
Description: Simple utility script to move a large upload of Nikon RAW images into folders organised src/YYYY/MM/DD
"""

import datetime
import shutil
from pathlib import Path
from stat import S_ISREG, ST_MODE, ST_MTIME
import os
import time
from collections import defaultdict

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

# Get all files and paths
data = (os.path.join(src, fn) for fn in os.listdir(src))
data = ((os.stat(path), path) for path in data)
data = ((stat[ST_MTIME], path) for stat, path in data if S_ISREG(stat[ST_MODE]))

# Store in dictionary as file moving will be slow
changes = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # {year: {month: {day: [[source, destination]]}}

for cdate, path in data:
    date = time.gmtime(cdate)
    name = os.path.basename(path)
    file_dest = Path(dest) / str(date.tm_year) / f"{date.tm_mon:02d}" / f"{date.tm_mday:02d} - MOVED {move_start} - {name}"
    changes[date.tm_year][date.tm_mon][date.tm_mday].append([path, file_dest])

# Use dictionary to move files
for year in changes:
    for mon in changes[year]:
        for day in changes[year][mon]:
            for file_src, file_dest in changes[year][mon][day]:
                print(f"Moving {file_src} -> {file_dest} ... ", end="")

                try:
                    shutil.move(file_src, file_dest)
                    print(f"SUCCESS")
                except FileNotFoundError:  # Folder is not created
                    folder = os.path.dirname(file_dest)
                    os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                    shutil.move(file_src, file_dest)
                    print(f"SUCCESS")
                except Exception as e:  # Prevent failure of subsequent files
                    print(f"FAILURE {e}")