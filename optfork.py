#!/usr/bin/env python

import sys
from adversary import *

valid_adversary = ["opt", "branching", "revealing", "toofluffy"]
valid_break_tie = [None, "slot", "reach"]

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-a", "--adversary", dest="adv", default = "opt",
                  help="adversary type, one of {}".format(valid_adversary))
parser.add_option("-w", "--w", dest="w", default = "0010",
                  help="characteristic string, should end with a 0")
parser.add_option("-r", "--random",
                  action="store_true", dest="random", default = False,
                  help="use a random string of N bits")
parser.add_option("-n", "--n",
                  type="int", dest="n", default = 10,
                  help="use a random string of N bits")
parser.add_option("-x", "--max-delete-blocks",
                  type="int", dest="max_delete_blocks", default = 10, metavar = "D",
                  help="delete X blocks from the end of non-longest tines")
# parser.add_option("-k", "--weight",
#                   type="int", dest="weight", default = None,
#                   help="use a random string of N bits and weight K")
parser.add_option("-p", "--split-prob",
                  type="float", dest="split_prob", default = 0.5,
                  help="splitting probability")
parser.add_option("-d", "--diagnostics",
                  action="store_true", dest="diagnostics", default = True,
                  help="show diagnostics")
parser.add_option("-s", "--stats",
                  action="store_true", dest="show_stats", default = False,
                  help="show stats")
parser.add_option("-m", "--matrix",
                  action="store_true", dest="show_matrix", default = False,
                  help="show matrix")
parser.add_option("-t", "--tines",
                  action="store_true", dest="show_tines", default = True,
                  help="show tines")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default = False,
                  help="verbose")
parser.add_option("-e", "--diag-verbose",
                  action="store_true", dest="diagnostics_verbose", default = False,
                  help="verbose")
parser.add_option("-l", "--double",
                  action="store_true", dest="double_charstring", default = False,
                  help="verbose")
parser.add_option("-b", "--break-tie", dest="break_tie", default = None,
                  help="tie-breaking basis, one of {}".format(valid_break_tie))

(options, args) = parser.parse_args()



def run_adversary(w = "", split_prob = 0):
	if options.adv == "opt": 
		a = OnlineAdversary(w = w, 
												double_charstring = options.double_charstring, 
												verbose = options.verbose)
	elif options.adv == "branching":
		a = BranchingAdversary(w = w, 
													break_tie = options.break_tie,
													double_charstring = options.double_charstring, 
													verbose = options.verbose)
	elif options.adv == "fluffy":
		a = FluffyAdversary(w = w, splitting_probability = options.split_prob, 
												double_charstring = options.double_charstring, 
												verbose = options.verbose)
	# elif adv == "revealing":
	# 	a = OnlineAdversary(w = w, double_charstring = True)
	else:
		options.print_help()
		print("Unknown adversary: {}".format(options.adv))
		raise ValueError()

	if options.diagnostics:
		a.fork.diagnostics(matrix = options.show_matrix, tines = options.show_tines, verbose = options.diagnostics_verbose)

	return a


def parse_and_play():
	# print(options)
	# print(args)

	# adv
	if options.adv not in valid_adversary:
		print("adv = {} not recognized.".format(options.adv))
		parser.print_help()
		sys.exit(1)	
	print("Using adv: {}".format(options.adv))
	if options.adv == "fluffy":
		print("Using splitting probability: {}".format(options.split_prob))

	# w
	if options.random:
		n = options.n
		import random_wrapper as r
		w = r.random_boolean_string(n - 1)
		w += "0" # force the last bit to be zero
	else:
		w = options.w
		n = len(w)

	if n <= 80:
		print("Using w: {} n: {}".format(w, n))
	else:		
		print("Using w: [too long] n: {}".format(n))

	# split prob
	split_prob = options.split_prob

	# cmd
	run_adv_cmd = "run_adversary(w = '{}')"\
		.format(w)
	trim_cmd = ".fork.trim_tines_and_get_matrix(max_delete_blocks = {}, show_tines = {}, show_matrix = {})"\
		.format(options.max_delete_blocks, options.show_tines, options.show_matrix) 

	cmd = run_adv_cmd + trim_cmd
	# cmd =\
	# 	"run_adversary(adv, w, split_prob, diagnostics = options.diagnostics)" + \
	# 	".fork.trim_tines_and_get_matrix(max_delete_blocks = options.x, show_tines = options.show_tines, show_matrix = options.show_matrix)" 

	# run adversary
	import cProfile
	stats_file = "optfork.new.stats"
	cProfile.run(cmd, stats_file)

	if options.show_stats:
		# print stats
		import pstats
		p = pstats.Stats(stats_file)
		# p.strip_dirs().sort_stats("time").print_stats(10)
		print()
		p.strip_dirs().sort_stats("time").print_stats(10)


def make_w_from_stock(base, n):
	# base = "0110110010"
	# base = "0011010010"
	if n >= 10:
		rep = int(n / 10)
		n = rep * len(base)
	else:
		rep = 1
		n = len(base)
	w = "".join([base] * rep)
	return w




if __name__ == "__main__":
	parse_and_play()

	# adv, w, split_prob = main()

	# # run adversary
	# import cProfile
	# stats_file = "optfork.new.stats"
	# cProfile.run(cmd, stats_file)

	# if show_stats:
	# 	# print stats
	# 	import pstats
	# 	p = pstats.Stats(stats_file)
	# 	# p.strip_dirs().sort_stats("time").print_stats(10)
	# 	print()
	# 	p.strip_dirs().sort_stats("time").print_stats(10)
