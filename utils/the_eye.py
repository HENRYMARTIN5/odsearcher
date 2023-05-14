import os
import fuzzysearch
import json
import psutil
import time
from datetime import timedelta

def register_args(parser):
    parser.add_argument('--eye-only', action='store_true', help='Only search the-eye.eu. Useful if you\'re looking for something specific and don\'t want to wait for the other sites to search.')
    parser.add_argument('-n', '--no-eye', action='store_true', help='Do not search the-eye.eu. Generally useful if you\'re constrained by disk space, since the index alone is 3gb.')
    parser.add_argument('--eye-no-nonpiracy', action='store_true', help='Do not perform a search of the-eye\'s non-piracy database')
    parser.add_argument('--eye-no-piracy', action='store_true', help='Do not perform a search of the-eye\'s piracy database - reccomended for systems on low RAM, the database is 4gb in RAM.')

def ensure_db_downloaded():
    if (not os.path.exists('dbWithNoPiracyFolder.json') or not os.path.exists("dbPiracy.json")) and not os.path.exists(".fixed_dbs"):
        return False
    return True

reserved = ["url", "date", "success", "type", "size"]

def percentage(part, whole):
    return (100 * float(part)/float(whole))

def do_search(name, args):
    if args.no_eye:
        return [], 0
    if not ensure_db_downloaded():
        print("Database not found. Please download it from: https://drive.google.com/drive/folders/1kf4lTu3-ZMlUveiCQL_B7qYZm0WAHKKB. Then, put the files in the same folder as the `searcher.py` script.")
        return [], 0
    if not os.path.exists(".fixed_dbs"):
        print("Database not yet fixed. Automatically fixing...")
        print("1/2 - Fixing non-piracy database...")
        os.system("python3 utils/eyefixer.py dbWithNoPiracyFolder.json dbWithNoPiracyFixed.json")
        print("2/2 - Fixing piracy database...")
        os.system("python3 utils/eyefixer.py dbPiracy.json dbPiracyFixed.json")
        print("Done. Deleting old databases...")
        os.remove("dbWithNoPiracyFolder.json")
        os.remove("dbPiracy.json")
        with open(".fixed_dbs", "w") as f:
            f.write("hi :)")
    found = []
    total = 0
    if not args.eye_no_nonpiracy:
        with open('dbWithNoPiracyFixed.json', 'r', errors='replace') as f:
            print("Loading into RAM...")
            db = f.read()
            print("Calculating length...")
            length = len(db.split("\n"))
            curindex = 0
            previous_percentage = 0
            # loop through key-value pairs
            _found = []
            _total = 0
            start_time = time.time()
            time_reached_1 = False
            for line in db.split("\n"):
                if percentage(curindex, length) - previous_percentage > 0.01:
                    previous_percentage = percentage(curindex, length)
                    if not time_reached_1:
                        print(str(round(previous_percentage, 3)) + "% done. ETA: unknown, Found: " + str(len(_found)) + "           \r", end="")
                        if round(previous_percentage) % 2 == 0 :
                            time_reached_1 = time.time() - start_time
                            start_time = time.time()
                    else:
                        print(str(round(previous_percentage, 3)) + "% done. ETA: " + str(timedelta(seconds=round(time_reached_1*(100-previous_percentage)))) + ", Found: " + str(len(_found)) + "           \r", end="")
                    
                line = line.strip()
                if line.startswith("\"url\": "):
                    url = line[8:-2]
                    if fuzzysearch.find_near_matches(name, url.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "."), url.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "_"), url.lower(), max_l_dist=1):
                        _found.append(url)
                        _total += 1
                curindex += 1
            if _total > 0:
                print("Found " + str(_total) + " results in the-eye.eu database.")
                for find in _found:
                    found.append(find)
                    total += 1
    if not args.eye_no_piracy:
        ram = psutil.virtual_memory()
        if ram.total < 4294967296:
            print("Warning: your system has less than 4GB of RAM. This may cause the database to crash during searching. If this happens, please use the `--the-eye-no-piracy` flag.")
        with open('dbPiracyFixed.json', 'r', errors='replace') as f:
            print("Loading into RAM...                           ")
            db = f.read()
            print("Calculating length...")
            length = len(db.split("\n"))
            curindex = 0
            previous_percentage = 0
            # loop through key-value pairs
            _found = []
            _total = 0
            start_time = time.time()
            time_reached_1 = False
            for line in db.split("\n"):
                if percentage(curindex, length) - previous_percentage > 0.01:
                    previous_percentage = percentage(curindex, length)
                    if not time_reached_1:
                        print(str(round(previous_percentage, 3)) + "% done. ETA: unknown, Found: " + str(len(_found)) + "           \r", end="")
                        if round(previous_percentage) % 2 == 0 :
                            time_reached_1 = time.time() - start_time
                            start_time = time.time()
                    else:
                        print(str(round(previous_percentage, 3)) + "% done. ETA: " + str(timedelta(seconds=round(time_reached_1*(100-previous_percentage)))) + ", Found: " + str(len(_found)) + "           \r", end="")
                    
                line = line.strip()
                if line.startswith("\"url\": "):
                    url = line[8:-2]
                    if fuzzysearch.find_near_matches(name, url.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "."), url.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "_"), url.lower(), max_l_dist=1):
                        _found.append(url)
                        _total += 1
                curindex += 1
            if _total > 0:
                print("Found " + str(_total) + " results in the-eye.eu database.")
                for find in _found:
                    found.append(find)
                    total += 1
    fixedfinds = []
    for find in found:
        if not find.startswith("http://the-eye.eu/public/") or not find.startswith("https://the-eye.eu/public/"):
            fixedfinds.append("https://the-eye.eu/public/" + find)
        else:
            fixedfinds.append(find)
    return fixedfinds, total
 