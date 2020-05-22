#! /usr/bin/env python3
import argparse
import logging
import os
import subprocess
import sys

from typing import Union, List

LOGGER = logging.getLogger(__name__)
sh = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(sh)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

ITEM_COUNT = 0

class Colors(object):
    BLUE        = '\033[1;34m'
    BOLD        = '\033[;1m'
    CYAN        = '\033[1;36m'
    GREEN       = '\033[1;32m'
    OFF         = '\033[1;;m'
    PURPLE      = '\033[1;35m'
    RED         = '\033[1;31m'
    RESET       = '\033[0;0m'
    REVERSE     = '\033[;7m'
    WHITE       = '\033[1;37m'
    YELLOW      = '\033[1;33m'

    @staticmethod
    def colorize(text, color):
        return color + str(text) + Colors.OFF

def bash(command: Union[List[str], str]):
    if ('list' in str(type(command))):
        command_array = [cmd.replace('"', '') for cmd in command]
    else:
        command_array = command.split()
    LOGGER.debug('Bash: %s', ' '.join(command_array))
    proc = subprocess.Popen(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    (output, err) = proc.communicate()
    return (output, err)

def generateStatusList():
    global ITEM_COUNT
    (output, err) = bash('git status -s')
    if (len(err) != 0):
        raise Exception(err.decode('utf-8'))
    output = output.decode('utf-8')
    lines = output.split('\n')
    # Iterate through git status text
    status_list = []
    for line in lines:
        if (line != ''):
            file_path = line[3:].split(' -> ')[-1]  # handle renamed case
            status_list.append({'mod': line[0:2], 'filePath': file_path})
    ITEM_COUNT = len(status_list) - 1
    return (status_list, ITEM_COUNT)

def checkValidRef(num: Union[str, int]) -> int:
    global ITEM_COUNT
    num = int(num)
    if num < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % num)
    elif num > ITEM_COUNT:
        raise argparse.ArgumentTypeError("%s is an out of range" % num)
    return num

def parseRange(range_string: str) -> List[int]:
    try:
        output = []
        parts = range_string.split(',') # singles
        for part in parts:
            bounds = part.split(':') # range selection
            if (len(bounds) == 2): # defined range
                if (bounds[1] == ''): # unbounded range
                    output += range(int(bounds[0]), ITEM_COUNT + 1)
                else: # bounded range
                    output += range(int(bounds[0]), int(bounds[1]) + 1)
            else: # single int
                output.append(int(part))
    except ValueError:
        LOGGER.info(Colors.colorize("ValueError\n", Colors.RED) + parser.epilog)
        exit(1)
    return output

def checkValidRange(range_string: str) -> str:
    values = parseRange(range_string)
    for value in values:
        checkValidRef(value)
    else:
        return range_string

# credit: https://stackoverflow.com/questions/3305287/python-how-do-you-view-output-that-doesnt-fit-the-screen
# slight modification
class Less(object):
    def __init__(self, num_lines: int=40):
        self.num_lines = num_lines
    def __ror__(self, msg: str):
        if (len(msg.split('\n')) <= self.num_lines):
            LOGGER.info(msg)
        else:
            with subprocess.Popen(["less", "-R"], stdin=subprocess.PIPE) as less:
                try:
                    less.stdin.write(msg.encode("utf-8"))
                    less.stdin.close()
                    less.wait()
                except KeyboardInterrupt:
                    less.kill()
                    bash('stty echo')

def main():
    ######################
    # Generate Status List
    ######################
    global ITEM_COUNT
    global parser
    try:
        status_list, ITEM_COUNT = generateStatusList()
    except Exception as e:
        LOGGER.info(e)
        exit(1)

    less = Less(20)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-v', action='store_true', help='show full paths of files')
    parser.add_argument('--debug', action='store_true', help='show bash commands')

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
    group1.add_argument('-r', type=checkValidRange, metavar='REF_RANGE', dest='reset', help=('eq to ' + Colors.colorize('git reset HEAD ', Colors.GREEN)
                        + Colors.colorize('<file>', Colors.RED)))
    parser.epilog = '''
    {1}   - accepts an {3} for a file reference as referenced in {0} default display
    {2} - accepts an {3}, a {4}, and/or a range in the form {5}
                where x is the start index and y is the end index (inclusive)'''.format(parser.prog,
                                                                                        Colors.colorize('REF_INT', Colors.RESET),
                                                                                        Colors.colorize('REF_RANGE', Colors.RESET),
                                                                                        Colors.colorize('integer', Colors.BOLD),
                                                                                        Colors.colorize('comma separated list', Colors.BOLD),
                                                                                        Colors.colorize('x:y', Colors.BOLD))

    args = parser.parse_args()

    # Debug
    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    git_flag_decode = {
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
        status_list, _ = generateStatusList()
        header = Colors.colorize('#   INDEX     CUR_TREE  FILE', Colors.YELLOW)
        LOGGER.info(header)
        for (index, item) in enumerate(status_list):
            path = item['filePath']
            if (not args.v):
                path = os.path.basename(path[:-1]) + path[-1]
            index = Colors.colorize(index, Colors.PURPLE)
            index_status = Colors.colorize(git_flag_decode[item['mod'][0]], Colors.GREEN)
            tree_stats = Colors.colorize(git_flag_decode[item['mod'][1]], Colors.RED)
            LOGGER.info('{:<16} {:<21}  {:<21}  {} ({})'.format(index, index_status, tree_stats, path, index))

    # Print path if reference given
    if (args.REF != None):
        LOGGER.info(status_list[int(args.REF)]['filePath'])
    # Add file to repo
    elif (args.add != None):
        cmds = ['git', 'add']
        input_range = parseRange(args.add)
        file_list = [status_list[x]['filePath'] for x in input_range]
        cmds.extend(file_list)
        bash(cmds)
        displayList()
    # Checkout file
    elif (args.checkout != None):
        cmds = ['git', 'checkout', 'HEAD']
        input_range = parseRange(args.checkout)
        file_list = [status_list[x]['filePath'] for x in input_range]
        cmds.extend(file_list)
        bash(cmds)
        displayList()
    # Show diff
    elif (args.diff != None):
        cmds = ['git', 'diff', 'HEAD']
        cmds.append(status_list[int(args.diff)]['filePath'])
        (output, err) = bash(cmds)
        output = output.decode('utf-8').split('\n')
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
    # Delete file
    elif (args.delete != None):
        cmds = ['rm', '-r']
        input_range = parseRange(args.delete)
        file_list = [status_list[x]['filePath'] for x in input_range]
        cmds.extend(file_list)
        bash(cmds)
        displayList()
    # Reset file
    elif (args.reset != None):
        cmds = ['git', 'reset', 'HEAD']
        input_range = parseRange(args.reset)
        file_list = [status_list[x]['filePath'] for x in input_range]
        cmds.extend(file_list)
        bash(cmds)
        displayList()
    else:
        # Display list
        displayList()

if __name__ == "__main__":
    main()