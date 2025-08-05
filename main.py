import datetime
import shutil
from pathlib import Path
from stat import S_ISREG, ST_CTIME, ST_MODE, ST_MTIME
import os, sys, time
from collections import defaultdict

src = input("Source: ")
dest = input("Destination: ")


data = (os.path.join(src, fn) for fn in os.listdir(src))
data = ((os.stat(path), path) for path in data)
data = ((stat[ST_MTIME], path) for stat, path in data if S_ISREG(stat[ST_MODE]))

changes = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # {year: {month: {day: [[source, destination]]}}

move_start = datetime.datetime.strftime(datetime.datetime.now(), "%Y.%m.%d %H.%M.%S")

for cdate, path in data:
    date = time.gmtime(cdate)
    name = os.path.basename(path)
    file_dest = Path(dest) / str(date.tm_year) / f"{date.tm_mon:02d}" / f"{date.tm_mday:02d} - MOVED {move_start} - {name}"
    changes[date.tm_year][date.tm_mon][date.tm_mday].append([path, file_dest])

for year in changes:
    for mon in changes[year]:
        for day in changes[year][mon]:
            for file_src, file_dest in changes[year][mon][day]:
                print(f"Moving {file_src} -> {file_dest} ... ", end="")

                try:
                    shutil.move(file_src, file_dest)
                    print(f"SUCCESS")
                except FileNotFoundError:
                    folder = os.path.dirname(file_dest)
                    os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                    shutil.move(file_src, file_dest)
                    print(f"SUCCESS")
                except Exception as e:
                    print(f"FAILURE {e}")