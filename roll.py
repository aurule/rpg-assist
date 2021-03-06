#!/usr/bin/python

# This program is made to roll any number of any kind of dice, then display, sum,
# or otherwise manipulate the results. Run with the -h or --help argument for
# description of all supported features.

import argparse
import random
import sys
import re

class Roller(object):
    '''Generic dice roller with many options.'''
    
    def __init__(self, args):
        '''Initialize internal vars. Can populate from an argparser object.'''
        self.sums = 0
        self.successes = 0
        self.rolls = 0
    
        if args is not None:
            self.verbose = args.verbose
            self.boom = args.boom
            self.bust = args.bust
            self.iters = args.iters
            self.dice = args.dice
            self.formula = args.formula
            self.count = args.count
            self.sum = args.sum
            self.add = args.add
            self.target = args.target
        
        self.do_target = self.target > 0
    
    # The roll function. Generates a list of COUNT random numbers from 1 to SIZE.
    # Recursively rolls exploding dice and handles subtraction of botch dice. As
    # such, you NEVER, EVER want an explode threshold of 1, as it will lead to
    # infinite recursion.
    def roll(self, count, size):
        output = []
        newrolls = 0
        for x in xrange(count):
            die = random.randint(1, size)
            if self.boom and die >= self.boom:
                newrolls += 1
            if die <= self.bust:
                newrolls -= 1
            output.append(die)
        if newrolls >= 1:
            output.extend(self.roll(newrolls, size))
        return output

    # Prints the argument as long as the -q option is omitted.
    def print_verbose(self, text):
        if self.count or self.sum:
            if self.verbose:
                print text
        else:
            print text

    def batch_rolls(self):
        # Handles all counting and formula logic.
        for rep in xrange(self.iters):
            summation = 0 #used for addition logic
            total = 0 #used for success threshold logic
            
            # Processes the dice arguments of number and die size, then rolls them.
            rollme = self.dice[:]
            rollme.reverse()
            output = []
            while len(rollme) > 0:
                rolls = int(rollme.pop())
                size = int(rollme.pop())
                output.extend(self.roll(rolls, size))

            if self.iters > 1:
                if self.verbose:
                    print '\n--<Roll ' + str(rep+1) + '>--'
            for num in output:
                if num <= self.bust:
                    num = num * -1
                if self.formula:
                    num = eval(self.formula, {}, {"roll":num})
                if self.sum: summation += num
                if self.count:
                    if num >= self.count:
                        total += 1
                        self.print_verbose('\033[1;32m' + str(num) + '\033[1;m')
                    elif num <= self.bust:
                        total -= 1
                        self.print_verbose('\033[1;31m' + str(num) + '\033[1;m')
                    else:
                        self.print_verbose(num)
                else:
                    self.print_verbose(num)
            if self.sum or self.count:
                self.print_verbose('\033[1;37m-----\033[1;m')
            if self.sum:
                if self.add:
                    added = eval(self.add, {}, {"sum":summation})
                    self.print_verbose(str(summation) + '+' + str(added))
                    summation = summation + int(added)
                print 'Sum: \033[1;36m' + str(summation) + '\033[1;m'
            if self.count:
                if self.iters > 1:
                    if self.verbose:
                        print 'Successes: \033[1;32m' + str(total) + '\033[1;m'
                    else:
                        print 'Roll ' + str(rep+1) + ': \033[1;32m' + str(total) + '\033[1;m'
                else:
                    print 'Successes: \033[1;32m' + str(total) + '\033[1;m'
            
            self.sums += summation
            self.successes += total
            self.rolls += self.iters
            
        if self.do_target:
            if self.successes >= self.target or self.sums >= self.target:
                print 'Rolls: \033[1;36m' + str(self.rolls) + '\033[1;m'
            else:
                self.batch_rolls() #keep rolling until we hit our target

def main():
    soc.batch_rolls()
    return

if __name__ == "__main__":
    # handle presets
    argline = ' '.join(sys.argv)
    argline = re.sub('fate', "4 3 -f roll-2 -s", argline) # fate: 4 3 -f 'roll-2' -s
    argline = re.sub('(\d) nwod', "\g<1> 10 -e 10 -c 8", argline) # N nwod: N 10 -e 10 -c 8
    argline = re.sub('(\d) owod', "\g<1> 10 -e 10 -c 7 -b 1", argline) # N owod X: N 10 -e 10 -c X -b 1
    sys.argv = argline.split()

    parser = argparse.ArgumentParser(description="Roll arbitrary dice.")
    parser.add_argument("-s, --sum", action="store_true", dest="sum", help="Sums the results of all rolls after applying formulas from the -f option.")
    parser.add_argument("-c, --count", dest="count", metavar="TARGET", type=int, help="Counts the number of dice whose values match or exceed TARGET after applying any formulas from the -f option.")
    parser.add_argument("-e, --explode", dest="boom", metavar="THRESHOLD", type=int, default=0, help="If any die matches or exceeds THRESHOLD, it is counted and rolled again. This is applied BEFORE any formulas from the -f option.")
    parser.add_argument("-b, --botch", dest="bust", type=int, default=0, metavar="THRESHOLD", help="If any die is less than or equal to THRESHOLD, it cancels one roll-again from the -e option (if applicable), applied before the extra die is rolled. When paired with any counting option (-c, -s) the die is subtracted from the total instead of added. This subtraction is done AFTER any formulas from the -f option.")
    parser.add_argument("-a, --add", dest="add", type=str, metavar="NUM", help="Add NUM to the total reported using the -s switch. If NUM is a string, it will be interpreted as a simple formula before being added. Within a formula, you can use 'sum' to represent the sum from the dice. This argument implies -s.")
    parser.add_argument("-f, --formula", dest="formula", metavar="FORMULA", type=str, help="Apply FORMULA to every die roll. When combined with -s or -c, the result of the formula is used in place of the die roll. Within the formula, use 'roll' for the outcome of the die roll. Example: -f 'roll*5' will multiply every roll by 5.")
    parser.add_argument("-r, --repeat", dest="iters", type=int, metavar="N", default=1, help="Repeat this roll command N times.")
    parser.add_argument("-v, --verbose", action="store_true", dest="verbose", help="Forces the -c and -s options to show the results of every roll as well as the final count or sum. No effect if used on its own.")
    parser.add_argument("-t, --target", dest="target", type=int, metavar="TARGET", default=0, help="Repeat the roll as many times as needed until their sum is TARGET. If the --count option is used as well, TARGET is the number of rolls exceeding that threshold. Additionally, the number of rolls made is printed.")
    parser.add_argument("dice", type=int, nargs='*', help="Dice to roll, given in pairs of the number of dice to roll, and the sides those dice have.")
    args = parser.parse_args()

    # some basic error checking
    if len(args.dice)%2 <> 0:
        parser.error("Incorrect number of arguments: Rolls and faces must be paired")
    if args.boom == 1:
        parser.error("Invalid argument: Explode threshold will always be satisfied")

    # Makes sure the sum option is automatically set via the add option, as
    # specified in the description.
    args.sum = args.sum or args.add
    
    soc = Roller(args)
    main()
