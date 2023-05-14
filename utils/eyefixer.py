# taken from https://github.com/The-Eye-Team/EyeDex - licensed under the GNU GPL v3 - copyright 2020 - thanks :)

#format db file for search
import os, sys
from tempfile import mkstemp
from shutil import move, copymode
from urllib.parse import unquote
BASEURL = "http://the-eye.eu/public/"
DELIMITER = "&"

def percentage(part, whole):
    return (100 * float(part)/float(whole))*2

def formatdb(db_file, output_file):
    #TODO: remove broken urls and data from file.. requires some work..
    #TODO: make json valid, noticing extra commas at end of file
    from rapidfuzz import utils
    fh, abs_path = mkstemp()
    counter = 1
    # figure out total length of old file
    print("Calculating file length...")
    with open(db_file, errors="replace") as old_file:
        num_lines = sum(1 for line in old_file)
    print("Loading and parsing file...")
    with os.fdopen(fh,'wb') as new_file:
        i = 0
        previous_percentage = 0
        with open(db_file, errors="replace") as old_file:
            print("Fixing file...")
            print("0% done\r", end="")
            # use readline() to read the first line 
            line = old_file.readline()
            while line:
                if percentage(i, num_lines) - previous_percentage > 0.01:
                    previous_percentage = percentage(i, num_lines)
                    print(str(round(previous_percentage, 2)) + "% done           \r", end="")
                #skip status
                if line.startswith('"success":'):
                    line = old_file.readline()
                    continue
                if line[-3:-1] == ' {':
                    #name
                    string = line[1:-5]
                    #MAKE SURE DELIMITER IS STRIPPED (from searchModified.cpp):
                    newstring = utils.default_process(string)
                    oldline = line
                    line = old_file.readline()
                    if len(newstring) == 0: #replace with anything after /
                        newstring = line.rstrip()[8:-3]
                        newstring = unquote(newstring[newstring.rfind('/')+1:])
                        if utils.default_process(newstring).strip() == "":
                            newstring = "NONE" + str(counter)
                            counter += 1
                    new_file.write(oldline.replace(string, newstring).encode())
                    if BASEURL in line:
                        if line.startswith('\t'):
                            # url - 1
                            url = line[9:-3]
                            starting = line[:9]
                            #skip file type, already in link
                            old_file.readline()
                        else:
                            url = line[8:-3]
                            starting = line[:8]
                            #skip status
                        # new_url = unquote(url).replace(BASEURL, '') #removed because unsafe chars might interfere with delimiter(see searchModified.cpp)
                        new_url = url.replace(BASEURL, '')
                        new_string = starting.encode() + new_url.encode() + line[-3:].encode()
                        new_file.write(new_string)
                        line = old_file.readline()
                        continue
                i += 1
                new_file.write(line.encode())
                line = old_file.readline()
    #Copy the file permissions from the old file to the new file
    copymode(db_file, abs_path)
    #Move new file
    move(abs_path, output_file)
    print("100% done\r", end="")
if __name__ == "__main__":
    
    if len(sys.argv) > 2:
        output = os.path.join(os.path.dirname(os.path.realpath(__file__)), sys.argv[2])
        formatdb(sys.argv[1], output)
    else:
        print("python3 formatter.py inputFile outputFile")