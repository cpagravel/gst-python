#! /usr/bin/env python3
import argparse                                 # parse arguments
import os, subprocess                           # run bash commands
from colors import *

def bash(command):
    if ('list' in str(type(command))):
        commandArray = command
    else:
        commandArray = command.split()
    proc = subprocess.Popen(commandArray, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    (output, err) = proc.communicate()
    return output

def GenerateList():
    output = bash('git status -s').decode('utf-8')
    lines = output.split('\n')
    # Iterate through git status text
    statusList = []
    for line in lines:
        if (line != ''):
            statusList.append({'mod': line[0:2], 'filePath': line[3:]})
    return statusList

def checkValidRef(num):
    num = int(num)
    if num < 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % num)
    else:
        return num

def parseRange(string0):
    output = []
    parts = string0.split(',') # individual
    for part in parts:
        bounds = part.split('-') # range selection
        if (len(bounds) == 2):
            output += range(int(bounds[0]), int(bounds[1]) + 1)
        else:
            output.append(int(part))
    return output

def checkValidRange(string0):
    values = parseRange(string0)
    for value in values:
        if (value < 0):
            argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    else:
        return string0

parser = argparse.ArgumentParser()

parser.add_argument('-v', action='store_true', help='show full paths of files')

group1 = parser.add_mutually_exclusive_group()
group1.add_argument('REF', metavar='REF', type=checkValidRef, nargs='?',
                    help='an integer for the accumulator')
group1.add_argument('-a', type=checkValidRange, metavar='REF', dest='add', help=('eq to ' + Colors.colorize('git add ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-c', type=checkValidRange, metavar='REF', dest='checkout', help=('eq to ' + Colors.colorize('git checkout HEAD ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-d', type=checkValidRef, metavar='REF', dest='diff', help=('eq to ' + Colors.colorize('git diff HEAD ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-D', type=checkValidRange, metavar='REF', dest='delete', help=('eq to ' + Colors.colorize('rm ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-e', type=checkValidRef, metavar='REF', dest='edit', help=('eq to ' + Colors.colorize('vim ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-r', type=checkValidRange, metavar='REF', dest='reset', help=('eq to ' + Colors.colorize('git reset HEAD ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
args = parser.parse_args()

gitFlagDecode = {
          'M': "Modified",
          'A': "Added   ",
          'D': "Deleted ",
          'R': "Renamed ",
          'C': "Copied  ",
          'U': "Unmerged",
          'T': "TypeChg ",
          '?': "Untrackd",
          '!': "Ignored ",
          'm': "Sub Mod ",
          ' ': "        "
        }

def displayList():
    statusList = GenerateList()
    header = Colors.colorize('#   INDEX     CUR_TREE  FILE', Colors.YELLOW)
    print(header)
    for (index, item) in enumerate(statusList):
        path = item['filePath']
        if (not args.v):
            path = os.path.basename(path[:-1]) + path[-1]
        index = Colors.colorize(index, Colors.PURPLE)
        indexStatus = Colors.colorize(gitFlagDecode[item['mod'][0]], Colors.GREEN)
        treeStats = Colors.colorize(gitFlagDecode[item['mod'][1]], Colors.RED)
        print('{:<16} {:<21}  {:<21}  {} ({})'.format(index, indexStatus, treeStats, path, index))

# Print path
if (args.REF != None):
    statusList = GenerateList()
    print(statusList[int(args.REF)]['filePath'])
    displayList()
# Add file to repo
elif (args.add != None):
    statusList = GenerateList()
    inputRange = parseRange(args.add)
    fileList = ''
    for value in inputRange:
        fileList += statusList[value]['filePath'] + ' '
    bash('git add {}'.format(fileList[:-1]))
    displayList()
# Checkout file
elif (args.checkout != None):
    statusList = GenerateList()
    inputRange = parseRange(args.checkout)
    fileList = ''
    for value in inputRange:
        fileList += statusList[value]['filePath'] + ' '
    bash('git checkout HEAD {}'.format(fileList[:-1]))
    displayList()
# Show diff
elif (args.diff != None):
    statusList = GenerateList()
    bash('git diff HEAD {}'.format(statusList[int(args.diff)]['filePath']))
    displayList()
# Delete file
elif (args.delete != None):
    statusList = GenerateList()
    inputRange = parseRange(args.delete)
    fileList = ''
    for value in inputRange:
        fileList += statusList[value]['filePath'] + ' '
    commandArray = ['rm', '-r', '{}'.format(fileList[:-1])]
    bash(commandArray)
    displayList()
# Edit file
elif (args.edit != None):
    statusList = GenerateList()
    bash('vim {}'.format(statusList[int(args.edit)]['filePath']))
    displayList()
# Reset file
elif (args.reset != None):
    statusList = GenerateList()
    inputRange = parseRange(args.reset)
    fileList = ''
    for value in inputRange:
        fileList += statusList[value]['filePath'] + ' '
    bash('git reset HEAD {}'.format(fileList[:-1]))
    displayList()
else:
    # Display list
    displayList()