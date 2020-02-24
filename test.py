#!/usr/bin/env python

import unittest
from charstring import *
from node import *
from fork import *
from tine import *
from adversary import *
from relative_margin import *
from random_wrapper import *


# w="1  1  0  0  1  1  1  0  0  1   1   1   0   1"
# 0--------3-----5
# |        |--------6--7
# |        `-----5--6--7--------10--11
# |--1--2-----4--5
# |           |--5--6--7-----9                       // t9
# |           `--5--6        |
# |                          |--10--11--12------14
# |                           `-10--11--12
# |      
#  `-1--2--------5--6--7--8---------11--12           // t8
#                          `----10--11------13
#                             
def fork_for_matrix():
	f = Fork("11001110011101", force_viable = True)
	t0 = f.root
	# honest blocks, in order
	t3 = f.extend_tine(t0, [3])
	t4 = f.extend_tine(t0, [1,2,4])
	t8 = f.extend_tine(t0, [1,2,5,6,7,8])
	t9 = f.extend_tine(t4, [5,6,7,9])
	t13 = f.extend_tine(t8, [10,11,13])
	# adversarial tines
	tine_extensions = {
		t3: [5, [6,7], [5,6,7,10,11] ],
		t4: [5, [5,6]],
		t8: [ [11,12] ],
		t9: [ [10,11,12,14], [10,11,12] ]
	}
	for tine, exts in tine_extensions.items():
		for ext in exts:
			# print("Extending tine at {} using blocks {}".format(tine.label, ext))
			f.extend_tine(tine, ext)


	return f		

class TestCharString(unittest.TestCase):

	def test_len(self):
		w = CharString("")
		self.assertEqual(0, w.len )
		w = CharString("010")
		self.assertEqual(3, w.len )

	def test_valid(self):
		self.assertRaises(ValueError, CharString, "0a1")
		w = CharString("01")
		self.assertEqual(True, w.valid())
		w = CharString("")
		self.assertEqual(True, w.valid())

	def test_at(self):
		w = CharString("")
		self.assertRaises(IndexError, w.at, 1)
		w = CharString("01")
		self.assertRaises(IndexError, w.at, 3)
		self.assertRaises(IndexError, w.at, -1)
		self.assertEqual('*', w.at(0))
		self.assertEqual('0', w.at(1))
		self.assertEqual('1', w.at(2))

		self.assertTrue(w.is_honest(0))
		self.assertTrue(w.is_honest(1))
		self.assertTrue(w.is_adversarial(2))

	def test_reserve(self):
		w = CharString("")
		self.assertEqual(0, w.reserve(1))
		w = CharString("0")
		self.assertEqual(0, w.reserve(1))
		w = CharString("1")
		self.assertEqual(0, w.reserve(1))
		w = CharString("01")
		self.assertEqual(1, w.reserve(1))
		w = CharString("011")
		self.assertEqual(2, w.reserve(1))

		w = CharString("0101101")
		self.assertEqual(4, w.reserve(0))
		self.assertEqual(4, w.reserve(1))
		self.assertEqual(3, w.reserve(2))
		self.assertEqual(3, w.reserve(3))
		self.assertEqual(2, w.reserve(4))
		self.assertEqual(0, w.reserve(7))

		w = CharString("01011010")
		self.assertEqual(4, w.reserve(0))
		self.assertEqual(4, w.reserve(1))
		self.assertEqual(3, w.reserve(2))
		self.assertEqual(3, w.reserve(3))
		self.assertEqual(2, w.reserve(4))
		self.assertEqual(0, w.reserve(7))
		self.assertEqual(0, w.reserve(8))

		w = "01011010"
		f = Fork("")
		for c in w:
			f.advance_charstring(suffix = c)
		self.assertEqual(4, f.w.reserve(0))
		self.assertEqual(4, f.w.reserve(1))
		self.assertEqual(3, f.w.reserve(2))
		self.assertEqual(3, f.w.reserve(3))
		self.assertEqual(2, f.w.reserve(4))
		self.assertEqual(0, f.w.reserve(7))
		self.assertEqual(0, f.w.reserve(8))


	def test_next_adv_slot(self):
		w = c.CharString("0101001")
		self.assertEqual(2, w.adversarial_slot_after(0))
		self.assertEqual(4, w.adversarial_slot_after(2))
		self.assertEqual(7, w.adversarial_slot_after(4))
		with self.assertRaises(IndexError):
			w.adversarial_slot_after(7)

	def test_adv_slots_after(self):
		w = c.CharString("0101001")
		self.assertEqual([2,4], w.adversarial_slots_after(slot = 0, num_slots = 2))
		self.assertEqual([2,4, 7], w.adversarial_slots_after(slot = 0, num_slots = 3))
		with self.assertRaises(ValueError):
			w.adversarial_slots_after(slot = 0, num_slots = 4)

		self.assertEqual([2,4], w.adversarial_slots_after(slot = 1, num_slots = 2))
		self.assertEqual([2,4,7], w.adversarial_slots_after(slot = 0, num_slots = 3))
		self.assertEqual([4], w.adversarial_slots_after(slot = 2, num_slots = 1))
		self.assertEqual([4,7], w.adversarial_slots_after(slot = 2, num_slots = 2))
		with self.assertRaises((IndexError, ValueError)):
			w.adversarial_slots_after(slot = 7, num_slots = 1)
		with self.assertRaises(IndexError):
			w.adversarial_slots_after(slot = 10, num_slots = 1)

		# requesting zero slots is okay
		self.assertEqual([], w.adversarial_slots_after(slot = 1, num_slots = 0))
		self.assertEqual([], w.adversarial_slots_after(slot = 0, num_slots = 0))

		with self.assertRaises(ValueError):
			w.adversarial_slots_after(slot = 1, num_slots = -4)
		with self.assertRaises(ValueError):
			w.adversarial_slots_after(slot = 1, num_slots = 10)
###################################
class TestNode(unittest.TestCase):

	def test_root(self):
		root = Node()
		self.assertEqual(0, root.depth)
		self.assertEqual(None, root.parent)

	def test_child(self):
		n0 = Node()
		n1 = Node(n0)
		self.assertEqual(1, n1.depth)
		n2 = Node(n1)
		self.assertEqual(2, n2.depth)

	def test_remove_child(self):
		f = Fork("0101")
		# 0--1--2
		# |  \-----3--4
		# ------2
		t0 = f.root
		t1 = f.extend_tine(t0, 1)
		t20 = f.extend_tine(f.root, 2)
		t21 = f.extend_tine(t1, 2)
		t31 = f.extend_tine(t1, 3)
		t43 = f.extend_tine(t31, 4)

		t0.remove_child(t20)
		self.assertTrue(t20 not in t0.children)
		self.assertEqual(len(t0.children), 1)

		# should raise exception
		with self.assertRaises(ValueError):
			t0.remove_child(t21)
		self.assertEqual(len(t0.children), 1)

		# should not delete
		delete_if_slot_3 = lambda node : node.label == 3
		t31.remove_child(t43, delete_if_slot_3) # no change in fork
		self.assertEqual(len(t31.children), 1)

		# should be okay
		delete_if_slot_4 = lambda node : node.label == 4
		t31.remove_child(t43, delete_if_slot_4)
		self.assertTrue(t31.isleaf)
###################################
class TestTine(unittest.TestCase):

	def test_empty_tine(self):
		# A tine does not exist without a fork
		self.assertRaises(ValueError, Tine, None)

		f = Fork()
		t = Tine(fork = f)
		self.assertEqual(0, t.reserve)
		self.assertEqual(0, t.len)

		f = Fork("0101")
		t = Tine(fork = f, label = 0)
		self.assertEqual(2, t.reserve)
		self.assertEqual(0, t.len)
		self.assertEqual(t.reserve, t.reach) # reach of the empty tine equals its reserve

	def test_to_row(self):
		encode_longest_tine_first = True

		for block_encoding in [False, True, True]:
			f = Fork("0101")
			t0 = f.root
			t1 = f.extend_tine(t0, 1)
			t20 = f.extend_tine(f.root, 2)
			t21 = f.extend_tine(t1, 2)
			t31 = f.extend_tine(t1, 3)
			t43 = f.extend_tine(t31, 4)

			if not block_encoding:
				self.assertEqual(list("11000"), t1.to_row(4, block_encoding = False))
				self.assertEqual(list("10200"), t20.to_row(4, block_encoding = False))
				self.assertEqual(list("11200"), t21.to_row(4, block_encoding = False))
				self.assertEqual(list("11010"), t31.to_row(4, block_encoding = False))
				self.assertEqual(list("11012"), t43.to_row(4, block_encoding = False))
			else:
				if encode_longest_tine_first:
					self.assertEqual(list("77075"), t43.to_row(4, longest_tine = True))
					# block encoding preserves state; thus the following test will fail
					self.assertNotEqual(list("33031"), t43.to_row(4, longest_tine = False))
					self.assertEqual(list("77000"), t1.to_row(4))
					self.assertEqual(list("70100"), t20.to_row(4))
					self.assertEqual(list("77100"), t21.to_row(4))
					self.assertEqual(list("77070"), t31.to_row(4))

					encode_longest_tine_first = False
				else:
					self.assertEqual(list("33031"), t43.to_row(4))
					# block encoding preserves state; thus the following test will fail
					self.assertNotEqual(list("77075"), t43.to_row(4, longest_tine = True))
					self.assertEqual(list("33000"), t1.to_row(4))
					self.assertEqual(list("30100"), t20.to_row(4))
					self.assertEqual(list("33100"), t21.to_row(4))
					self.assertEqual(list("33030"), t31.to_row(4))



	def test_path(self):
		f = fork_for_matrix()
		# There's only one node at slot 8
		t8 = f.nodes_by_slot[8][0]

		# preset_honest: 3, preset_adv: 1
		exp_row_slots =  [0, 1, 2, 0, 0, 5, 6, 7, 8, 0, 0, 0, 0, 0, 0]
		exp_row_blocks = [3, 1, 1, 0, 0, 1, 1, 1, 3, 0, 0, 0, 0, 0, 0]
		exp_row = [str(slot) for slot in exp_row_blocks]
		actual_row = t8.to_row(w_len = 14, block_encoding = True)
		self.assertEqual(exp_row, actual_row)

		# prune at slot 7
		exp_row_blocks = [3, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
		exp_row = [str(slot) for slot in exp_row_blocks]
		actual_row = t8.to_row(w_len = 14, block_encoding = True, prune_slot_at = 7)
		self.assertEqual(exp_row, actual_row)

	def test_disjoint(self):
		f = fork_for_matrix()
		t13 = f.nodes_by_slot[13][0]
		t9 = f.nodes_by_slot[9][0]
		t8 = f.nodes_by_slot[8][0]
		t11 = [c for c in t8.children if c.label == 11][0]
		t11 = [c for c in t8.children if c.label == 11][0]
		# t11 = t11s[0]
		self.assertTrue(t13.is_disjoint(t9))

		self.assertFalse(t13.is_disjoint(t8))
		self.assertFalse(t13.is_disjoint(t11))

		self.assertTrue(t13.is_disjoint(t8, suffix_start = 10))
		self.assertTrue(t13.is_disjoint(t11, suffix_start = 9))

		self.assertFalse(t13.is_disjoint(t8, suffix_start = 8))
		self.assertFalse(t13.is_disjoint(t8, suffix_start = 7))

###################################
class TestFork(unittest.TestCase):

	def test_forefront(self):
		f = fork_for_matrix()
		nodes = f.get_nodes_in_forefront_before_slot(1)
		self.assertEqual([f.root], nodes)

		nodes = f.get_nodes_in_forefront_before_slot(2)
		self.assertEqual([1, 1], [n.label for n in nodes])

		nodes = f.get_nodes_in_forefront_before_slot(3)
		self.assertEqual([2, 2], [n.label for n in nodes])

		nodes = f.get_nodes_in_forefront_before_slot(4)
		self.assertEqual(set([3, 2, 2]), set([n.label for n in nodes]))

		nodes = f.get_nodes_in_forefront_before_slot(9)
		self.assertEqual(set([5, 7, 7, 5, 7, 6, 8]), set([n.label for n in nodes]))

	def test_w(self):
		f = Fork("")
		self.assertEqual(True, f.w.valid())
		self.assertEqual(0, f.w.len)
		self.assertRaises(ValueError, Fork, "a1") # invalid cahr string

		f = Fork("01010")
		self.assertEqual("01010", f.w.str())

	def test_root(self):
		f = Fork("")
		self.assertTrue(f.root.honest)
		self.assertTrue(f.root.parent is None)
		self.assertTrue(f.root.bit is 0)


	def test_get_nodes(self):
		f = fork_for_matrix()
		slot = 3

		# partial
		nodes = f.get_nodes_upto_slot(slot = slot)
		for n in nodes:
			self.assertTrue(n.label <= slot)
		for s in range(slot + 1):
			for node in f.nodes_by_slot[s]:
				self.assertTrue(node in nodes)

		# full
		slot = f.w.len
		nodes = f.get_nodes_upto_slot(slot = slot)
		for n in nodes:
			self.assertTrue(n.label <= slot)
		for s in range(slot + 1):
			for node in f.nodes_by_slot[s]:
				self.assertTrue(node in nodes)


		# excess
		slot = f.w.len + 2
		nodes = f.get_nodes_upto_slot(slot = slot)
		for n in nodes:
			self.assertTrue(n.label <= slot)
		for s in range(slot + 1):
			if s <= f.w.len:
				for node in f.nodes_by_slot[s]:
					self.assertTrue(node in nodes)

	def test_balanced_prefix(self):
		f = fork_for_matrix()

		# two tines, length 2
		balanced, t1, t2 = f.is_prefix_balanced_before_slot(3)
		self.assertTrue(balanced) 
		self.assertEqual(set([2, 2]), set([t1.label, t2.label]))
		self.assertEqual([2, 2], [t.len for t in [t1, t2]])

		balanced, t1, t2 = f.is_prefix_balanced_before_slot(4)
		self.assertTrue(balanced) 
		self.assertEqual(set([2, 2]), set([t1.label, t2.label]))
		self.assertEqual([2, 2], [t.len for t in [t1, t2]])
		
		balanced, t1, t2 = f.is_prefix_balanced_before_slot(9)
		self.assertTrue(balanced) 
		self.assertEqual([6, 6], [t.len for t in [t1, t2]])
		self.assertEqual(set([7, 8]), set([t.label for t in [t1, t2]]))
		# self.assertEqual(set([ [0, 1, 2, 5, 6, 7, 8], [0, 1, 2, 4, 5, 6, 7] ]), 
		# 	set([t1.slots(), t2.slots()]))

		# bad cases
		with self.assertRaises(ValueError):
			balanced, t1, t2 = f.is_prefix_balanced_before_slot(1) # root
			balanced, t1, t2 = f.is_prefix_balanced_before_slot(2) # not an honest slot
			balanced, t1, t2 = f.is_prefix_balanced_before_slot(5) # not an honest slot

	def test_honest_blocks(self):
		f = fork_for_matrix()
		n = f.w.len
		for slot in range(0, n+1):
			honest = f.w.is_honest(slot)
			if honest:
				# only one block per slot
				self.assertEqual(1, len(f.nodes_by_slot[slot]))
				# length is at least the honest depth of the previous slot
				if slot >= 1:
					this_block = f.nodes_by_slot[slot][0]
					min_depth = f._honest_depths[slot - 1]
					self.assertTrue(this_block.len >= min_depth, 
													msg = "honest block at slot {} not viable".format(slot))

	def test_sort_nodes(self):
		f = fork_for_matrix()
		nodes = f.get_nodes_upto_slot(3)
		n = len(nodes)
		# default sort: by slot
		s_nodes = sorted_nodes(nodes)
		for i in range(n - 1):
			n1 = s_nodes[i]
			n2 = s_nodes[i+1]
			self.assertTrue(n1.label <= n2.label)

		# sort by length
		s_nodes = sorted_nodes(nodes, by = "len")
		for i in range(n - 1):
			n1 = s_nodes[i]
			n2 = s_nodes[i+1]
			self.assertTrue(n1.len <= n2.len)

		# sort by reach
		s_nodes = sorted_nodes(nodes, by = "reach")
		for i in range(n - 1):
			n1 = s_nodes[i]
			n2 = s_nodes[i+1]
			self.assertTrue(n1.reach <= n2.reach)

		# sort by reach, reverse
		s_nodes = sorted_nodes(nodes, by = "reach", reverse = True)
		for i in range(n - 1):
			n1 = s_nodes[i]
			n2 = s_nodes[i+1]
			self.assertTrue(n1.reach >= n2.reach)


	# Critical tines don't have to be viable
	def test_critical_tines(self):
		# the root is a critical tine
		f = Fork("00")
		self.assertEqual(1, len(f.critical_tines))

		f = Fork("0101")
		t0 = f.root
		t1 = f.extend_tine(f.root, 1)
		self.assertEqual(1, t1.len)
		self.assertEqual(2, t1.reserve)
		self.assertEqual(0, t1.gap)
		self.assertEqual(2, t1.reach)
		self.assertEqual(t1, f.honest_tines_with_largest_reach()[0])
		for t in f.critical_tines:
			self.assertTrue(t.is_viable())

		t20 = f.extend_tine(f.root, 2)
		self.assertEqual(1, t20.len)
		self.assertEqual(0, t20.gap)
		self.assertEqual(1, t20.reserve)
		self.assertEqual(1, t20.reach)
		self.assertEqual(0, len(f.critical_tines))
		self.assertEqual(0, t1.gap)
		self.assertEqual(2, t1.reach)
		self.assertEqual(t1, f.honest_tines_with_largest_reach()[0])

		t21 = f.extend_tine(t1, 2)
		# f.diagnostics()
		self.assertEqual(2, t21.len)
		self.assertEqual(t21.len, f.longest_tine.len)
		self.assertEqual(1, t21.reserve)
		self.assertEqual(0, t21.gap)
		self.assertEqual(1, t21.reach)
		self.assertEqual(1, t1.reach)
		self.assertEqual(0, t20.reach)
		# the root t0 is not a viable tine
		self.assertEqual(2, len(f.critical_tines))
		self.assertEqual(set([t0, t20]), set(f.critical_tines))
		self.assertTrue(not t0.is_viable() and t0.reach is 0)
		self.assertTrue(t20.is_viable() and t20.reach is 0)
		# f.diagnostics()
		# print([t.path for t in f.honest_tines_with_largest_reach()])
		self.assertEqual([t1], f.honest_tines_with_largest_reach())


		t31 = f.extend_tine(t1, 3)
		# f.diagnostics()
		self.assertEqual(2, t31.len)
		self.assertEqual(t31.len, f.longest_tine.len)
		self.assertEqual(1, t31.reserve)
		self.assertEqual(0, t31.gap)
		self.assertEqual(1, t31.reach)
		self.assertEqual(1, t1.reach)  # reserve 2, gap 1
		self.assertEqual(0, t20.reach) # reserve 1, gap 1
		self.assertEqual(1, t21.reach) # reserve 1, gap 0
		# two zero-reach tines...
		zero_reach_tines = [t for t in f.tines.values() if t.reach is 0]
		self.assertEqual(set([t0, t20]), set(zero_reach_tines))
		# ...but they are not viable
		self.assertEqual([], [t for t in zero_reach_tines if t.is_viable()])
		self.assertEqual(set(zero_reach_tines), set(f.critical_tines))

		# If we extend t31 then {t20, t21, t43} will be critical
		t43 = f.extend_tine(t31, 4)
		self.assertEqual(3, t43.len)
		self.assertEqual(t43.len, f.longest_tine.len)
		self.assertEqual(0, t43.reserve)
		self.assertEqual(0, t43.gap)
		self.assertEqual(0, t43.reach) # reserve 0, gap 0
		self.assertEqual(-1, t20.reach) # reserve 1, gap 2
		self.assertEqual(0, t21.reach) # reserve 1, gap 1
		self.assertEqual(2, len(f.critical_tines))
		self.assertEqual(set([t21, t43]), set(f.critical_tines))

		# does the root node ever become a critical tine?
		# f.diagnostics()
		f.advance_charstring("1")
		# f.diagnostics()
		zero_reach_tines = [t for t in f.tines.values() if t.reach is 0]
		self.assertEqual(set([t0, t20]), set(zero_reach_tines))
		# ...but they are not viable
		self.assertEqual([], [t for t in zero_reach_tines if t.is_viable()])
		self.assertEqual(2, len(f.critical_tines))
		self.assertEqual(set([t20, t0]), set(f.critical_tines))


	def test_lca(self):
		f = Fork("0101")
		t0 = f.root
		t1 = f.extend_tine(t0, 1)
		t20 = f.extend_tine(f.root, 2)
		t21 = f.extend_tine(t1, 2)
		t31 = f.extend_tine(t1, 3)
		t43 = f.extend_tine(t31, 4)

		# there should be no 'visited_lca' property in any node
		# cleanup_invariant = lambda node: self.assertFalse(hasattr(node, 'visited_lca'))
		cleanup_invariant = lambda node: self.assertEqual(None, node.visited_lca)

		self.assertEqual(t0, t1.lca(t0))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t1, t1.lca(t1))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t0, t1.lca(t0))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t0, t0.lca(t1))
		f.visit_nodes(cleanup_invariant)

		self.assertEqual(t0, t20.lca(t21))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t0, t21.lca(t20))
		f.visit_nodes(cleanup_invariant)

		self.assertEqual(t1, t1.lca(t21))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t1, t21.lca(t1))
		f.visit_nodes(cleanup_invariant)

		self.assertEqual(t1, t31.lca(t21))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t1, t21.lca(t31))
		f.visit_nodes(cleanup_invariant)

		self.assertEqual(t1, t43.lca(t21))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t1, t21.lca(t43))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t0, t43.lca(t20))
		f.visit_nodes(cleanup_invariant)
		self.assertEqual(t0, t20.lca(t43))
		f.visit_nodes(cleanup_invariant)


	def test_viability(self):
		f = Fork("0010", force_viable = True)
		t0 = f.root
		try:
			f.extend_tine(t0, [1,2]) # good
			t3 = f.extend_tine(t0, [3]) # good
		except Exception:
			self.fail("Unexpected exception.")

		with self.assertRaisesRegex(ValueError, "Viability error"):
			f.extend_tine(t3, [4]) # not viable

	def test_order_of_blocks_in_extension(self):
		f = Fork("0101")
		t0 = f.root
		# a sorted label-list should not raise exception
		try:
			t43 = f.extend_tine(t0, [1,3,4])
		except Exception:
			self.fail("A sorted block-list raised exception")
		# an unsorted label-list should raise exception
		with self.assertRaisesRegex(ValueError, "sorted"):
			f.extend_tine(t0, [1, 4, 3])


	def test_find_critical_tines(self):
		f = fork_for_matrix()
		new = sorted([t.id for t in f.critical_tines])
		# [print("tine at {} reach: {}".format(t.label, t.reach)) for t in f.tines.values()]
		# print("critical tines at : {}".format([t.label for t in f.critical_tines]))
		f._critical_tines = []
		f._find_critical_tines_old()
		old = sorted([t.id for t in f.critical_tines])
		self.assertEqual(str(old), str(new))
		# print("old critical tines at: {}".format([t.label for t in f.critical_tines]))

	# @unittest.skip
	def test_tine_with_best_reach(self):
		f = fork_for_matrix()
		# f.diagnostics(verbose = True)
		# check that the longest tine has length 11
		self.assertEqual(11, f.longest_tine.len)
		self.assertEqual(0, f.longest_tine.reach)


		critical_tines = f.critical_tines
		# # print the reach of every node
		# touch_tine = lambda tine: print("reach: {}, len: {}, label: {}".format(tine.reach, tine.len, tine.label))
		# f.root.visit_subtree(touch_tine)
		# # print the reach of every tine
		# touch_tine = lambda tine: print("reach: {}, len: {}, label: {}".format(tine.reach, tine.len, tine.label))
		# f.root.visit_leaves(touch_tine)


		# critical tines:
		# at 12, length 10
		#	at 14, length 11
		self.assertEqual(2, len(critical_tines))
		params = []
		for tine in critical_tines:
			params.append( (tine.label, tine.len) )
		self.assertEqual(set(params), set([(12, 10), (14, 11)]))

		# as it happens, the tines with the largest reach has reach zero
		best_tines = f.honest_tines_with_largest_reach()
		# f.diagnostics(nodes = True, verbose = True)
		# honest_nodes = [n for arr in f.nodes_by_slot for n in arr if n.honest]
		# [print("honest node: {} reach: {}".format(h.path, h.reach)) for h in honest_nodes]
		# [print("ref tine: {} reach: {}".format(t.path, t.reach)) for t in best_tines]
		# # print
		# # print([str(tine) for tine in best_tines])
		
		# best tine is the honest tine at slot 9
		self.assertEqual(f.nodes_by_slot[9], best_tines)

	def test_fork_for_matrix(self):
		f = fork_for_matrix()
		# # what is the total number of tines?
		tines = f.tines.values()
		for t in tines:
			print("tine: " + t.path)

		# print("\nFork for matrix:")
		# touch_tine = lambda tine: print("tine: reach: {}, length: {}, label: {}".format(tine.reach, tine.len, tine.label))
		# f.root.visit_leaves(touch_tine)

	# @unittest.skip
	def test_matrix(self):
		# f = Fork("0101")
		# t0 = f.root
		# t1 = f.extend_tine(t0, 1)
		# t20 = f.extend_tine(t0, 2)
		# t21 = f.extend_tine(t1, 2)
		# t31 = f.extend_tine(t1, 3)
		# t43 = f.extend_tine(t31, 4)
		# matrix = f.to_matrix()
		# print("\n")
		# for row in matrix:
		# 	print("".join(row))

		f = fork_for_matrix()
		# probe the fork
		print()
		# print_tine_name = lambda tine : print( "{}<--{}".format(tine.parent.label, tine.label) )
		# f.root.visit_leaves(print_tine_name)
		
		# test tines_to_row
		include_root = False
		matrix_rows, ignore, tines = f._tines_to_rows(include_root = include_root)
		str_rows = ["".join(row) for row in matrix_rows]		
		str_rows_expected = [
			"100102000000000",
			"122012000000000",
			"100102220022000",
			"122002221022010",
			"122012220122202",
			"122012220122200",
			"122002221002200",
			"122012200000000",
			"100100220000000"
		]
		if include_root:
			str_rows_expected.append("100000000000000")
		# print("str_rows: ")
		# for r in matrix_rows:
		# 	r_str = "".join(r)
		# 	l = 0
		# 	for c in r_str:
		# 		if c != '0':
		# 			l += 1
		# 	print("{} len: {}".format(r_str, l))
		# print("str_rows_expected: ")
		# for r in str_rows_expected:
		# 	r_str = "".join(r)
		# 	l = 0
		# 	for c in r_str:
		# 		if c != '0':
		# 			l += 1
		# 	print("{} len: {}".format(r_str, l))


		# first, check unordered
		self.assertEqual(set(str_rows_expected), set(str_rows))
		# now check ordered
		self.assertEqual(str_rows_expected, str_rows)

		# test matrix compaction
		rows, ignore, tines = f.to_matrix()
		str_compacted = ["".join(row) for row in rows]
		# remember that the empty tine is also displayed
		str_compacted_expected = [
			"100102000000000",
			"*22012000000000",
			"000*02220022000",
			"*22002221022010",
			"0000*2220122202",
			"000000000*22200",
			"00000000*002200",
			"0000*2200000000",
			"000*00220000000"
		]
		if include_root:
			str_compacted_expected.append("*00000000000000")
		# print("str_compacted: ")
		# for r in str_compacted:
		# 	r_str = "".join(r)
		# 	l = 0
		# 	for c in r_str:
		# 		if c != '0':
		# 			l += 1
		# 	print("{} len: {}".format(r_str, l))
		# print("str_compacted_expected: ")
		# for r in str_compacted_expected:
		# 	r_str = "".join(r)
		# 	l = 0
		# 	for c in r_str:
		# 		if c != '0':
		# 			l += 1
		# 	print("{} len: {}".format(r_str, l))


		self.assertEqual(str_compacted_expected, str_compacted)

		# test to_string()
		f_str = str(f)		
		f_str_expected = "\n".join([
			"1,0,0,1,0,2,0,0,0,0,0,0,0,0,0" ,
			"*,2,2,0,1,2,0,0,0,0,0,0,0,0,0" ,
			"0,0,0,*,0,2,2,2,0,0,2,2,0,0,0" ,
			"*,2,2,0,0,2,2,2,1,0,2,2,0,1,0" ,
			"0,0,0,0,*,2,2,2,0,1,2,2,2,0,2" ,
			"0,0,0,0,0,0,0,0,0,*,2,2,2,0,0" ,
			"0,0,0,0,0,0,0,0,*,0,0,2,2,0,0" ,
			"0,0,0,0,*,2,2,0,0,0,0,0,0,0,0" ,
			"0,0,0,*,0,0,2,2,0,0,0,0,0,0,0"
			])
		# print("f_str: \n{}".format(f_str))
		# print("f_str_expected: \n" + f_str_expected)
		self.assertEqual(f_str_expected, f_str)

	def test_pruning(self):
		f = Fork("0101")
		# 0--1--2
		# |  \-----3--4
		# ------2
		t0 = f.root
		t1 = f.extend_tine(t0, 1)
		t20 = f.extend_tine(f.root, 2)
		t21 = f.extend_tine(t1, 2)
		t31 = f.extend_tine(t1, 3)
		t43 = f.extend_tine(t31, 4)


		self.assertEqual(1, len(f.longest_tines))
		self.assertEqual(t43, f.longest_tine)

		# node.height is not adjusted
		# self.assertEqual(t31.height, 0)
		f.prune_slot(4)
		self.assertTrue(t31.isleaf)
		self.assertEqual(2, len(f.longest_tines))
		self.assertTrue(t31 in f.longest_tines)
		self.assertTrue(t21 in f.longest_tines)
		# self.assertEqual(t31.height, 0)

		f.prune_slot(2)
		self.assertTrue(t1.isleaf)
		self.assertEqual(1, len(f.longest_tines))
		self.assertEqual(t1, f.longest_tine)
		self.assertTrue(t1 in f.longest_tines)

	def test_longest_tines(self):
		f = Fork("01011")
		# 0--1--2
		# |  \-----3--4
		# ------2
		t0 = f.root
		t1 = f.extend_tine(t0, 1)
		t20 = f.extend_tine(f.root, 2)
		t21 = f.extend_tine(t1, 2)
		t31 = f.extend_tine(t1, 3)
		t43 = f.extend_tine(t31, 4)

		# a single longest tine
		self.assertEqual(0, f.longest_tine.gap)
		self.assertEqual(t43, f.longest_tine)
		self.assertEqual(1, len(f.longest_tines))
		self.assertEqual(t43, f.longest_tine)
		tines, length = f.find_longest_tines()
		self.assertEqual(len(tines), 1)
		self.assertEqual(tines[0], t43)

		# newly extended tine is longest; two longest tines
		# 0--1--2-----4
		# |  \-----3--4
		# ------2
		t42 = f.extend_tine(t21, 4)
		self.assertEqual(2, len(f.longest_tines))
		self.assertTrue(t43 in f.longest_tines)
		self.assertTrue(t42 in f.longest_tines)
		for t in f.longest_tines:
			self.assertEqual(0, t.gap)



		self.assertEqual(1, t31.gap)
		self.assertEqual(1, t21.gap)

		# f.diagnostics(tines = True, matrix = False, verbose = True)
		t31.remove_child(t43)
		t21.remove_child(t42)
		f.update_tines()
		# two longest tines
		# 0--1--2
		# |  \-----3
		# ------2
		tines, length = f.find_longest_tines()
		f._longest_tines = tines
		f._longest_tine = tines[0]
		# longest_tines = f.longest_
		# self.assertEqual(tines, )
		self.assertEqual(2, length)
		self.assertEqual(2, t31.len)
		self.assertEqual(2, t21.len)
		self.assertEqual(len(tines), 2)
		self.assertTrue(t31 in tines)
		self.assertTrue(t21 in tines)
		self.assertEqual(0, t31.gap)
		self.assertEqual(0, t21.gap)

	def test_prune_slot(self):
		f = Fork("01010")
		# 0--1--2-----4--5
		# |  \-----3--4
		# ------2
		t0 = f.root
		t1 = f.extend_tine(t0, 1)
		t20 = f.extend_tine(f.root, 2)
		t21 = f.extend_tine(t1, 2)
		t31 = f.extend_tine(t1, 3)
		t43 = f.extend_tine(t31, 4)
		# t42 = f.extend_tine(t21, 4)
		# t54 = f.extend_tine(t42, 5)

		# # now prune	at slot 4	
		f.prune_slot(4)
		# 0--1--2
		# |  \-----3
		# ------2

		# for t in f.tines.values():
		# 	print("tine: {} len: {}".format(t.path, t.len))
		# print("----")
		# for t in f.longest_tines:
		# 	print("tine: {} len: {}".format(t.path, t.len))
		tines = f.longest_tines
		self.assertEqual(2, len(tines))
		self.assertTrue(t31 in tines)
		self.assertTrue(t21 in tines)


	def test_tines_list(self):
		f = Fork("01010")
		# 0--1--2-----4--5
		# |  \-----3--4
		# ------2
		t0 = f.root
		self.assertEqual(1, len(f.tines))

		t1 = f.extend_tine(t0, 1)
		t20 = f.extend_tine(t0, 2)
		t21 = f.extend_tine(t1, 2)
		t31 = f.extend_tine(t1, 3)
		t43 = f.extend_tine(t31, 4)
		t42 = f.extend_tine(t21, 4)
		t54 = f.extend_tine(t42, 5)

		self.assertEqual(4, len(f.tines))
		for t in [t0, t20, t43, t54]:
			self.assertTrue(t.id in f.tines)
			self.assertEqual(t, f.tines[t.id])

		# remove a tine-tip
		# 0--1--2-----4
		# |  \-----3--4
		# ------2
		t42.remove_child(t54, fork = f)
		self.assertEqual(4, len(f.tines))
		for t in [t0, t20, t43, t42]:
			self.assertTrue(t.id in f.tines)
			self.assertEqual(t, f.tines[t.id])

		# now prune	at slot 4	
		f.prune_slot(3)
		# 0--1--2
		# |  
		# ------2
		self.assertEqual(3, len(f.tines))
		for t in [t0, t20, t21]:
			self.assertTrue(t.id in f.tines)
			self.assertEqual(t, f.tines[t.id])

	def test_new_encoding(self):
		f = fork_for_matrix()

		f.diagnostics(
			block_encoding = True, 
			tines = True, matrix = True, verbose = True)

		t14 = f.nodes_by_slot[14][0]
		row14 = [int(v) for v in t14.to_row(f.w.len, block_encoding = True, longest_tine = True)]
		self.assertEqual(row14, [7,5,5,0,7,5,5,5,0,7,5,5,5,0,5])
		
		t13 = f.nodes_by_slot[13][0]
		row13 = [int(v) for v in t13.to_row(f.w.len, block_encoding = True)]
		self.assertEqual([int(v) for v in row13], [7,1,1,0,0,1,1,1,3,0,1,1,0,3,0])

		t9 = f.nodes_by_slot[9][0]
		row9 = [int(v) for v in t9.to_row(f.w.len, block_encoding = True)]
		self.assertEqual(row9, [7,5,5,0,7,5,5,5,0,7,0,0,0,0,0])


	# @unittest.skip("Skipping test_trimming")
	def test_trimming(self):

		w = "0011011010"
		# w = "00110"
		show_tines = True
		show_matrix = False
		print_tines = True
		# prune_slot_at = None
		prune_slot_at = None
		max_delete_blocks = int(len(w) * 0.66)

		if print_tines:
			print("---Test Trimming---")			

		adv = OnlineAdversary(w = w, double_charstring = True, verbose = False)

		if print_tines:
			print("---Done adversary---")			

		print("=========== Before pruning ==============")
		adv.fork.diagnostics(tines = True, matrix = False)
		
		arr = adv.fork.trim_tines_and_get_matrix(
			max_delete_blocks = max_delete_blocks, 
			show_tines = show_tines, 
			show_matrix = show_matrix,
			prune_slot_at = prune_slot_at, 
			verbose = False)


		if print_tines:
			for k in range(0, len(arr)):
				print("{}:\n{}\n".format(k, arr[k]))

	# the two lists must have the same length
	# the prefix list must end with a series of EMPTY values
	def is_prefix_of(self, prefix_arr, big_arr, EMPTY = '0'):		
		# the two lists must have the same length
		self.assertEqual(len(prefix_arr), len(big_arr) )
		n = len(prefix_arr)
		# find the first index where there's a mismatch
		for i in range(n):
			if prefix_arr[i] != big_arr[i]:
				# the rest of the prefix_arr must be zeros
				for j in range(i, n):
					if prefix_arr[j] != EMPTY:
						return False
				break
		return True

	def test_is_prefix_of(self):
		self.assertTrue(self.is_prefix_of([2,3,4,0,0], [2,3,4,5,6], EMPTY = 0))
		self.assertTrue(self.is_prefix_of([0,0,0,0,0], [2,3,4,5,6], EMPTY = 0))
		self.assertFalse(self.is_prefix_of([0,0,0,0,6], [2,3,4,5,6], EMPTY = 0))
		self.assertFalse(self.is_prefix_of([0,3,4,5,6], [2,3,4,5,6], EMPTY = 0))


	def num_nonempty_values_in_row(self, row, EMPTY = '0'):
		n = 0
		for v in row:
			if v != EMPTY:
				n += 1
		return n

	def test_num_nonempty_values_in_row(self):
		self.assertEqual(3, self.num_nonempty_values_in_row([1,2,3], EMPTY = 0))
		self.assertEqual(2, self.num_nonempty_values_in_row([0,2,3], EMPTY = 0))
		self.assertEqual(1, self.num_nonempty_values_in_row([0,2,0], EMPTY = 0))
		self.assertEqual(0, self.num_nonempty_values_in_row([0,0,0], EMPTY = 0))
		self.assertEqual(0, self.num_nonempty_values_in_row([], EMPTY = 0))

	# tests whether the relative (vertical) ordering of tines 
	# in the visualization of the fork, 
	# remains unchanged after trimming trailing blocks 
	# from some of the tines
	def test_stable_trimming(self):

		w = "001010110"
		# w = "00110"
		show_tines = False
		print_tines = True
		max_delete_blocks = int(len(w) * 0.66)
		sort_by_splitting_point = True

		if print_tines:
			print("---Test Trimming---")			

		adv = OnlineAdversary(w = w, double_charstring = False, verbose = False)

		if print_tines:
			print("---Done adversary---")			

		print("=========== Before pruning ==============")
		adv.fork.diagnostics(tines = True, matrix = False)
		
		f = adv.fork

		# add a single adversarial slot
		f.advance_charstring("1")
		self.assertEqual(10, f.w.len)
		t6 = f.nodes_by_slot[6][0]
		t10 = f.extend_tine(t6, [10])
		num_longest_tines = len(f.longest_tines)
		self.assertEqual(2, num_longest_tines)

		arr = f.trim_tines_and_get_matrix_stable(
		# arr = adv.fork.trim_tines_and_get_matrix(
			max_delete_blocks = 2, 
			show_tines = show_tines, 
			sort_by_splitting_point = sort_by_splitting_point,
			verbose = True)		

		if print_tines:
			for k in range(0, len(arr)):
				print("{}:\n{}\n".format(k, arr[k]))

		# rows for the longest tine should remain unchanged across all matrices
		# find those rows
		len_longest = adv.fork.longest_tine.len
		rows_for_longest_tines = []
		mat = arr[0].split("\n")
		for r in range(len(mat)):
			row = mat[r].split(",")
			if self.num_nonempty_values_in_row(row) == len_longest + 1:
				# this row corresponds to a longest tine
				print("{} is a longest-tine row".format(r))
				rows_for_longest_tines.append(r)
		# self.assertEqual(rows_for_longest_tines, [1, 3])
		self.assertEqual(num_longest_tines, len(rows_for_longest_tines))


		# each row should be a prefix of the same row in the previous matrix
		n = len(arr)
		for i in range(n - 1):
			prev = arr[i].split("\n")
			nxt = arr[i + 1].split("\n")
			# nxt may have fewer rows
			for r in range(len(nxt)):
				nxt_row = nxt[r].split(",")
				prev_row = prev[r].split(",")
				if r in rows_for_longest_tines:
					self.assertEqual(nxt_row, prev_row)
				else:
					prev_row_nnz = self.num_nonempty_values_in_row(prev_row, EMPTY = '0')
					nxt_row_nnz = self.num_nonempty_values_in_row(nxt_row, EMPTY = '0')
					self.assertEqual(nxt_row_nnz, prev_row_nnz - 1)
					self.assertTrue(self.is_prefix_of(nxt_row, prev_row, EMPTY = '0'), 
						msg = "\n{} is not a prefix of \n{}".format(nxt_row, prev_row))




	def test_nodes_pq(self):
		f = fork_for_matrix()		
		f.diagnostics()
		print()
		print("longest tine: {}".format(f.longest_tine.path))
		t42 = f.nodes_by_slot[4][0]

		self.assertEqual(4, t42.label)
		arr = list(t42.children)
		[t42.remove_child(child = c, fork = f) for c in arr]
		self.assertTrue(t42.isleaf)
		f.update_tines()
		f.update_longest_tines()


		# [print("node id: {} slot: {} reserve: {} gap: {} reach: {}".format(node.id, node.label, node.reserve, node.gap, node.reach)) \
		#		for arr in f.nodes_by_slot for node in arr]
		# print("---------")


		pq = f.pq_nodes_by_reach_increasing()
		while not pq.isempty():
			node, neg_reach = pq.pop(with_priority = True)
			self.assertEqual(node.reach, -neg_reach)
			self.assertTrue(node.reach >= 0)


		# nodes should be sorted first by reach and then by slot
		pq_types = ["inc", "dec"]
		for pq_type in ["inc", "dec"]:
			if pq_type is "dec":
				pq = f.pq_nodes_by_reach_decreasing(honest_only = True)
			elif pq_type is "inc":
				pq = f.pq_nodes_by_reach_increasing(honest_only = True)

			tines = []
			while not pq.isempty():
				tines.append(pq.pop())
			n = pq.size()
			for pos in range(n-1):
				t1 = tines[pos]
				t2 = tines[pos + 1]
				# first: sort by reach
				if pq_type is "dec":
					self.assertTrue(t1.reach >= t2.reach)
				else:
					self.assertTrue(t1.reach <= t2.reach)
				# then: sort by slot incrasing
				if t1.reach == t2.reach:
					self.assertTrue(t1.label <= t2.label)
	
	def test_tine_with_earliest_slot(self):
		f = fork_for_matrix()
		t5 = f.nodes_by_slot[5][0]
		t10 = f.nodes_by_slot[10][0]
		t7 = f.nodes_by_slot[7][0]
		self.assertEqual(t5, tine_with_earliest_slot([t5, t10, t7]))
		self.assertEqual(t5, tine_with_earliest_slot([t10, t7, t5]))

	
	def test_tine_with_smallest_reach(self):
		f = fork_for_matrix()
		# f.diagnostics(verbose = True, nodes = True)
		t3 = f.nodes_by_slot[3][0] # reach -3
		t4 = f.nodes_by_slot[4][0] # reach -1
		t8 = f.nodes_by_slot[8][0] # reach -1
		t9 = f.nodes_by_slot[9][0] # reeach 0
		self.assertEqual(t3, tine_with_smallest_reach([t3, t4, t8, t9]))
		self.assertEqual(t4, tine_with_smallest_reach([t4, t8, t9]))
		self.assertEqual(t8, tine_with_smallest_reach([t8, t4, t9]))

	def test_tine_with_oldest_split(self):
		f = fork_for_matrix()
		t14 = f.nodes_by_slot[14][0]

		t, ignore, slot = tine_with_oldest_split([t14], [t14])
		self.assertEqual(None, t)
		self.assertEqual(float("inf"), slot)

		# bunch of tines		
		tines = [f.nodes_by_slot[slot][0] for slot in [13, 9, 8, 4]]
		t13 = f.nodes_by_slot[13][0]
		t, ignore, slot = tine_with_oldest_split(tines, [t14])
		self.assertEqual(t13, t)
		self.assertEqual(0, slot)

		t12 = [t for t in f.nodes_by_slot[12] if t.isleaf and 10 in t.slots()][0]
		t6 = [t for t in f.nodes_by_slot[6] if t.isleaf][0]
		t5 = [t for t in f.nodes_by_slot[5] if t.isleaf][0]
		# t4 = f.nodes_by_slot[4][0]
		t, ignore, slot = tine_with_oldest_split([t12, t6], [t14])
		self.assertEqual(t6, t)
		self.assertEqual(4, slot)


###################################
class TestPriorityQueue(unittest.TestCase):
	def test_pq(self):
		import priorityqueue
		pq = priorityqueue.MaxPriorityQueue()
		self.assertEqual(0, pq.size())

		popped = []
		items = [10, 4, 2, 6, 12, 5, 14, 15, 1]
		for item in items:
			pq.insert(item, item)
		self.assertEqual(len(items), pq.size())

		n = len(items)
		while not pq.isempty():
			popped.append(pq.pop())
			n -= 1
			self.assertEqual(n, pq.size())
		self.assertEqual(popped, [15, 14, 12, 10, 6, 5, 4, 2, 1])

		# test items with same priority
		for item in [
			(10, 'ten'), 
			(4,'four'), 
			(2, 'two'),
			(10, 'ten2'), 
			(2, 'two2'),
			(10, 'ten3'), 
			(4,'four2')
			]: 
			pq.insert(item[1], item[0])

		# test items
		items = ['ten', 'ten2', 'ten3', 'four', 'four2', 'two', 'two2']
		self.assertEqual(items, pq.items())
		self.assertEqual(len(items), pq.size())

		# test peek
		item, priority = pq.peek()
		self.assertEqual(['ten', 10], [item, priority]	)
		self.assertEqual(['ten', 10], list(pq.peek())	)
		self.assertEqual('ten', pq.peek_item())
		self.assertEqual(10, pq.peek_priority())

		popped = []
		while not pq.isempty():
			popped.append(pq.pop())
		self.assertEqual(popped, ['ten', 'ten2', 'ten3', 'four', 'four2', 'two', 'two2'])

		# test exclude_item_if
		negative_priority = lambda item, priority : priority < 0
		pq = priorityqueue.MaxPriorityQueue(exclude_item_if = negative_priority)
		for item in [10, 4, 2, 6, 0, -4, 12, 5, 14, 15, 1, -10]:
			pq.insert(item, item)
		popped = []
		while not pq.isempty():
			popped.append(pq.pop())
		self.assertEqual(popped, [15, 14, 12, 10, 6, 5, 4, 2, 1, 0])
###################################
# height of an internal node 
# is the length of the longest path rooted at that node
# height of a leaf node is zero
class TestHeight(unittest.TestCase):
	def test_height(self):
		f = Fork(maintain_heights = True)
		t = Tine(fork = f)

		# single thread
		# 0
		c0 = f.root
		self.assertEqual(c0.height, 0)

		# 0--1--2--3
		c1 = Tine(fork = f, parent = c0)
		c2 = Tine(fork = f, parent = c1)
		c3 = Tine(fork = f, parent = c2)

		# c3.update_height_upstream()
		self.assertEqual(c3.height, 0)
		self.assertEqual(c2.height, 1)
		self.assertEqual(c1.height, 2)
		self.assertEqual(c0.height, 3)

		# 0--1--2--3
		#       |
		#       4--5--6
		c4 = Tine(fork = f, parent = c2)
		c5 = Tine(fork = f, parent = c4)
		c6 = Tine(fork = f, parent = c5)
		c6.update_height_upstream()


		self.assertEqual(c6.height, 0)
		self.assertEqual(c5.height, 1)
		self.assertEqual(c4.height, 2)
		self.assertEqual(c2.height, 3)
		self.assertEqual(c1.height, 4)
		self.assertEqual(c0.height, 5)
		self.assertEqual(c3.height, 0)

		# 0--1--2--3
		#       |
		#       4--5--6
		#       |
		#       7
		c7 = Tine(fork = f, parent = c4)
		self.assertEqual(c7.height, 0)
		self.assertEqual(c6.height, 0)
		self.assertEqual(c5.height, 1)
		self.assertEqual(c4.height, 2)
		self.assertEqual(c2.height, 3)
		self.assertEqual(c1.height, 4)
		self.assertEqual(c0.height, 5)
		self.assertEqual(c3.height, 0)

		# # update_height() works only on leaf node
		# with self.assertRaises(ValueError):
		# 	c2.update_height_upstream()

		# 0--1--2--3
		#       |
		#       4--5
		#       |
		#       7
		c5.remove_child(child = c6, fork = f)
		self.assertEqual(c7.height, 0)
		self.assertEqual(c5.height, 0)
		self.assertEqual(c4.height, 1)
		self.assertEqual(c2.height, 2)
		self.assertEqual(c1.height, 3)
		self.assertEqual(c0.height, 4)
		self.assertEqual(c3.height, 0)

		# 0--1--2--3
		c2.remove_child(child = c4, fork = f)
		self.assertEqual(c2.height, 1)
		self.assertEqual(c1.height, 2)
		self.assertEqual(c0.height, 3)
		self.assertEqual(c3.height, 0)
###################################
class TestKnownFork(unittest.TestCase):

	def check_tines(self, fork, exp_tines):
		tines = [t for t in fork.tines.values() if t is not fork.root]
		tine_slots = [t.slots() for t in tines]
		for exp_tine in exp_tines:
			self.assertTrue(exp_tine in tine_slots)

	def test_11010(self):
		w = "11010"

		adv = OnlineAdversary(w = w)
		# adv.fork.diagnostics()
		# only one tine		
		exp_tines = [
			[0, 3, 5]
		]
		self.check_tines(adv.fork, exp_tines)

		adv = OnlineAdversary(w = w, double_charstring = True, verbose = False)
		# adv.fork.diagnostics()
		exp_tines = [
			[0, 3, 5],
			[0, 3, 4, 6],
			[0, 1, 2, 4, 7, 8, 9, 10]
		]
		self.check_tines(adv.fork, exp_tines)

		# as we are not breaking tie by slot, 
		# the longest tine [0, 3] will be extended upon slot 5
		adv = BranchingAdversary(w = w, verbose = False)
		# adv.fork.diagnostics()
		exp_tines = [
			[0, 3, 5]
		]
		self.check_tines(adv.fork, exp_tines)

		adv = BranchingAdversary(w = w, double_charstring = True, verbose = False)
		# adv.fork.diagnostics()
		exp_tines = [
			[0, 3, 5],
			[0, 3, 4, 6],
			[0, 1, 2, 4, 7, 8, 9, 10]
		]
		self.check_tines(adv.fork, exp_tines)

		adv = BranchingAdversary(w = w, break_tie = "slot", verbose = False)
		# adv.fork.diagnostics()
		exp_tines = [
			[0, 3],
			[0, 1, 5]
		]
		self.check_tines(adv.fork, exp_tines)


		adv = BranchingAdversary(w = w, double_charstring = True, break_tie = "slot", verbose = False)
		# adv.fork.diagnostics()
		exp_tines = [
			[0, 1, 5],
			[0, 3, 4, 6],
			[0, 1, 2, 4, 7, 8, 9, 10]
		]
		self.check_tines(adv.fork, exp_tines)

		adv = BranchingAdversary(w = w, break_tie = "reach", verbose = False)
		# adv.fork.diagnostics()
		exp_tines = [
			[0, 3, 5],
		]
		self.check_tines(adv.fork, exp_tines)

		adv = BranchingAdversary(w = w, double_charstring = True, break_tie = "reach", verbose = False)
		# adv.fork.diagnostics()
		exp_tines = [
			[0, 3, 5],
			[0, 3, 4, 6],
			[0, 1, 2, 4, 7, 8, 9, 10]
		]
		self.check_tines(adv.fork, exp_tines)


	def test_fork_for_matrix(self):
		f = fork_for_matrix()
		exp_tines = [
			[0, 3, 5],
			[0, 3, 6, 7],
			[0, 3, 5, 6, 7, 10, 11],

			[0, 1, 2, 4, 5], 
			[0, 1, 2, 4, 5, 6, 7, 9, 10, 11, 12, 14],
			[0, 1, 2, 4, 5, 6, 7, 9, 10, 11, 12],
			[0, 1, 2, 4, 5, 6],

			[0, 1, 2, 5, 6, 7, 8, 11, 12],
			[0, 1, 2, 5, 6, 7, 8, 10, 11, 13]
		]
		self.check_tines(f, exp_tines)

	# example from the Ouroboros paper
	# w = 0^{2k} 1^k 1001 1^k 0^{2k}
	def forkable_w(self, k = 1):
		zeros = "0" * (2 * k)
		ones = "1" * k
		w = zeros + ones + "1001" + ones + zeros
		return w

	def test_forkable_prefix(self):
		w = self.forkable_w(k = 1)
		n = len(w)
		# append a "0" so that the adversarial tine is actually created
		w_with_honest = w + "0"
		# adv = OnlineAdversary(w = w_with_honest )
		adv = BranchingAdversary(w = w_with_honest
			# , break_tie = "slot" 
			)
		adv.fork.diagnostics()
		balanced, t1, t2, slot = adv.fork.has_forkable_prefix(start_slot = 2)
		self.assertTrue(balanced)
		self.assertEqual(5, slot)
		self.assertEqual(set([2, 4]), set([t1.label, t2.label]))
		self.assertEqual(2, t1.len)
		self.assertEqual(2, t2.len)

		f = fork_for_matrix()
		balanced, t1, t2, slot = f.has_forkable_prefix(start_slot = 3)
		self.assertTrue(balanced)
		self.assertEqual(set([2, 2]), set([t1.label, t2.label]))
		self.assertEqual(3, slot)
		self.assertEqual(2, t1.len)
		self.assertEqual(2, t2.len)

	def test_forkable_w(self):
		for k in range(1, 3):
			w = self.forkable_w(k)
			n = len(w)
			# append a "0" so that the adversarial tine is actually created
			w_with_honest = w + "0"
			# adv = OnlineAdversary(w = w_with_honest )
			adv = BranchingAdversary(w = w_with_honest, break_tie = "slot" )
			adv.fork.diagnostics()
			start_slot = 2
			balanced = True # just to start the loop
			at_least_one_balanced_fork = False
			while balanced:
				balanced, t1, t2, slot = adv.fork.has_forkable_prefix(start_slot = start_slot)
				if balanced:
					print("\nBalanced fork for prefix: {} at slot: {}\n tine: {} len: {}\n tine: {} len: {}"
						.format(adv.fork.w.prefix(slot), slot, t1.path, t1.len, t2.path, t2.len))
					# found a fork; keep scanning
					start_slot = slot + 1
					at_least_one_balanced_fork = True

			self.assertTrue(at_least_one_balanced_fork)


	def test_trident(self):
		w = self.forkable_w(k = 2)
		n = len(w)
		# append a "0" so that the adversarial tine is actually created
		w_with_honest = w + "0"
		adv = OnlineAdversary(w = w_with_honest, verbose = False )
		# adv = BranchingAdversary(w = w_with_honest)
		adv.fork.diagnostics()



####################################
class TestAdv(unittest.TestCase):

	def test_tines_of_interest(self):
		w = "11010110100000"
		adv = BranchingAdversary(w = w)
		adv.fork.diagnostics(nodes = True)
		tines, has_critical = adv.tines_of_interest()
		# these tines must be sorted by reach, increasing
		n = len(tines)
		for pos in range(n - 1):
			t1 = tines[pos]
			t2 = tines[pos + 1]
			self.assertEqual(t1.reach <= t2.reach)

	def show(self, arr):
		for k in range(0, len(arr)):
			print("k = {}:\n{}\n".format(k, arr[k]))

	def do_trim(self, 
		adv = None,
		show_tines = True,
		show_matrix = False,
		print_tines = True,
		block_encoding = True,
		prune_slot_at = None,
		max_delete_blocks = 2,
		verbose = False):

		redo_prune_slot = False
		if prune_slot_at:
			redo_prune_slot = True
			saved_prune_slot = prune_slot_at
			prune_slot_at = None

		arr = adv.fork.trim_tines_and_get_matrix(
			max_delete_blocks = max_delete_blocks, 
			show_tines = show_tines, 
			show_matrix = show_matrix,
			block_encoding = block_encoding,
			prune_slot_at = prune_slot_at,
			verbose = verbose
			)
		if print_tines:
			self.show(arr)

		if redo_prune_slot:
			prune_slot_at = saved_prune_slot
			print("Pruning slot: {}".format(prune_slot_at))

			arr = adv.fork.trim_tines_and_get_matrix(
				max_delete_blocks = max_delete_blocks, 
				show_tines = show_tines, 
				show_matrix = show_matrix,
				block_encoding = block_encoding,
				prune_slot_at = prune_slot_at,
				verbose = verbose
				)
			if print_tines:
				self.show(arr)

	# @unittest.skip("Skipping test_trimming")
	def test_slider(self):
		verbose = False
		max_delete_blocks = 7
		show_matrix = True
		double_charstring = True

		# w = "0011011001000010"
		# w = "10110101101011010110"
		w = "00110"
		print("w: {} len: {}".format(w, len(w)))
	
		n = len(w)
		prune_slot_at = None

		adv = BranchingAdversary(w = w, double_charstring = double_charstring)

		self.do_trim(
			adv = adv,
			show_matrix = show_matrix,
			prune_slot_at = prune_slot_at,
			max_delete_blocks = max_delete_blocks,
			verbose = verbose
		)

	def test_double(self):
		# w = "0011011001000010"
		w = "0010"
		show_matrix = False

		adv = OnlineAdversary(w = w)
		adv.fork.diagnostics(matrix = show_matrix)

		double_charstring = True
		adv = OnlineAdversary(w = w, double_charstring = double_charstring)
		# adv = OnlineAdversary(w = "0101", verbose = False)

		self.do_trim(
			adv = adv,
			show_tines = True,
			show_matrix = show_matrix,
			print_tines = True,
			prune_slot_at = len(w) + 1,
			max_delete_blocks = 2
		)

	def test_build(self):
		# w = "11001110011101"
		adv = OnlineAdversary()
		f = adv.fork
		self.assertEqual(0, f.w.len)
		self.assertTrue(f.w.valid())

		adv._build("0", no_action = True)
		self.assertEqual(1, f.w.len)
		self.assertTrue(f.w.valid())

		adv._build("1", no_action = True)
		self.assertEqual(2, f.w.len)
		self.assertTrue(f.w.valid())

		adv._build("0", no_action = True)
		self.assertEqual(3, f.w.len)
		self.assertTrue(f.w.valid())

		adv._build("1", no_action = True)
		self.assertEqual(4, f.w.len)
		self.assertTrue(f.w.valid())

		# now extend tines
		t0 = f.root
		# print(f._honest_depths)
		t1 = f.extend_tine(t0, 1)
		t20 = f.extend_tine(t0, 2)
		t21 = f.extend_tine(t1, 2)
		t31 = f.extend_tine(t1, 3)
		t43 = f.extend_tine(t31, 4)
		self.assertEqual(list('33031'), t43.to_row(f.w.len))
		# self.assertEqual("1,1,0,1,2", str(t43))

	# def test_w(self):
	# 	w = "010101"
	# 	adv = RevealingOnlineAdversary(w = w)
	# 	self.assertEqual(adv.fork.w.len, 12)
	# 	self.assertEqual(str(adv.fork.w), w + "000000")

	# @unittest.skip("Skipping test_see")
	def test_see(self):
		# w = "101010"
		# w = "0011011001000010"
		# w = "111010101000101"
		w = "10111110010"

		
		adv_paper = OnlineAdversary(w = w, verbose = True)
		adv_paper.fork.diagnostics(matrix = False, nodes = True, verbose = True)
		# tines = adv_paper.fork.tines.values()
		# self.assertTrue(adv_paper.fork.root in tines)
		# self.assertEqual(2, len(tines)) # one non-trivial tine

		# adv = RevealingAdversary(w = w)
		# adv.fork.diagnostics(matrix = False, tines = True)
		# tines = adv.fork.tines.values()
		# self.assertTrue(adv.fork.root in tines)
		# self.assertTrue(len(tines) >= 3) # at least two two non-trivial tines
		# # for t in adv.fork.longest_tines:
		# # 	print("longest {}".format(t.path))

		# self.assertEqual(1, len(adv.fork.longest_tines))


	def w_is_all_zeros(self, w):
		if w:
			n = len(w)
			return w == ("0" * n)

	def num_leading_ones(self, w):
		num_leading_ones = 0
		if w:
			for c in w:
				if c == '1':
					num_leading_ones += 1
				else:
					break
		return num_leading_ones


	def single_tine(self, adv_type, break_tie = None, double_charstring = False):
		assert adv_type in ["branching", "opt"]		
		verbose = False
		n = 7

		for k in range(0,pow(2, n - 1)):
			val = 2 * k
			# binary representation of k
			w = "{0:b}".format(val).zfill(n)
			
			if adv_type == "branching":
				adv = BranchingAdversary(	w = w, 
																	break_tie = break_tie, 
																	double_charstring = double_charstring)
			elif adv_type == "opt":
				adv = OnlineAdversary(w = w, double_charstring = double_charstring)

			tines = adv.fork.tines.values() 
			num_tines = len(tines) - 1 # subtract one for the root
			if num_tines <= 1:
				# okay if w contains at least n/2 ones
				# or w = 000...
				num_leading_ones = self.num_leading_ones(w) 
				all_zeros = self.w_is_all_zeros(w)
				print("adversary: {} w: {} num_tines: {}".format(adv_type, w, num_tines))
				okay = all_zeros or num_leading_ones >= n/2
				if not okay:
					adv.fork.diagnostics()
				self.assertTrue(okay)


	def test_single_tine(self):
		# w = "101010"
		# w = "0011011001000010"
		# w = "111010101000101"
		# w = "00100"
		self.single_tine("branching", double_charstring = False, break_tie = "slot")
		self.single_tine("branching", double_charstring = True)
		self.single_tine("opt", double_charstring = True)

	def test_trim_two_longest_tines(self):
		w = "00110"
		adv = OnlineAdversary(w = w)
		self.assertEqual(2 + 1, len(adv.fork.tines)) # the root

		# extend t21 with adv block at 4
		t21 = adv.fork.nodes_by_slot[2][0]
		adv.fork.extend_tine(t21, 4)
		self.assertEqual(2 + 1, len(adv.fork.tines)) # the root
		t42 = adv.fork.nodes_by_slot[4][1]
		self.assertTrue(t42.isleaf) # the new leaf
		self.assertFalse(t21.isleaf) # the new leaf
		self.assertEqual(2, len(adv.fork.longest_tines)) # two longest tines

		arr = adv.fork.trim_tines_and_get_matrix(max_delete_blocks = 5)
		print(arr)
		for matrix in arr:
			# there will be two rows in the matrix
			self.assertEqual(2, len(matrix.split("\n")))

	# @unittest.skip("Skipping test_extend_longest_tine")
	def menagerie(self):
		random = False
		verbose = False
		double_charstring = False
		n = 10
		if random:
			import random_wrapper as r
			w = r.random_boolean_string(n - 1) + "0"
			print("Random w: {}".format(w))
		else:
			# # w = "101010"
			# w = "0100100111"
			# w = "0011011001000010"
			# w = "1101110100"

			# w = "1011010110"
			w = "1011010110" * 2
		
		adv_paper = OnlineAdversary(w = w, verbose = verbose)
		print("\n>>>>> Parsimonious adversary")
		adv_paper.fork.diagnostics(matrix = False, tines = True)
		
		
		# adv_paper = OnlineAdversary(w = w, verbose = False, double_charstring = True)
		# print("\n>>>>> Parsimonious adversary (double_charstring = {})".format(adv_paper.double_charstring))
		# adv_paper.fork.diagnostics(matrix = False, tines = True)


		print("\n>>>>> Branching adversary")
		adv = BranchingAdversary(w = w, verbose = verbose)
		adv.fork.diagnostics(matrix = False, tines = True)

		# print("\n>>>>> Fluffy adversary")
		# adv = FluffyAdversary(w = w, verbose = verbose)
		# adv.fork.diagnostics(matrix = False, tines = True)





####################################
class TestMargin(unittest.TestCase):
	def test_margin(self):
		w = None
		r, m = reach_and_margin(w)
		self.assertTrue(r == [] and m == [])

		w = "1"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 1], r)
		self.assertEqual([0, 1], m)
		w = "0"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 0], r)
		self.assertEqual([0, -1], m)
		w = "11"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 1, 2], r)
		self.assertEqual([0, 1, 2], m)
		w = "10"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 1, 0], r)
		self.assertEqual([0, 1, 0], m)
		w = "00"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 0, 0], r)
		self.assertEqual([0, -1, -2], m)
		w = "01"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 0, 1], r)
		self.assertEqual([0, -1, 0], m)
		w = "000"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 0, 0, 0], r)
		self.assertEqual([0, -1, -2, -3], m)
		w = "001"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 0, 0, 1], r)
		self.assertEqual([0, -1, -2, -1], m)
		w = "010"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 0, 1, 0], r)
		self.assertEqual([0, -1, 0, 0], m)
		w = "011"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 0, 1, 2], r)
		self.assertEqual([0, -1, 0, 1], m)
		w = "100"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 1, 0, 0], r)
		self.assertEqual([0, 1, 0, -1], m)
		w = "101"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 1, 0, 1], r)
		self.assertEqual([0, 1, 0, 1], m)
		w = "110"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 1, 2, 1], r)
		self.assertEqual([0, 1, 2, 1], m)
		w = "111"
		r, m = reach_and_margin(w)
		self.assertEqual([0, 1, 2, 3], r)
		self.assertEqual([0, 1, 2, 3], m)

		w = "1100000101111011011001000100001011"
		r, m = reach_and_margin(w)
		rr = [0,1,2,1,0, 0, 0, 0, 1, 0, 1, 2,3,4,3,4,5,4,5,6,5,4,5,4,3,2,3,2,1,0,0, 1,0,1,2]
		mm = [0,1,2,1,0,-1,-2,-3,-2,-3,-2,-1,0,1,0,1,2,1,2,3,2,1,2,1,0,0,1,0,0,0,-1,0,0,1,2]
		# print("w  : {}".format(w))
		# print("exp    r: {}".format(rr))
		# print("actual r: {}".format(r))
		# print("exp    m: {}".format(mm))
		# print("actual m: {}".format(m))
		self.assertEqual(rr, r)
		self.assertEqual(mm, m)


	def test_relative_margin(self):
		w = "1"
		r, m = reach_and_margin(w, 0)
		self.assertEqual([0, 1], r)
		self.assertEqual([0, 1], m)
		w = "1"
		r, m = reach_and_margin(w, 1)
		self.assertEqual([0, 1], r)
		self.assertEqual([1], m)
		w = "0"
		r, m = reach_and_margin(w, 1)
		self.assertEqual([0, 0], r)
		self.assertEqual([0], m)
		w = "000"
		r, m = reach_and_margin(w, 1)
		self.assertEqual([0, 0, 0, 0], r)
		self.assertEqual([0, -1, -2], m)
		r2, m = reach_and_margin(w, 2, reach = r)
		self.assertEqual([0, -1], m)
		self.assertEqual(r2, r)
		w = "101"
		r, m = reach_and_margin(w, 1)
		self.assertEqual([0, 1, 0, 1], r)
		self.assertEqual([1, 0, 1], m)
		r2, m = reach_and_margin(w, 2, reach = r)
		self.assertEqual(r2, r)
		self.assertEqual([0, 1], m)
		r3, m = reach_and_margin(w, 3, reach = r)
		self.assertEqual([1], m)
		self.assertEqual(r3, r)
		w = "111"
		r, m = reach_and_margin(w, 1)
		self.assertEqual([0, 1, 2, 3], r)
		self.assertEqual([1, 2, 3], m)
		r2, m = reach_and_margin(w, 2, reach = r)
		self.assertEqual([2, 3], m)
		self.assertEqual(r2, r)
		r3, m = reach_and_margin(w, 3, reach = r)
		self.assertEqual([3], m)
		self.assertEqual(r3, r)

		w = "1100000101111011011001000100001011"
		r, m = reach_and_margin(w)
		rr = [0,1,2,1,0, 0, 0, 0, 1, 0, 1, 2,3,4,3,4,5,4,5,6,5,4,5,4,3,2,3,2,1,0,0, 1,0,1,2]
		mm = [0,1,2,1,0,-1,-2,-3,-2,-3,-2,-1,0,1,0,1,2,1,2,3,2,1,2,1,0,0,1,0,0,0,-1,0,0,1,2]
		# print("w  : {}".format(w))
		# print("exp    r: {}".format(rr))
		# print("actual r: {}".format(r))
		# print("exp    m: {}".format(mm))
		# print("actual m: {}".format(m))
		self.assertEqual(rr, r)
		self.assertEqual(mm, m)
		r2, m = reach_and_margin(w, 2, reach = r)
		mm = [2,1,0,-1,-2,-3,-2,-3,-2,-1,0,1,0,1,2,1,2,3,2,1,2,1,0,0,1,0,0,0,-1,0,0,1,2]
		self.assertEqual(mm, m)
		self.assertEqual(r2, r)
		r3, m = reach_and_margin(w, 7, reach = r)
		mm = [0, 1, 0, 1, 2,3,4,3,4,5,4,5,6,5,4,5,4,3,2,3,2,1,0,-1,0,0,1,2]
		self.assertEqual(mm, m)
		self.assertEqual(r3, r)

	def test_partial_sum_min(self):
		w = None
		psum, pmin = partial_sum_min(w)
		self.assertEqual([], psum)
		self.assertEqual([], pmin)

		w = "0"
		psum, pmin = partial_sum_min(w)
		self.assertEqual([0,-1], psum)
		self.assertEqual([0,-1], pmin)
		w = "1"
		psum, pmin = partial_sum_min(w)
		self.assertEqual([0,1], psum)
		self.assertEqual([0,0], pmin)

		w = "010"
		psum, pmin = partial_sum_min(w)
		self.assertEqual([0,-1,0,-1], psum)
		self.assertEqual([0,-1,-1,-1], pmin)

		w = "010001101100"
		psum, pmin = partial_sum_min(w)
		self.assertEqual([0,-1,0, -1,-2,-3,-2,-1,-2,-1, 0,-1,-2], psum)
		self.assertEqual([0,-1,-1,-1,-2,-3,-3,-3,-3,-3,-3,-3,-3], pmin)


	def test_left_catalan(self):
		w = None
		lcat = left_catalan_slots(w)
		self.assertEqual([], lcat)

		w = "0"
		lcat = left_catalan_slots(w)
		self.assertEqual([1], lcat)
		w = "1"
		lcat = left_catalan_slots(w)
		self.assertEqual([], lcat)
		w = "010"
		lcat = left_catalan_slots(w)
		self.assertEqual([1], lcat)
		w = "0010"
		lcat = left_catalan_slots(w)
		self.assertEqual([1,2], lcat)
		w = "10010"
		lcat = left_catalan_slots(w)
		self.assertEqual([3], lcat)
		# w = "11000 00 10 111101101100100010000 1011"
		w = "1100000101111011011001000100001011"
		lcat = left_catalan_slots(w)
		self.assertEqual([5,6,7,30], lcat)

		w = "001000101010010"
		# w = "0 010 0 0101010 010"
		lcat = left_catalan_slots(w)
		self.assertEqual([1,2,5,6,13], lcat)
		w = "0010001010100101"
		# w = "0 010 0 0101010 0101"
		lcat = left_catalan_slots(w)
		self.assertEqual([1,2,5,6,13], lcat)




	def test_right_catalan(self):
		w = None
		rcat = right_catalan_slots(w)
		self.assertEqual([], rcat)

		w = "0"
		rcat = right_catalan_slots(w)
		self.assertEqual([1], rcat)
		w = "1"
		rcat = right_catalan_slots(w)
		self.assertEqual([], rcat)
		w = "010"
		rcat = right_catalan_slots(w)
		self.assertEqual([3], rcat)
		w = "0010"
		rcat = right_catalan_slots(w)
		self.assertEqual([1,4], rcat)
		w = "10010"
		rcat = right_catalan_slots(w)
		self.assertEqual([2,5], rcat)
		w = "001000101010010"
		# w = "001 0 0010101 001 0"
		rcat = right_catalan_slots(w)
		self.assertEqual([1,4,5,12,15], rcat)
		w = "0010001010100101"
		# w = "001 0 0010101 00101"
		rcat = right_catalan_slots(w)
		self.assertEqual([1,4,5,12], rcat)


	def test_catalan(self):
		w = None
		rcat = right_catalan_slots(w)
		self.assertEqual([], rcat)

		w = "0"
		cat = catalan_slots(w)
		self.assertEqual([1], cat)
		w = "1"
		cat = catalan_slots(w)
		self.assertEqual([], cat)
		w = "001000101010010"
		cat = catalan_slots(w)
		self.assertEqual([1,5], cat)
		w = "0010001010100101"
		cat = catalan_slots(w)
		self.assertEqual([1,5], cat)

	# test cat_slot <=> negative relative margin for all prefix
	def verify_catalan_implies_neg_margin(self, w, verbose = False):
		cat = catalan_slots(w)
		if verbose:
			print("w: {}\ncat: {}".format(w, cat))

		for cat_slot in cat:
			# x must end before cat_slot
			for x_len in range(cat_slot - 1, -1, -1):
				reach, margin = reach_and_margin(w, x_len)
				# xy must span cat_slot
				for xy_len in range(cat_slot, len(w)):
					y_len = xy_len - x_len
					self.assertTrue(0 > margin[y_len], 
						"x_len: {}, cat_slot: {}, xy_len: {},\nmargin: {}\nw: {}".format(x_len, cat_slot, xy_len, margin, w))

	def test_catalan_neg_margin(self):
		w = "001000101010010"
		cat = catalan_slots(w)
		self.assertEqual([1,5], cat)
		# test that the relative margin is negative
		self.verify_catalan_implies_neg_margin(w)

	def test_catalan_implies_neg_margin_exhaustive(self):
		# n = 20
		n = 10	

		for k in range(0,pow(2, n)):
			# val = 2 * k
			# binary representation of k
			w = "{0:b}".format(k).zfill(n)
			self.verify_catalan_implies_neg_margin(w)

	def test_catalan_implies_neg_margin_long_random(self):
		# n = 300
		n = 10
		num_samples = 1
		verbose = True

		for pr_one in [0.4]:
			for i in range(num_samples):
				w = random_boolean_string(n = n, pr_one = pr_one)
				# print("w: " + w)
				self.verify_catalan_implies_neg_margin(w, verbose = verbose)
				self.verify_neg_margin_implies_catalan(w, verbose = verbose)

	def verify_neg_margin_implies_catalan(self, w, verbose = False):
		n = len(w)
		cat = catalan_slots(w)
		if verbose:
			print("w: {}\ncat: {}".format(w, cat))
		r, ignore = reach_and_margin(w)
		for x_len in range(n):
			ignore, m = reach_and_margin(w, x_len, reach = r)
			m.pop(0)
			# print("m:     {}".format(m))
			# remove the first item (empty y)
			has_non_neg = len([1 for v in m if v >= 0]) >= 1
			# print("has_non_neg: {}".format(has_non_neg))
			if not has_non_neg:
				cat_slot = x_len + 1
				self.assertTrue(cat_slot in cat)

	def test_neg_margin_implies_catalan(self):
		w = "001000101010010"
		cat = catalan_slots(w)
		self.assertEqual([1,5], cat)
		self.verify_neg_margin_implies_catalan(w)

	def test_neg_margin_implies_catalan_exhaustive(self):
		# n = 20
		n = 10

		for k in range(0,pow(2, n)):
			# val = 2 * k
			# binary representation of k
			w = "{0:b}".format(k).zfill(n)
			self.verify_neg_margin_implies_catalan(w)


	def test_neg_margin_implies_catalan_long_random(self):
		# n = 300
		n = 50
		num_samples = 1
		verbose = True

		for pr_one in [0.4]:
			for i in range(num_samples):
				w = random_boolean_string(n = n, pr_one = pr_one)
				# print("w: " + w)
				self.verify_neg_margin_implies_catalan(w, verbose = verbose)

	def test_catalan_equiv_neg_margin_long_random(self):
		# n = 300
		n = 50
		num_samples = 1
		verbose = False

		for pr_one in [0.4]:
			for i in range(num_samples):
				w = random_boolean_string(n = n, pr_one = pr_one)
				# print("w: " + w)
				self.verify_catalan_implies_neg_margin(w, verbose = verbose)
				self.verify_neg_margin_implies_catalan(w, verbose = verbose)


# Run the tests
if __name__ == '__main__':
	unittest.main()