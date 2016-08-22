#!/usr/bin/env python2
from __future__ import print_function
from subprocess import call
import eyed3
import sys
import os

usage = '''
Usage:

yt2mp3 [OPTIONS] URLFILE

URLFILE: Source file that is parsed in order to get the url's and Tags of the mp3's to be created.
         An example-entry would be:
         
         http://www.youtube.com/watch?v=aaaaaaaaa -t "title" -a "artist" -A "album"

         The tags (-t ..., -a ..., etc) are directly given to eyed3, the url to youtube-dl

OPTIONS: Additional options:

        quality : -q,-Q,--quality,--Quality,-b,-B,--bitrate,--Bitrate
                  (e.g. -q 256 for a Quality of 256 kB/s)
        tags    : -t,-T,--tags,--Tags 
                  (Shall tags in URLFILE be used? Off by default)
        rename  : -r,-R,--rename,--Rename
                  (If given, the filenames of the mp3's that are created are renamed according to the -t Tag)
        cont    : -c,-C,--continue,--Continue
                  (If given, a previous try that got interrupted is resumed)
'''

def parse_command(arg_list):
    options = {'quality' : ['-q', '-Q' , '--quality', '--Quality', '-b', '-B' '--bitrate' '--Bitrate'], 
               'tags'    : ['-t', '-T', '--tags', '--Tags'], 
               'rename'  : ['-r', '-R', '--rename', '--Rename'],
               'cont'    : ['-c', '-C', '--continue', '--Continue'],
               'num'     : ['-n', '-N', '--number', '--Number']                                        }
    bitrate = 196
    tags    = True
    urlfile = False
    rename  = False
    cont    = False
    num     = 0 

    while arg_list:
        if arg_list[0] in options['quality']:
            del arg_list[0]
            try:
                bitrate = int(arg_list[0].replace('K', ''))
            except ValueError:
                print("Couldn't read quality argument -- 196 kB/s are used by default")
                print(usage)
            finally :
                del arg_list[0]

        elif arg_list[0] in options['cont']:
            del arg_list[0]
            cont = True

        elif arg_list[0] in options['num']:
            del arg_list[0]
            try: 
                num  = int(arg_list[0])
            except ValueError:
                print("Couldn't read number argument -- n = 0 by default")
                print(usage)
            finally:
                del arg_list[0]

        elif arg_list[0] in options['tags']:
            del arg_list[0]
            tags = True

        elif arg_list[0] in options['rename']:
            del arg_list[0]
            rename = True
        
        else :
            if urlfile is not False:
                print("Error: Couldn't parse command.")
                print(usage)
                sys.exit()
            else :
                urlfile = arg_list[0]
                del arg_list[0]
    
    if urlfile == False:
        print('Error: No URL-file given')
        print(usage)
        sys.exit()
    print('\n-------------------------------')
    print('Filename: %s     ' % urlfile)
    print('Bitrate: %d kB/s ' % bitrate)
    if tags:   print('Tags enabled     ')
    if rename: print("Will try to rename mp3's")
    if cont:   print("Will continue previous try")
    if num:    print("Process blocks of size %d" % num)
    print('-------------------------------\n')
    return (bitrate, tags, urlfile, rename, cont, num)

def create_mp3(cmd_tuple):
    url_list = []
    tag_list = []
    try :
        url_file = open(cmd_tuple[2])
    except IOError :
        print("Error: Couldn't open URL-File %s" % cmd_tuple[2])
        sys.exit()
    for line in url_file :
        if line[0] not in ["\n", "#"]:
            parts = line.split()
            url_list.append(parts[0])
            tag_list.append(' '.join([str(x) for x in parts[1:]]))

    if cmd_tuple[1]: # This means: if tags=True
        name_list = [x[x.find('=')+1:] + '.mp3' for x in url_list] # create list of names
        print("Create mp3's: youtube-dl %s --id --extract-audio --audio-format mp3 --audio-quality %dK %s" % \
              ("-c" if cmd_tuple[4] else "", cmd_tuple[0], ' '.join([str(x) for x in url_list])))
        print("-----------------------------------------------------------")
        call("youtube-dl %s --extract-audio --id --audio-format mp3 --audio-quality %dK %s" % \
             ("-c" if cmd_tuple[4] else "", cmd_tuple[0], ' '.join([str(x) for x in url_list])), shell=True)
        print("-----------------------------------------------------------\n")
        for n in range(len(url_list)):
            if tag_list[n]:
                print("Create Tags: eyeD3 %s %s" % (tag_list[n], name_list[n]))
                call(r"eyeD3 --remove-all %s > /dev/null 2>&1" % name_list[n], shell=True);
                call(r"eyeD3 %s %s > /dev/null" % (tag_list[n], name_list[n]), shell=True)
        if cmd_tuple[3]: # if rename=True
            for n in range(len(url_list)):
                tags = eyed3.load(name_list[n])
                if tags.tag.title not in ["",u""]:
                    try :
                        call('mv "./%s" "./%s"' % \
                             (name_list[n], tags.tag.title.replace(' ', '_') + ".mp3"), shell=True)
                        print("Renamed: %s  --->  %s" % (name_list[n], tags.tag.title.replace(' ', '_') + ".mp3\n"))
                    except AttributeError :
                        print("Couldn't rename %s\n" % name_list[n])


    else :
        print("Create mp3's: youtube-dl -t --extract-audio --audio-format mp3 --audio-quality %dK %s" % (cmd_tuple[0], ' '.join([str(x) for x in url_list])))
        print("-----------------------------------------------------------")
        call("youtube-dl -t --extract-audio --audio-format mp3 --audio-quality %dK %s" % (cmd_tuple[0], ' '.join([str(x) for x in url_list])), shell=True)
        print("-----------------------------------------------------------\n")


if __name__ == '__main__':
    create_mp3(parse_command(sys.argv[1:]))

