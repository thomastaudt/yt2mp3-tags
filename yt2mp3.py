#!/usr/bin/env python2
from __future__ import print_function
from subprocess import call
import argparse
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

def parse_args():
    parser = argparse.ArgumentParser(description='Convert YouTube Videos to MP3.')
    parser.add_argument('urlfile', metavar='urlfile', type=str, help='File containing the urls of the target videos')
    parser.add_argument('-q', '--quality', help='Quality (bitrate) of MP3. E.g. -q 256 for 256 kB/s', default=192, type=int)
    parser.add_argument('-n', '--notags', action='store_true', help='Don\'t use tags given in urlfile')
    parser.add_argument('-r', '--rename', action='store_true', help='Rename filenames of MP3\'s according to -t tag')
    parser.add_argument('-c', '--continue', dest='cont', action='store_true', help='Retry previous try')

    args = parser.parse_args()

    print('\n-------------------------------')
    print('Filename: %s     ' % args.urlfile)
    print('Bitrate: %d kB/s ' % args.quality)
    if not args.notags: print('Tags enabled')
    if args.rename: print("Will try to rename mp3's")
    if args.cont: print("Will continue previous try")

    print('-------------------------------\n')

    return args
                         

def create_mp3(args):
    url_list = []
    tag_list = []
    try :
        url_file = open(args.urlfile)
    except IOError :
        print("Error: Couldn't open URL-File %s" % args.urlfile)
        sys.exit()
    for line in url_file :
        if line[0] not in ["\n", "#"]:
            parts = line.split()
            url_list.append(parts[0])
            tag_list.append(' '.join([str(x) for x in parts[1:]]))

    if not args.notags: # This means: if tags=True
        name_list = [x[x.find('=')+1:] + '.mp3' for x in url_list] # create list of names
        print("Create mp3's: youtube-dl %s --id --extract-audio --audio-format mp3 --audio-quality %dK %s" % \
              ("-c" if args.cont else "", args.quality, ' '.join([str(x) for x in url_list])))
        print("-----------------------------------------------------------")
        call("youtube-dl %s --extract-audio --id --audio-format mp3 --audio-quality %dK %s" % \
             ("-c" if args.cont else "", args.quality, ' '.join([str(x) for x in url_list])), shell=True)
        print("-----------------------------------------------------------\n")
        for n in range(len(url_list)):
            if tag_list[n]:
                print("Create Tags: eyeD3 %s ./%s" % (tag_list[n], name_list[n]))
                call(r"eyeD3 --remove-all ./%s > /dev/null 2>&1" % name_list[n], shell=True);
                call(r"eyeD3 %s ./%s > /dev/null" % (tag_list[n], name_list[n]), shell=True)
        if args.rename: # if rename=True
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
        print("Create mp3's: youtube-dl -t --extract-audio --audio-format mp3 --audio-quality %dK %s" % (args.quality, ' '.join([str(x) for x in url_list])))
        print("-----------------------------------------------------------")
        call("youtube-dl -t --extract-audio --audio-format mp3 --audio-quality %dK %s" % (args.quality, ' '.join([str(x) for x in url_list])), shell=True)
        print("-----------------------------------------------------------\n")


if __name__ == '__main__':
    create_mp3(parse_args())

