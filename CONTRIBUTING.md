# Contributing

## Code Style

odsearcher has a strict code style. It is based on PEP 8, but with a few extra rules:

- Indentation is always tabs. No spaces. No exceptions. Ever.
- There should be a blank line between every function, and two blank lines between every class.
- There should be a blank line between every import (not `__import__`) and the code that follows it.
- Use. Markdownlint. If your markdown isn't compliant with the rules (except no-duplicate-header), I will not accept your PR until you fix it. (Quite frankly, it's not that hard to follow the rules.)

## Pull Requests

When making a pull request, please make sure to follow these guidelines:

- Make sure your code follows the code style guidelines (above).
- Make sure your changes are documented in the pull request description.
- Make sure your pull request is up to date with the latest version of the master branch.
- When dealing with merge conflicts, make sure to resolve them in favor of the master branch, unless they are critical to your changes.

## Issues

If you find a bug or a missing key feature, please report it on the issues page on GitHub. Please make sure to follow these guidelines:

- Make sure your issue is not a duplicate of another issue.
- Ensure that your issue is related to odsearcher, and not the indexer.
- Always include a command or example index that reproduces the issue, if applicable.

## Adding Support for a Directory

In the `/utils` folder, you'll find a list of supporting modules/scripts for the script as a whole. In order to add your own support for a directory that uses a different format for indexes (and is too large to index otherwise), as was the case with the-eye.ru, create a new file there and implement the following:

- `register_args(parser)` - Takes the argument parser from the main script and adds its own command-line arguments to it. If this isn't required, you can skip it.
- `do_search(target_string, args)` - Takes the target search string and the passed command-line arguments and searches the directory for the file. You can use any form of fuzzy search here (for example, if the site already provides an integrated search feature), but `fuzzysearch` is perferred. This code should do the trick for checking a given record, `record`, and the target string, `target_string`:

```py
if fuzzysearch.find_near_matches(target_string, record.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(target_string.replace(" ", "."), record.lower(), max_l_dist=1) or fuzzysearch.find_near_matches(target_string.replace(" ", "_"), record.lower(), max_l_dist=1):
   # matched, do something
```

After finding all records on the directory, `do_search` should return an tuple of a list of strings and an int: the matches, and the number of matches found.

After creating your module, you'll need to add it to the main `searcher.py` file. Just look for a line towards the top of the file defining a list called `utils`. Just add the name of your python script to the end of that list, and it should be automatically imported. Now, look in the main `search()` function. You'll need to add your module's search to the chain of search. As of commit [f1fc3fc](https://github.com/HENRYMARTIN5/odsearcher/commit/f1fc3fcec05791288fcc5db68c521879c47d2720), that chain looks like this:

```py
    total = 0
    matches = []
    if not args.eye_only:
        for file in os.listdir():
            if file.endswith(".txt"):
                print("\nSearching in " + file + " ...")
                with open(file, "r", errors='replace') as f:
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
                
    # extra utils here
    _matches, _total = the_eye.do_search(name, args)
    matches += _matches
    total += _total
```

At the very bottom, you'll want to duplicate the call to `the_eye.do_search()` and replace `the_eye` with the name of your directory. Hopefully, everything will work first-try, and you'll have your new directory up and running in no time!
