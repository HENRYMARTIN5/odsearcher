# odsearcher

Searches locally indexed open directories for files using broad search categories and refinements

## Installation

1. Install Python 3.6 or higher
2. Clone the repo: `git clone https://github.com/HENRYMARTIN5/odsearcher.git`
3. Run the script: `python3 odsearcher.py`. All dependencies will be installed automatically. It will print out a help message if you don't provide any arguments.
4. Next, you'll need to download KoalaBear84's [OpenDirectoryDownloader](https://github.com/KoalaBear84/OpenDirectoryDownloader/releases) and unzip it to a directory inside the odsearcher directory called `OpenDirectoryDownloader`. Download the correct, **self-contained** release for your platform. Non-self-contained releases might work, but are not supported.
5. If you want to search [the-eye.eu](https://the-eye.eu/), you'll also have to download their databases, since crawling it manually would take hours on end (38, to be exact). Get them from [here](https://drive.google.com/drive/folders/1kf4lTu3-ZMlUveiCQL_B7qYZm0WAHKKB) and unzip them into the same directory as `odsearcher.py`.
6. And if you want to search the RARBG archives, you'll need to download the individual files from [here](https://github.com/2004content/rarbg/raw/main/sorted/-rarbg.264.1080p.movies.txt) and [here](https://raw.githubusercontent.com/2004content/rarbg/main/sorted/-rarbg.264.1080p.shows.txt) and place them in the same directory as `odsearcher.py`, named `rarbg_movies.txt` and `rarbg_shows.txt`, respectively.

## Usage

If you installed the script as reccomended in the above instructions, then you'll already have downloaded the databases for the-eye. If you didn't, that's completely okay - your searches just won't turn anything up until you add some open directories to your local index. If you want a small sample of open directories to get started with, see `samples.md`. To find more open directories, check out the search tools at [odfinder.github.io](https://odfinder.github.io/) and [open-directories.reecemercer.dev](https://open-directories.reecemercer.dev/) - I've found them to work the best out of all I've tried. For interesting results, try pasting the resulting search query into other engines, such as Startpage or DuckDuckGo.

```txt
usage: odsearcher.py [-h] [-d] [-s] [-e] [-v] [-a] [-w] [-b] [-t] [-m] [-l LANGUAGE] [-g] [--season SEASON] [--episode EPISODE] [--filter-camera] [--disable-sanity-filter] [--force-format FORCE_FORMAT] [--require-https] [--eye-only] [-n] [--eye-no-nonpiracy] [--eye-no-piracy] [--add ADD] [--force-singlethreaded] [--scan-filepursuit] [--scan-odcrawler] [-r REMOVE] [-u] [-c] name

Search for a specific file in the current indexed opendirectories

positional arguments:
  name                  Name of the file or substring to search for. Fuzzy search is performed automatically.

options:
  -h, --help            show this help message and exit
  -d, --download        Download the file(s) found automagically
  -s, --shell-export    Export to a .sh script to download later
  -e, --export          Export the results to a list of URLs
  -v, --video           Optimize for video search
  -a, --audio           Optimize for audio search
  -w, --warez           Optimize for warez search
  -b, --books           Optimize for ebook search
  -t, --tv              Optimize for TV show search
  -m, --multiplevideo   Optimize for multiple-video search (eg. movie series)
  -l LANGUAGE, --language LANGUAGE
                        Filter to the specified language (eg. en, fr, de, es, etc.)
  -g, --googledork      Google dork to find more directories containing the file.
  --season SEASON       Season number for TV show search
  --episode EPISODE     Episode number for TV show search
  --filter-camera       Filter out camera rips (why were these even invented?)
  --disable-sanity-filter
                        Disable the sanity filter (eg. no trailers, no sample files, no node_modules on seedboxes, etc.)
  --force-format FORCE_FORMAT
                        Force the format of the file (eg. mkv, mp4, avi, etc.)
  --require-https       Filter out results that do not use HTTPS (stay safe out there!)
  --eye-only            Only search the-eye.eu. Useful if you're looking for something specific and don't want to wait for the other sites to search.
  -n, --no-eye          Do not search the-eye.eu. Generally useful if you're constrained by disk space, since the index alone is 3gb.
  --eye-no-nonpiracy    Do not perform a search of the-eye's non-piracy database
  --eye-no-piracy       Do not perform a search of the-eye's piracy database - reccomended for systems on low RAM, the database is 4gb in RAM.
  --no-rarbg            Do not search the RARBG archives.
  --add ADD             Add a new directory to the index
  --force-singlethreaded
                        Force single-threaded mode for OpenDirectoryDownloader, useful for ratelimited ODs
  --scan-filepursuit    Scan filepursuit for new directories to index that might contain the target file
  --scan-odcrawler      Similar to filepursuit, but uses odcrawler.xyz instead
  -r REMOVE, --remove REMOVE
                        Remove a directory from the index
  -u, --update          Update all directories in the index
  -c, --clean           Clean the index of dead directories
```

## Examples

Search for and automatically download a piece of software:

```sh
python3 odsearcher.py -wd "doom 1993"
```

Search for and export a list of possible links to a specific song:

```sh
python3 odsearcher.py -ae "tally hall ruler of everything"
```

Search for and export a .sh script to download all episodes of a specific TV show:

```sh
python3 odsearcher.py -st "the simpsons"
```

Filter results to a specific language:

```sh
python3 odsearcher.py -l en "search query here"
```

Add a new open directory to the index:

```sh
python3 odsearcher.py --add https://somerandomweb.site/path/to/open/directory " " # note the empty quotes - to tell the script that you're not searching for anything
```

Omit the-eye from the search:

```sh
python3 odsearcher.py -n "search query here"
```

Use only the-eye for the search:

```sh
python3 odsearcher.py --eye-only "search query here"
```

Use HTTPS only:

```sh
python3 odsearcher.py --require-https "search query here"
```

Find a specific book, requiring HTTPS, excluding the-eye's piracy database, and export everything to a bash script to download the files:

```sh
python3 odsearcher.py --require-https --eye-no-piracy -sb "book title here" 
```

> Pro tip: use lowercase characters for your search query - strings are compared case-insensitively, so you'll get more results that way.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.
