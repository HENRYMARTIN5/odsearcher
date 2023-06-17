import os
import fuzzysearch
import psutil
import time
from datetime import timedelta

def register_args(parser):
    parser.add_argument('--no-rarbg', action='store_true', help='Do not search the RARBG archives.')

def ensure_db_downloaded():
    if (not os.path.exists('rarbg_movies.txt') or not os.path.exists("rarbg_shows.txt")):
        return False
    return True

def do_search(name, args):
    if args.no_rarbg:
        return [], 0
    if not ensure_db_downloaded():
        print("Database not found. See README.md for instructions on how to download it.")
        return [], 0
    found = []
    total = 0
    with open("rarbg_movies.txt", "r") as f:
        print("Searching movies...")
        text = f.read()
        i = 0
        for line in text.splitlines():
            if fuzzysearch.find_near_matches(name, line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "."), line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "_"), line.lower(), max_l_dist=1):
                found.append(line)
                total += 1
            i += 1
    with open("rarbg_shows.txt", "r") as f:
        print("Searching shows...")
        text = f.read()
        i = 0
        for line in text.splitlines():
            if fuzzysearch.find_near_matches(name, line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "."), line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "_"), line.lower(), max_l_dist=1):
                found.append(line)
                total += 1
            i += 1
    return found, total
    