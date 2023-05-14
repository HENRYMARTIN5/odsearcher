#!/bin/python3

try:
    import argparse
    import fuzzysearch
    import os
    import langid
    import re
    from utils import the_eye
    import googlesearch
except ImportError:
    # install dependencies
    import subprocess
    import sys
    import re
    subprocess.check_call([sys.executable, "-m", "pip", "install", "argparse"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fuzzysearch"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rapidfuzz"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langid"])
    import argparse
    import fuzzysearch
    import os
    import langid
    import googlesearch

utils = ["the_eye"]

# import all utils
for util in utils:
    exec("from utils import " + util)

parser = argparse.ArgumentParser(description='Search for a specific file in the current indexed opendirectories')
parser.add_argument('name', help='Name of the file or substring to search for. Fuzzy search is performed automatically.')
parser.add_argument('-d', '--download', action='store_true', help='Download the file(s) found automagically')
parser.add_argument('-s', '--shell-export', action='store_true', help='Export to a .sh script to download later')
parser.add_argument('-e', '--export', action='store_true', help='Export the results to a list of URLs')
parser.add_argument('-v', '--video', action='store_true', help='Optimize for video search')
parser.add_argument('-a', '--audio', action='store_true', help='Optimize for audio search')
parser.add_argument('-w', '--warez', action='store_true', help='Optimize for warez search')
parser.add_argument('-b', '--books', action='store_true', help='Optimize for ebook search')
parser.add_argument('-t', '--tv', action='store_true', help='Optimize for TV show search')
parser.add_argument('-m', '--multiplevideo', action='store_true', help='Optimize for multiple-video search (eg. movie series)')
parser.add_argument('-l', '--language', help='Filter to the specified language (eg. en, fr, de, es, etc.)')
parser.add_argument('-g', '--no-googledork', action='store_true', help='Google dork to find more directories containing the file.')
parser.add_argument('--season', help='Season number for TV show search')
parser.add_argument('--episode', help='Episode number for TV show search')
parser.add_argument('--filter-camera', action='store_true', help='Filter out camera rips')
parser.add_argument('--disable-sanity-filter', action='store_true', help='Disable the sanity filter (eg. no trailers, no sample files, no node_modules on seedboxes, etc.)')
parser.add_argument('--force-format', help='Force the format of the file (eg. mkv, mp4, avi, etc.)')
for util in utils:
    exec(util + ".register_args(parser)")
parser.add_argument('--add', help='Add a new directory to the index')
parser.add_argument('-r', '--remove', help='Remove a directory from the index')
parser.add_argument('-u', '--update', action='store_true', help='Update all directories in the index')
args = parser.parse_args()

def check_filetype(name):
    # check language
    if args.language:
        lang, confidence = langid.classify(name)
        if lang != args.language:
            return False
    if "node_modules" in name.lower() and not args.disable_sanity_filter:
        return False
    if args.filter_camera:
        if "camrip" in name.lower() or "cam-rip" in name.lower() or "cam rip" in name.lower() or "cam" in name.lower() or "hdcam" in name.lower() or "hd-cam" in name.lower():
            return False
    if args.video or args.multiplevideo or args.tv:
        if name.endswith(".mkv") or name.endswith(".mp4") or name.endswith(".avi") or name.endswith(".flv") or name.endswith(".mov") or name.endswith(".wmv") or name.endswith(".webm"):
            if not "trailer" in name.lower() and not args.disable_sanity_filter:
                return True
            else:
                return False
        else:
            return False
    elif args.audio:
        if name.endswith(".mp3") or name.endswith(".flac") or name.endswith(".wav") or name.endswith(".ogg") or name.endswith(".m4a") or name.endswith(".aac"):
            return True
        else:
            return False
    elif args.warez:
        if name.endswith(".rar") or name.endswith(".zip") or name.endswith(".7z") or name.endswith(".tar") or name.endswith(".gz") or name.endswith(".bz2") or name.endswith(".xz") or name.endswith(".iso") or name.endswith(".img") or name.endswith(".dmg") or name.endswith(".exe") or name.endswith(".msi") or name.endswith(".apk") or name.endswith(".ipa") or name.endswith(".deb") or name.endswith(".rpm") or name.endswith(".jar") or name.endswith(".war") or name.endswith(".ear") or name.endswith(".cab") or name.endswith(".pak") or name.endswith(".pak"):
            return True
        else:
            return False
    elif args.books:
        if name.endswith(".pdf") or name.endswith(".epub") or name.endswith(".mobi") or name.endswith(".azw") or name.endswith(".azw3") or name.endswith(".azw4") or name.endswith(".azw8") or name.endswith(".prc") or name.endswith(".pdb") or name.endswith(".txt") or name.endswith(".html") or name.endswith(".doc") or name.endswith(".docx") or name.endswith(".rtf") or name.endswith(".odt") or name.endswith(".djvu") or name.endswith(".fb2") or name.endswith(".ibooks") or name.endswith(".cbz") or name.endswith(".cbr") or name.endswith(".cb7") or name.endswith(".cbt") or name.endswith(".cba") or name.endswith(".chm") or name.endswith(".mht") or name.endswith(".mhtml") or name.endswith(".xps") or name.endswith(".zip") or name.endswith(".rar") or name.endswith(".tar") or name.endswith(".gz") or name.endswith(".bz2") or name.endswith(".xz") or name.endswith(".7z") or name.endswith(".cbt") or name.endswith(".cba") or name.endswith(".djvu"):
            return True
        else:
            return False
    else:
        return True

def bash_escape(text):
    return text.replace(" ", "%20")

def extract_season_and_episode(string):
    pattern = r's(\d+)e(\d+)'
    match = re.search(pattern, string, re.IGNORECASE)
    if match:
        season = int(match.group(1))
        episode = int(match.group(2))
        return season, episode
    else:
        # this time with a slash in between the season and episode - folder-based naming
        pattern = r's(\d+)/e(\d+)'
        match = re.search(pattern, string, re.IGNORECASE)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            return season, episode
        return "", ""

def search(name):
    name = name.lower()
    # current directory contains a bunch of text files with the urls to files in the open directories
    # we will search for the file name in each of these files
    total = 0
    matches = []
    if not args.eye_only:
        for file in os.listdir("OpenDirectoryDownloader/Scans"):
            if file.endswith(".txt"):
                print("\nSearching in " + file + " ...")
                with open(os.path.join("OpenDirectoryDownloader/Scans", file), "r", errors='replace') as f:
                    text = f.read()
                    i = 0
                    for line in text.splitlines():
                        if fuzzysearch.find_near_matches(name, line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "."), line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "_"), line.lower(), max_l_dist=1):
                            if check_filetype(line):
                                print(line)
                                total += 1
                                matches.append(line)
                        i += 1
                print("Done searching in " + file + ".\n")
    _matches, _total = the_eye.do_search(name, args)
    matches += _matches
    total += _total
    print("Total matches: " + str(total))

    if not args.no_googledork and total == 0:
        print("No matches, googledorking for " + name + " ...")
        if args.video or args.multiplevideo:
            filequery = "mkv|mp4|avi|mov|mpg|wmv|divx|mpeg"
        elif args.audio:
            filequery = "mp3|wav|ac3|ogg|flac|wma|m4a|aac|mod"
        elif args.warez:
            filequery = "exe|iso|dmg|tar|7z|bz2|gz|rar|zip|apk"
        elif args.books:
            filequery = "rzb|tpz|apnx|lrs|mart|tk3|mobi|azw3|kfx|ncx|ibooks|lrf|pdf"
        else:
            filequery = False
        if filequery:
            query = name.lower() + " (" + filequery + ") -inurl:(jsp|pl|php|html|aspx|htm|cf|shtml) intitle:index.of -inurl:(listen77|mp3raid|mp3toss|mp3drug|index_of|index-of|wallywashis|downloadmana)"
        else:
            query = name.lower() + " -inurl:(jsp|pl|php|html|aspx|htm|cf|shtml) intitle:index.of -inurl:(listen77|mp3raid|mp3toss|mp3drug|index_of|index-of|wallywashis|downloadmana)"
        print("\nGoogle dorking for " + query + " ...")
        urlsIndexed = []
        results = googlesearch.search(query)
        for url in results:
            # is url indexed?
            if os.path.exists(os.path.join("OpenDirectoryDownloader/Scans", url.replace("/", "_") + ".txt")):
                print("Already indexed " + url + ". Skipping.")
                continue
            isGoodResult = False

            print("Indexing " + url + " ...")
            os.chdir("OpenDirectoryDownloader")
            if os.name == "nt":
                os.chdir("OpenDirectoryDownloader")
                os.system("opendirectorydownloader.exe -q -u " + url)
                os.chdir("..")
            else:
                os.chdir("OpenDirectoryDownloader")
                os.system("chmod +x OpenDirectoryDownloader")
                os.system("./OpenDirectoryDownloader -q -u " + url)
                os.chdir("..")
            print("Done indexing " + url + ".\n")
            urlsIndexed.append(url)
        print("Done googledorking for " + query + ". Searching again in new databases...\n")
        for newlyIndexed in urlsIndexed:
            with open(os.path.join("OpenDirectoryDownloader/Scans", newlyIndexed.replace("/", "_") + ".txt"), "r", errors='replace') as f:
                text = f.read()
                i = 0
                for line in text.splitlines():
                    if fuzzysearch.find_near_matches(name, line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "."), line.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(name.replace(" ", "_"), line.lower(), max_l_dist=1):
                        if check_filetype(line):
                            print(line)
                            total += 1
                            matches.append(line)
                    i += 1
           
    if total > 0:
        # find highest quality match for video
        tvToDl = []
        episodesGrabbed = []
        if args.video:
            for match in matches:
                if "2160p" in match:
                    toDl = match
                elif "1080p" in match:
                    toDl = match
                elif "720p" in match:
                    toDl = match
                elif "480p" in match:
                    toDl = match
                elif "360p" in match:
                    toDl = match
                elif "240p" in match:
                    toDl = match
                elif "144p" in match:
                    toDl = match
                else:
                    print("Couldn't sift by quality. Downloading all matches and letting you decide.")
                    toDl = False
        elif args.tv:
            # find highest quality for each episode
            for match in matches:
                # find season and episode number
                season, episode = extract_season_and_episode(match)
                if season != "" and episode != "":
                    if not str(season) + " " + str(episode) in episodesGrabbed:
                        episodesGrabbed.append(str(season) + " " +  str(episode))
                        if "2160p" in match:
                            tvToDl.append(match)
                        elif "1080p" in match:
                            tvToDl.append(match)
                        elif "720p" in match:
                            tvToDl.append(match)
                        elif "480p" in match:
                            tvToDl.append(match)
                        elif "360p" in match:
                            tvToDl.append(match)
                        elif "240p" in match:
                            tvToDl.append(match)
                        elif "144p" in match:
                            tvToDl.append(match)
                        else:
                            print("Couldn't sift by quality. Downloading indiscriminately and letting you decide.")
                            tvToDl.append(match)
                    else:
                        print("Already grabbed episode " + str(season) + " " + str(episode) + ". Skipping.")
                else:
                    print("Couldn't find season and episode number in " + match + ". Skipping.")
            
            grabbed2 = []
            for dl in tvToDl:
                season, episode = extract_season_and_episode(dl)
                if str(season) + " " + str(episode) not in grabbed2:
                    grabbed2.append(str(season) + " " + str(episode))
                    print(dl)
            tvToDl = grabbed2
        
            # filter down by season and episode (if specified)
            correctDls = []
            for dl in tvToDl:
                season, episode = extract_season_and_episode(dl)
                if season == args.season and episode == args.episode and args.season and args.episode:
                    correctDls.append(dl)
                elif season == args.season and args.season and not args.episode:
                    correctDls.append(dl)
                elif episode == args.episode and args.episode and not args.season:
                    correctDls.append(dl)
                elif not args.season and not args.episode:
                    correctDls.append(dl)
            tvToDl = correctDls
                
        
        try:
            toDl
        except NameError:
            toDl = False
        except UnboundLocalError:
            toDl = False

        if not args.shell_export:
            if args.export:
                if not os.path.exists("downloads"):
                    os.mkdir("downloads")
                os.chdir("downloads")
                with open("download_links.txt", "w") as f:
                    for match in matches:
                        f.write(match + "\n")
                print("Links exported to downloads/download_links.txt")
                return
            if not args.download:
                yn = input("Download all now? [Y/n] ")
            else:
                yn = "Y"
            if yn == "Y" or yn == "y":
                if not toDl:
                    if not args.tv:
                        if not os.path.exists("downloads"):
                            os.mkdir("downloads")
                            os.chdir("downloads")
                        for match in matches:
                            os.system("wget " + bash_escape(match))
                    else:
                        if len(tvToDl) == 0:
                            print("No episodes found.")
                        else:
                            if not os.path.exists("downloads"):
                                os.mkdir("downloads")
                            os.chdir("downloads")
                            for dl in tvToDl:
                                os.system("wget " + bash_escape(dl))
                else:
                    if not os.path.exists("downloads"):
                        os.mkdir("downloads")
                    os.chdir("downloads")
                    os.system("wget " + bash_escape(toDl))
        else:
            if not os.path.exists("downloads"):
                os.mkdir("downloads")
            os.chdir("downloads")
            with open("download.sh", "w") as f:
                if not toDl:
                    for match in matches:
                        f.write("wget " + bash_escape(match.encode('ascii', 'replace').decode()) + "\n")
                else:
                    if not args.tv:
                        f.write("wget " + bash_escape(toDl.encode('ascii', 'replace').decode()) + "\n")
                    else:
                        if len(tvToDl) == 0:
                            print("No episodes found.")
                        else:
                            for dl in tvToDl:
                                f.write("wget " + bash_escape(dl.encode('ascii', 'replace').decode()) + "\n")
            print("Exported to download.sh")

def adddir(dir):
    # call opendirectorydownloader.exe on windows, opendirectorydownloader on linux - file is located in parent dir
    if os.name == "nt":
        os.chdir("OpenDirectoryDownloader")
        os.system("opendirectorydownloader.exe -q -u " + dir)
        os.chdir("..")
    else:
        os.chdir("OpenDirectoryDownloader")
        os.system("chmod +x OpenDirectoryDownloader")
        os.system("OpenDirectoryDownloader -q -u " + dir)
        os.chdir("..")

def removedir(dir):
    filename = dir.replace("/", "_")
    if os.path.exists(os.path.join("OpenDirectoryDownloader/Scans", filename)):
        os.remove(filename)
        print("Removed.")
    else:
        print("Directory not found.")

def update():
    # update all directories
    for dir in os.listdir():
        if dir.endswith(".txt"):
            print("Updating " + dir + "...")
            adddir(dir)

if __name__ == "__main__":
    if not args.add or args.remove or args.update:
        if not args.name:
            print("You must specify a name to search for.")
            sys.exit(1)
        search(args.name)
    else:
        if args.add:
            adddir(args.add)
        elif args.remove:
            removedir(args.remove)
        elif args.update:
            update()
        else:
            print("How the hell did you get here?")
            sys.exit(1)