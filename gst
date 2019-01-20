#! /usr/bin/env python3
import argparse                                 # parse arguments
import os, subprocess                           # run bash commands
from colors import *

itemCount = 0
def bash(command):
    if ('list' in str(type(command))):
        commandArray = [cmd.replace('"', '') for cmd in command]
    else:
        commandArray = command.split()
    proc = subprocess.Popen(commandArray, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    (output, err) = proc.communicate()
    return (output, err)

def GenerateList():
    global itemCount
    (output, err) = bash('git status -s')
    if (len(err) != 0):
        raise Exception(err.decode('utf-8'))
    output = output.decode('utf-8')
    lines = output.split('\n')
    # Iterate through git status text
    statusList = []
    for line in lines:
        if (line != ''):
            statusList.append({'mod': line[0:2], 'filePath': line[3:]})
    itemCount = len(statusList) - 1
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
        bounds = part.split(':') # range selection
        if (len(bounds) == 2): # defined range
            if (bounds[1] == ''): # unbounded range
                output += range(int(bounds[0]), itemCount + 1) 
            else: # bounded range
                output += range(int(bounds[0]), int(bounds[1]) + 1)
        else: # single int
            output.append(int(part))
    return output

def checkValidRange(string0):
    values = parseRange(string0)
    for value in values:
        if (value < 0):
            argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    else:
        return string0

# credit: https://stackoverflow.com/questions/3305287/python-how-do-you-view-output-that-doesnt-fit-the-screen
# slight modification
class Less(object):
    def __init__(self, num_lines=40):
        self.num_lines = num_lines
    def __ror__(self, msg):
        if (len(msg.split('\n')) <= self.num_lines):
            print(msg)
        else:
            with subprocess.Popen(["less", "-R"], stdin=subprocess.PIPE) as less:
                try:
                    less.stdin.write(msg.encode("utf-8"))
                    less.stdin.close()
                    less.wait()
                except KeyboardInterrupt:
                    less.kill()
                    bash('stty echo')

less = Less(20)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-v', action='store_true', help='show full paths of files')

group1 = parser.add_mutually_exclusive_group()
group1.add_argument('REF', metavar='REF_INT', type=checkValidRef, nargs='?',
                    help='output the file path of a referenced file; can be used for input into other programs')
group1.add_argument('-a', type=checkValidRange, metavar='REF_RANGE', dest='add', help=('eq to ' + Colors.colorize('git add ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-c', type=checkValidRange, metavar='REF_RANGE', dest='checkout', help=('eq to ' + Colors.colorize('git checkout HEAD ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-d', type=checkValidRef, metavar='REF_INT', dest='diff', help=('eq to ' + Colors.colorize('git diff HEAD ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-D', type=checkValidRange, metavar='REF_RANGE', dest='delete', help=('eq to ' + Colors.colorize('rm ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-e', type=checkValidRef, metavar='REF_INT', dest='edit', help=('eq to ' + Colors.colorize('vim ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
group1.add_argument('-r', type=checkValidRange, metavar='REF_RANGE', dest='reset', help=('eq to ' + Colors.colorize('git reset HEAD ', Colors.GREEN) 
                    + Colors.colorize('<file>', Colors.RED)))
parser.epilog = '''
REF_INT   - accepts an integer for a file reference as referenced in {} default display
REF_RANGE - accepts an integer, a comma separated list, and/or a range in the form 'x:y'
            where x is the start index and y is the end index (inclusive)'''.format(parser.prog)

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
    try:
        statusList = GenerateList()
    except Exception as e:
        print(e)
        return
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
# Add file to repo
elif (args.add != None):
    cmds = ['git', 'add']
    statusList = GenerateList()
    inputRange = parseRange(args.add)
    fileList = [statusList[x]['filePath'] for x in inputRange]
    cmds.extend(fileList)
    bash(cmds)
    displayList()
# Checkout file
elif (args.checkout != None):
    cmds = ['git', 'checkout', 'HEAD']
    statusList = GenerateList()
    inputRange = parseRange(args.checkout)
    fileList = [statusList[x]['filePath'] for x in inputRange]
    cmds.extend(fileList)
    bash(cmds)
    displayList()
# Show diff
elif (args.diff != None):
    cmds = ['git', 'diff', 'HEAD']
    statusList = GenerateList()
    cmds.append(statusList[int(args.diff)]['filePath'])
    (output, err) = bash(cmds)
    # (output, err) = bash('git diff HEAD {}'.format(statusList[int(args.diff)]['filePath']))
    output = output.decode('utf-8').split('\n')
    count = 0
    for (index, line) in enumerate(output):
        try:
            if (line[0] == '-'):
                output[index] = Colors.RED + line + Colors.OFF
            elif (line[0] == '+'):
                output[index] = Colors.GREEN + line + Colors.OFF
            elif (line[0:2] == '@@'):
                k = line.rfind('@')
                output[index] = Colors.BLUE + output[index][:k + 1] + Colors.OFF + output[index][k + 1:] 
            elif (line[0:10] == 'diff --git'):
                output[index] = Colors.WHITE + line
                output[index+2] = Colors.WHITE + output[index+2]
                output[index+3] = Colors.WHITE + output[index+3] + Colors.OFF
        except IndexError as e:
            pass
    '\n'.join(output) | less
    # print('\n'.join(output))
# Delete file
elif (args.delete != None):
    cmds = ['rm', '-r']
    statusList = GenerateList()
    inputRange = parseRange(args.delete)
    fileList = [statusList[x]['filePath'] for x in inputRange]
    cmds.extend(fileList)
    bash(cmds)
    displayList()
# Edit file
elif (args.edit != None):
    cmds = ['vim']
    statusList = GenerateList()
    cmds.append(statusList[int(args.edit)]['filePath'])
    bash(cmds)
    displayList()
# Reset file
elif (args.reset != None):
    cmds = ['git', 'reset', 'HEAD']
    statusList = GenerateList()
    inputRange = parseRange(args.reset)
    fileList = [statusList[x]['filePath'] for x in inputRange]
    cmds.extend(fileList)
    bash(cmds)
    displayList()
else:
    # Display list
    displayList()