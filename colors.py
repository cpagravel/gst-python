# Not used directly, but kept for reference
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

    testText = (
        '%s%s%s\n' % (BLUE, 'BLUE', RESET) +
        '%s%s%s\n' % (BOLD, 'BOLD', RESET) +
        '%s%s%s\n' % (CYAN, 'CYAN', RESET) +
        '%s%s%s\n' % (GREEN, 'GREEN', RESET) +
        '%s%s%s\n' % (PURPLE, 'PURPLE', RESET) +
        '%s%s%s\n' % (RED, 'RED', RESET) +
        '%s%s%s\n' % (RESET, 'RESET', RESET) +
        '%s%s%s\n' % (REVERSE, 'REVERSE', RESET) +
        '%s%s%s\n' % (WHITE, 'WHITE', RESET) +
        '%s%s%s\n' % (YELLOW, 'YELLOW', RESET))

    @staticmethod
    def print_all_colors():
        for i in range(0,15):
            testString = ('{:>3}   '.format(i) + '\033[1;%dm%s%s' % (int(i), i, Colors.OFF))
            print(testString)

    @staticmethod
    def colorize(text, color):
        return color + str(text) + Colors.OFF

    @staticmethod
    def decolorize(text):
        return re.sub(r"\033.*?m", "", text)