

import charstring as c
import tine as t

class Fork:
	'''Fork'''


	def __init__(self, char_str = "" , force_viable = False, maintain_heights = False):
		# self._raw_char_str = char_str
		self._w = c.CharString(char_str) # empty string
		if not self.w.valid():
			raise ValueError("'{}' is not a valid characteristic string.".format(self.w))

		self._maintain_heights = maintain_heights

		self._honest_depths = []
		self._nodes_by_slot = []
		for slot in range(0, self.w.len + 1): # the index zero is for indexing convenience
			self._honest_depths.append(0) # initially
			self._nodes_by_slot.append([]) # initially

		
		self.node_counter = 0

		# self.root = t.Tine(fork = self) # empty tine
		self.root = t.Tine(self) # empty tine
		self._longest_tine = self.root   # initial value
		self._longest_tines = [self.root]   # initial value
		self._critical_tines = [self.root] # initially
		self.tines = {self.root.id : self.root} 	# initial list of all tines
		# self.lca_table = {}

		self._num_slots_seen = 0 # no slot seen so far

		if isinstance(force_viable, bool):
			self._force_viable = force_viable
		else:
			raise ValueError("force_viable must be boolean")
		
		self._find_critical_tines()

		if self._w == "":
			self.adversarial_slots = []
			self.num_adversarial_slots = 0
		else:
			self.adversarial_slots = self.w.all_adversarial_slots()
			self.num_adversarial_slots = len(self.adversarial_slots)



	# ============= Setter/getters ===============

	def _get_num_slots_seen(self):
		return self._num_slots_seen
	num_slots_seen = property(_get_num_slots_seen)
	
	

	def _get_longest_tines(self):
		return self._longest_tines
	longest_tines = property(_get_longest_tines)

	def _get_longest_tine(self):
		return self._longest_tine
	longest_tine = property(_get_longest_tine)

	def _get_critical_tines(self):
		return self._critical_tines
	critical_tines = property(_get_critical_tines)


	def _get_w(self):
		return self._w

	w = property(_get_w)

	def _get_nodes_by_slot(self):
		return self._nodes_by_slot

	nodes_by_slot = property(_get_nodes_by_slot)
	

	# # ============ LCA table ===============
	# def lca_key(self, tine1, tine2):
	# 	return str(sorted([tine1.id, tine2.id]))

	# def lca(self, tine1, tine2):
	# 	key = self.lca_key(tine1, tine2)
	# 	if key in self.lca_table:
	# 		return self.lca_table[key]
	# 	else:
	# 		lca = tine1.lca(tine2)
	# 		self.lca_table[key] = lca
	# 		return lca


	# ============ Methods executed after a node is created/deleted ==================
	def on_new_node(self, node):
		self._nodes_by_slot[node.label].append(node)
		# attach id
		node.id = self.node_counter

		# increment the node counter
		self.node_counter += 1
		# print("node id: {}".format(node.id))

		# update height
		if self._maintain_heights:
			node.update_height_upstream()

		# update the list of tines
		# special: root is always a tine
		# if node.id == 0:
		# 	self.tines[node.id] = node


	# this method is SLOPPY
	# it does not update self.tines or self.longest_tines
	# nor is it recursive
	def on_node_deleted(self, child, parent = None):
		if child is self.root:
			raise ValueError("Error: root node deleted")

		if parent is None:
			parent = child.parent

		# update node_by_slot
		self._nodes_by_slot[child.label].remove(child)

		# update height
		if self._maintain_heights:
			parent.update_height_upstream(removal = True)

		# update the list of tines
		try:
			# before = str(fork.tines.keys())

			# recursive deletion
			# if not child.isleaf:
			# 	# remove all children as well
			# 	arr = list(child.children)
			# 	[child.remove_child(child = c, fork = self) for c in arr]

			# the child is no longer a tine
			del self.tines[child.id]
			# make parent the new tine if it is now a leaf
			if parent.isleaf:
				self.tines[parent.id] = parent


			# after = str(fork.tines.keys())
			# print("Removing tine ({}--{}) id: {} from {} new  {}"
			# 	.format(self.label, child.label, child.id, before, after))
		except KeyError:
			pass




	# ============ Methods for fork-building =================

	def advance_charstring(self, suffix):
		# breakpoint()
		if len(suffix) == 1 and suffix in ['0', '1']:
			# advance by only one bit
			new_w = c.CharString(prev = self.w, new_bit = suffix)
			assert new_w.len == 1 + self.w.len

			if suffix == '1':
				self.adversarial_slots.append(new_w.len)
				self.num_adversarial_slots += 1
		else:
			s = self.w.str() + suffix
			new_w = c.CharString(s = s)		
			self.adversarial_slots = self.w.all_adversarial_slots()
			self.num_adversarial_slots = len(self.adversarial_slots)
			
		hd = self._honest_depths[self.w.len] # last value

		# self._honest_depths.append(hd)
		for i in range(len(suffix)):
			# update honest depths for new slots
			# 	the new values will be the last value
			self._honest_depths.append(hd)
			# make room for new slots
			self._nodes_by_slot.append([])
		

		# update w
		self._w = new_w

		# reserves will change; update critical tines
		self._find_critical_tines()		



# ============== Tine viability ==================

	# answers whether a tine of a certain length is viable at the onset of a given slot
	# the input should either be a tine, 
	#		in which case length and slot is resolved from the tine,
	#		or the tuple (slot, length), 
	#   in which case a tine is not required
	def is_viable_tine(self, tine, onset_slot = None):
		return self.is_viable_length(tine.len, onset_slot)

	def is_viable_length(self, length, onset_slot = None):
		if onset_slot is None:
			if self.w.len == 0:
				onset_slot = 1
			else:
				onset_slot = self.w.len

		if onset_slot <= 0:
			raise ValueError("is_viable_length(): 'Onset of slot: {}' is meaningless for w: {}".format(onset_slot, self.w.str()))			

		completed_slot = onset_slot - 1
		if completed_slot < 0 or completed_slot > self.w.len:
			raise IndexError("onset_slot: {} is incorrect for w.len: {}".format(self.w, self.w.len))

		# finally, viability test			
		# the length must be no shorter than slot's honest depth
		try:
			return length >= self._honest_depths[completed_slot]
		except IndexError:
			print("IndexError: completed_slot: {} while len(self._honest_depths) = {} w = {}"
				.format(completed_slot, len(self._honest_depths), self.w))
		# by this rule, the root is viable before any honest block is added


	#============ Extend a tine =======================


	def extend_tine(self, tine, labels):	
		labels = self.check_extension_labels(tine, labels)
		# now build the tine by adding a sequence of blocks
		orig_tine = tine
		old_tine = tine
		for label in labels:			
			new_tine = None
			if self.w.is_adversarial(label):
				new_tine = t.Tine(fork = self, label = label, parent = old_tine)
			elif self.okay_to_extend(old_tine, label):
				new_tine = t.Tine(fork = self, label = label, parent = old_tine)
				# update honest depths if an honest tine
				self._on_new_honest_tine(new_tine)
			else:
				raise ValueError("Not okay to extend")	

			# get ready to add the next block
			old_tine = new_tine

		# the final tine is here
		self.on_newly_extended_tine(new_tine = new_tine, old_tine = orig_tine)
		return new_tine	

	def check_extension_labels(self, tine, labels):
		if isinstance(labels, int):
			labels = [labels]
		# no duplicate labels
		if len(labels) != len(set(labels)):
			raise ValueError("Repeated labels: {}".format(labels))

		# labels must be an increasing list of integers
		# sorted_labels = self._bubblesort(labels)
		n = len(labels)
		for i in range(n - 1):
			if labels[i + 1] <= labels[i]:
				raise ValueError("Labels not sorted: {}".format(labels))

		# all labels must be later than tine's label
		if tine.label >= labels[0]:
			raise ValueError("Bad label: new block at {} must be later than parent's label {}".format(label, parent.label))

		# finally
		return labels


	def okay_to_extend(self, parent, label):
			# viability of honest tines
			# parent cannot be shorter than child's honest depth
			honest_block = self.w.is_honest(label)
			parent_viable = self.is_viable_tine(tine = parent, onset_slot = label)
			# extend if
			#	(i.)  not forcing viability; or
			#   (ii.) forcing viability, but adversarial block; or
			#   (iii.)forcing viability, honest block, and viable
			if self._force_viable and honest_block and not parent_viable:
				raise ValueError("Viability error: cannot extend a non-viable tine: {} reach: {} with an honest slot: {} in w: {}"
					.format(parent.path, parent.reach, label, self.w.str()))
			else:
				return True

	
	def _on_new_honest_tine(self, tine):
		# update current and future honest depths
		if tine.honest:
			for slot in range(tine.label, self.w.len + 1):
				self._honest_depths[slot] = tine.len
		else:
			raise ValueError("Not an honest tine")	

	def on_newly_extended_tine(self, new_tine, old_tine = None):

		# add to the list of tines
		# before = str(self.tines.keys())
		self.tines[new_tine.id] = new_tine

		# remove the orig tine from this list unless it is the root
		if not old_tine:
			old_tine = new_tine.parent

		if old_tine is not None and old_tine is not self.root:
			# not a tine (i.e., leaf node) anymore
			try:
				del self.tines[old_tine.id]
			except KeyError:
				# key does not exist
				pass
		# after = str(self.tines.keys())
		# print("Adding tine ({}--{}) id: {} to {} new  {}"
		# 	.format(new_tine.parent.label, new_tine.label, new_tine.id, before, after))

		# update the longest_tine if necessary
		# keep track of only viable tines
		new_viable_longest_tine = False
		new_tine_is_viable = self.is_viable_length(length = new_tine.len, onset_slot = self.w.len + 1)
		if new_tine_is_viable:
			if new_tine.len > self.longest_tine.len:
				# new longest tine
				new_viable_longest_tine = True
				# update the longest tine
				self._longest_tine = new_tine
				self._longest_tines = [new_tine]

			elif new_tine.len == self.longest_tine.len:
				self._longest_tines.append(new_tine)

		# update critical tines if necessary
		self._find_critical_tines()



	# ==================== Tine reach and critical tines ====================

	# return viable tines with maximal reach
	def honest_tines_with_largest_reach(self):
		# import priorityqueue
		# pq = priorityqueue.MaxPriorityQueue()

		# # recall: self.tines includes the root
		# for t in self.tines.values():
		# 	if t.reach >= 0: 
		# 		if not viable_only or t.is_viable():
		# 			pq.insert(t, t.reach )

		pq = self.pq_nodes_by_reach_decreasing(honest_only = True)

		# first tine
		tine = pq.pop()
		best_tines = [tine]
		# print("\nfirst best tine: {} reach: {}, length: {}, label: {}".format(tine, tine.reach, tine.len, tine.label))

		# are there other tines with the same reach?
		done = False
		# while (len(tines) >= 1) and not done:
		while (not pq.isempty()) and not done:
			tine = pq.pop()
			if tine.reach == best_tines[0].reach:
				# print("\nother best tine: {} reach: {}, length: {}, label: {}".format(tine, tine.reach, tine.len, tine.label))
				best_tines.append(tine)
			else:
				done = True

		return best_tines

	# critical tines does not have to be viable
	def _find_critical_tines(self, node = None):
		# self._critical_tines = [t for t in self.tines.values() if t.reach == 0 and self.is_viable_tine(t)]
		self._critical_tines = [t for t in self.tines.values() if t.reach == 0]

	def _find_critical_tines_old(self, node = None):
		if node is None:
			node = self.root
			self._critical_tines.clear()
		
		# now consider only leaves
		if node.isleaf:
			# leaf
			if node.reach == 0:
				self._critical_tines.append(node)
		else:
			# has children
			for child in node.children:
				self._find_critical_tines_old(child)

		# finally
		# special: the root is always extensible
		if (node == self.root) and node.reach == 0 and (not node in self._critical_tines):
			self._critical_tines.append(node)



	# keep only nodes with a non-negative reach
	def pq_nodes_by_reach_decreasing(self, honest_only = False):

		# insert this node at the priority queue keyed by reach (smallest first)
		import priorityqueue as q
		
		# This is a max-pririty queue
		# key = reach
		# Remember: negative reach = negative priority
		priority_negative = lambda item, priority: priority < 0
		pq = q.MaxPriorityQueue(exclude_item_if = priority_negative)

		# insert to pq only nodes with non-negative reach
		if not honest_only:
			[pq.insert(node, node.reach) for arr in self.nodes_by_slot for node in arr]
		else:
			[pq.insert(node, node.reach) for arr in self.nodes_by_slot for node in arr if node.honest]

		return pq


	# keep only nodes with a non-negative reach
	def pq_nodes_by_reach_increasing(self, honest_only = False):

		# insert this node at the priority queue keyed by reach (smallest first)
		import priorityqueue as q
		
		# This is a max-pririty queue
		# key = -reach
		# Remember: negative reach = positive priority
		priority_positive = lambda item, priority: priority > 0
		pq = q.MaxPriorityQueue(exclude_item_if = priority_positive)

		# insert to pq only nodes with non-negative reach
		if honest_only:
			[pq.insert(node, -node.reach) for arr in self._nodes_by_slot for node in arr if node.honest]
		else:
			[pq.insert(node, -node.reach) for arr in self._nodes_by_slot for node in arr]

		return pq

	#===================== Methods for display ====================

	def add_row_on_top(self, arr, row):
		new_matrix = [row]
		for line in arr:
			new_matrix.append(line)
		return new_matrix

	def _sort_rows_by_splitting_point(self, matrix, tine_paths, tines):
		import priorityqueue as q
		pq = q.MaxPriorityQueue()
		star_symbol = '*'

		for i in range(len(matrix)):
			row = matrix[i]
			path = tine_paths[i]
			tine = tines[i]

			if star_symbol in row:
				# earlier splits get higher priority
				priority = -row.index(star_symbol)
			else:
				# the reference tine; highest priority
				priority = -len(row)
			pq.insert((row, path, tine), priority)

		# now pop and add
		matrix, tine_paths, tines = self._alternately_add_rows_to_matrix(pq)
		return matrix, tine_paths, tines

	def encode_nodes(self):
		# reset all encodings
		[node.reset_encoding() for node in self.get_nodes()]

		# First, decorate all nodes on the longest tines
		# Then decorate all other nodes
		tines_and_types = [(self.longest_tines, True), (self.tines.values(), False)]
		for tines, on_longest_tine in tines_and_types:
			for tine in tines:
				node = tine
				while node and not node.is_encoding_on_longest_tine():
					# pre-calculate the block encodings along the longest tines
					node.calculate_and_set_encoding(on_longest_tine = on_longest_tine)
					# deal with the parent node
					node = node.parent


	# long tines in the middle, short tines on the fringe
	# assumes that node encodings are already computed
	def _tines_to_rows(self, 
		nodes = None, 
		show_paths = False,
		block_encoding = False, prune_slot_at = None,
		long_tine_in_the_middle = True, 
		include_root = False):
	
		import priorityqueue
		pq = priorityqueue.MaxPriorityQueue()

		n = self.w.len

		# if block_encoding:
		# 	# need to tell blocks if they are on the longest tine

		if nodes is None:
			# all tines
			nodes = self.tines.values()			

		for tine in nodes:
			if not include_root and tine == self.root:
				pass
			else:
				if not show_paths:
					path = ""
				else:
					if not prune_slot_at:
						path = tine.path
					else:
						path = tine.partial_path(prune_slot_at)

				longest_tine = (tine == self.longest_tine)
				row = tine.to_row(
					w_len = n, 
					block_encoding = block_encoding, 
					longest_tine = longest_tine, 
					prune_slot_at = prune_slot_at 
				)
				
				pq.insert((row, path, tine), tine.len)

		
		if long_tine_in_the_middle:
			# long tines in the middle, short tines on the fringe
			matrix, tine_paths, tines = self._alternately_add_rows_to_matrix(pq)

		else:
			matrix = []
			tine_paths = []
			tines = []

			while not pq.isempty():
				item = pq.pop()
				# row = item[0]
				# tine_path = item[1]
				row, tine_path, tine = item

				matrix.append(row)
				tine_paths.append(tine_path)
				tines.append(tine)

		return matrix, tine_paths, tines

	# expect: priority queue entries are (row, tine_path)
	def _alternately_add_rows_to_matrix(self, pq):
		matrix = []
		tine_paths = []
		tines = []

		top = True		
		while not pq.isempty():
			# item = pq.pop()
			# row = item[0]
			# tine_path = item[1]
			row, tine_path, tine = pq.pop()

			if top:
				matrix = self.add_row_on_top(matrix, row)
				tine_paths = self.add_row_on_top(tine_paths, tine_path)
				tines = self.add_row_on_top(tines, tine)
			else:
				matrix.append(row)
				tine_paths.append(tine_path)
				tines.append(tine)
			
			# change side
			# print('Not changing side in tines to rows')
			top = (not top)
		return matrix, tine_paths, tines

	def to_matrix(self, nodes = None, sort_by_splitting_point = False, show_tines = False, 
		block_encoding = False, deepest_node = None, prune_slot_at = None):
		long_tine_in_the_middle = not sort_by_splitting_point

		if block_encoding:
			# pre-calculate the block encodings along the longest tine
			self.encode_nodes()


		rows, tine_paths, tines = self._tines_to_rows(
			nodes = nodes, 
			show_paths = show_tines,
			block_encoding = block_encoding, prune_slot_at = prune_slot_at, 
			long_tine_in_the_middle = long_tine_in_the_middle)

		# [print(r) for r in rows]

		matrix = self._compact_matrix(rows, block_encoding = block_encoding)

		if sort_by_splitting_point:
			# need to sort rows by splitting point
			# need the matrix be compacted already
			# the longest tine need to be at the top
			matrix, tine_paths, tines = self._sort_rows_by_splitting_point(matrix, tine_paths, tines)
		return matrix, tine_paths, tines


	def _matrix_to_string(self, matrix, delim = ","):
		str = "\n".join([delim.join(row) for row in matrix] )
		return str

	# comma-separated entries; lines separated by new-line
	def __str__(self, 
		nodes = None, delim = ",", show_matrix = True, show_tines = False, 
		block_encoding = False, prune_slot_at = None,
		sort_by_splitting_point = False, verbose = False):

		matrix, tine_paths, tines = self.to_matrix(
			nodes = nodes, 
			show_tines = show_tines, 
			block_encoding = block_encoding, prune_slot_at = prune_slot_at, 
			sort_by_splitting_point = sort_by_splitting_point)

		str = ""
		if show_tines:
			lines = []
			for r in range(0, len(matrix)):
				row = ""
				if show_matrix:
					row = matrix[r]
				tine_path = tine_paths[r]
				lines.append(delim.join(row) + " tine: " + tine_path)
			str = "\n".join(lines)
		else:
			# str = "\n".join([ delim.join(row) for row in matrix] )
			str = self._matrix_to_string(matrix)
		return str


	def to_string(self, 
		nodes = None, delim = ",", show_matrix = True, show_tines = False, 
		sort_by_splitting_point = False, block_encoding = False, 
		prune_slot_at = None 
		):

		return self.__str__(
			nodes = nodes, delim = delim, show_tines = show_tines, 
			block_encoding = block_encoding, prune_slot_at = prune_slot_at, 
			show_matrix = show_matrix, sort_by_splitting_point = sort_by_splitting_point)


	def _add_star(self, row, col):
		# replace current block with *
		row[col] = "*"

		# delete all blocks to its left except the root column
		for c in range(0, col):
			if row[c] != "0":
				row[c] = "0"

		return row

	def _compact_matrix(self, matrix, block_encoding = False):
		num_rows = len(matrix)
		num_cols = self.w.len + 1 # one column extra for the root node
		
		honest_cells = ["3", "7"]
		adv_cells = ["1", "5"]

		# scan columns from right to left
		for col in range(num_cols - 1, -1, -1):
			slot = col
			is_slot_honest = self.w.is_honest(slot)
			if col == 0 or is_slot_honest:
				# the root column is treated as honest
				# are there multiple entries in this honest column?
				preivous_honest_block = False
				num_honest_cells = 0
				first_honest_cell_row_index = None
				some_honest_cell_on_the_longest_tine = False
				num_honest_cells_on_the_longest_tine = 0 # for the genesis slot

				# with this column at hand, scan rows from top to bottom
				row_index = -1
				for row in matrix:
					row_index += 1
					cell_value = row[col]
					this_honest_cell_on_the_longest_tine = False

					# is it an honest cell?
					if not block_encoding:
						is_honest_cell = (cell_value == "1")
					else:
						is_honest_cell = (cell_value in honest_cells)


					if is_honest_cell:
						if num_honest_cells == 0:
							first_honest_cell_row_index = row_index
						num_honest_cells += 1

						if block_encoding and cell_value == "7":
							# this honest cell is on the longest tine
							# in a given slot, multiple honest cells on the longest chain 
							# 	happens only for the root node
							multiple_honest_cells_on_the_longest_tine = \
								(num_honest_cells_on_the_longest_tine is not None) and \
								(num_honest_cells_on_the_longest_tine >= 1)

							# assert (col == 0 or multiple_honest_cells_on_the_longest_tine is False)

							this_honest_cell_on_the_longest_tine = True
							num_honest_cells_on_the_longest_tine += 1

						# we don't do anything on the first honest cell in this column
						if num_honest_cells >= 2:
							if not block_encoding:
								# always substitue non-leading honest cells
								row = self._add_star(row, col)
							else:
								if this_honest_cell_on_the_longest_tine and num_honest_cells_on_the_longest_tine == 1:
									# this honest cell is the first on the longest tine
									# we've already encountered an off-the-longest-chain honest cell
									# modify that row and keep the current row intact
									other_row = matrix[first_honest_cell_row_index] # this is the unchanged row
									matrix[first_honest_cell_row_index] = self._add_star(other_row, col)
								else:
									# substitue non-leading honest cells
									row = self._add_star(row, col)



							# # at least two honest blocks
							# # replace current block with *
							# row[col] = "*"

							# # delete all blocks to its left except the root column
							# for c in range(0, col):
							# 	if row[c] != "0":
							# 		row[c] = "0"


		return matrix


	def diagnostics(self, 
		tines = True, 
		nodes = False, 
		matrix = False, 
		critical_tines = False, 
		verbose = False,
		matrix_delim = ",",
		tines_with_matrix = False, 
		block_encoding = False,
		include_root = False):

		# compact display if possible
		if matrix and tines:
			tines_with_matrix = True
			# tines = False

		# print the reach of every node
		print("\n===== Fork on w = {} ({} bits) =====".format(self.w.str(), self.w._get_len()))
		# diagnostics of every node
		if nodes:
			tines = False
			print("----Node diagnostics----")
			[n.diagnostics(verbose) for arr in self.nodes_by_slot for n in arr]
					
		if tines:
			num_tines = len(self.tines)
			if not include_root:
				num_tines -= 1

			print("----Tines ({})----".format(num_tines))
			for t in self.tines.values():
				if t is not self.root or include_root:
					t.diagnostics(verbose)
			# touch_tine = lambda tine: tine.diagnostics(verbose)
			# self.root.visit_leaves(touch_tine)
			# if include_root:
			# 	self.root.diagnostics(verbose)
	
		if critical_tines:
			print("----Critical tines----")
			for tine in self._critical_tines:
				tine.diagnostics()
	
		if matrix:
			print("----Matrix----")

			num_chars = self.w.len + 1
			num_delims = num_chars - 1
			matrix_line = "-" * ( num_chars + num_delims) # one extra for the root

			w_line = "w=" + ",".join(self.w.str())
			print(w_line)
			print(matrix_line)
			print(self.__str__(delim = matrix_delim, show_tines = tines_with_matrix, block_encoding = block_encoding))
			print(matrix_line)



	#==================== Methods for a trimmed fork ==================

	def trim_tine_tips_old(self):
		remove_leaf = lambda leaf: leaf.parent.children.remove(leaf)		
		if len(self.root.children) >= 1:
			self.root.visit_leaves(remove_leaf)

	def trim_tine_tips(self, tines = None):
		if not tines:
			tines = list(self.tines.values()).copy()

		new_tines = []
		for t in tines:
			if t is not self.root:
				t.parent.remove_child(child = t, fork = self)
				# did the parent become a new tine?
				if t.parent.isleaf:
					new_tines.append(t.parent)
		return new_tines


	# input: a list of tines {t}
	# output: a list of nodes {p} where
	#  t is the only child of p
	def parents_at_height(self, nodes, height, verbose = False):
		new_nodes = {}		

		for t in nodes:
			# print("Examining node: {}".format(t.id))
			if hasattr(t, 'no_trim'):
				# it stays in the next level
				new_nodes[t.id] = t
			elif t is not self.root:
				# all tines have the same height
				p = t.parent
				if hasattr(p, 'no_trim'):
					# p.no_trim = True but t.no_trim is None
					# p does not go into the next level
					continue
				# print("Examining parent node: {} at height: {} with {} children".format(p.id, p.height, p.num_children()))
				# this is crucial: check the height
				elif p.height == height: 
					if p.id not in new_nodes:
						# yes: the parent is in the next level set
						#   and it's not been seen yet

						# print("Adding node {} at height {}".format(p.id, p.height))					
						new_nodes[p.id] = p

		
		# return (new_nodes.values(), deepest_node)
		return new_nodes.values()


	# returns an array of size max_delete_blocks + 1
	# index k = 0, 1, ..., max_delete_blocks
	# value at index k is 
	#	the matrix representation after trimming the last k blocks
	#	from every tine
	def trim_tines_and_get_matrix(self, 
		max_delete_blocks =  0, 
		show_matrix = True, 
		show_tines = False,
		sort_by_splitting_point = False,
		block_encoding = True,
		prune_slot_at = None,
		verbose = False		):
		hard_trim = False

		# print("Begin trim_tines_and_get_matrix")
		# self.diagnostics(matrix = False, tines = True)
		
		result = []		
		
		# self.update_tines()

		no_more_cut = False
		if verbose:
			for lt in self.longest_tines:
				print("\tlongest tine: {}".format(lt.path))

		valid_prune = \
			prune_slot_at is not None and \
			prune_slot_at >= 1 and \
			prune_slot_at <= self.w.len


		# the longest-tine must not be cut
		# mark all nodes on the longest tine(s) as non-trimmable
		for lt in self.longest_tines:
			node = lt
			while node:
				setattr(node, 'no_trim', True)
				if verbose:
					print("node slot: {} no_trim: {}".format(node.label, node.no_trim))
				node = node.parent

		nodes = self.tines.values()


		# check no_trim
		# [print("no_trim: {}".format(n.label)) for arr in self._nodes_by_slot for n in arr if hasattr(n, 'no_trim')]


		if verbose:
			print("Valid prune: {} prune_slot_at: {}".format(valid_prune, prune_slot_at))

		if block_encoding:
			# pre-calculate the block encodings along the longest tine
			for lt in self._longest_tines:
				lt.to_row(self.w.len, block_encoding = True, longest_tine = True)

		if not hard_trim:
			self.update_heights()
			height = 0

		for k in range(0, max_delete_blocks + 1):
			# print("\n---- k = {} ----".format(k))
			# self.diagnostics(matrix = False, tines = True)
			if k >= 1 and not no_more_cut:

				# if len(self.root.children) >= 1:
				# 	self.root.visit_leaves(remove_leaf)
				# self.trim_tine_tips_old()


				if hard_trim:
					self.trim_tine_tips()
					if self.root.num_children() == 0:
						no_more_cut = True
				else:
					if verbose:
						print("Level set at height: {} nodes: {} ".format(height, [n.label for n in nodes]))

					height = height + 1
					nodes = self.parents_at_height(nodes = nodes, height = height, verbose = verbose)
					if not nodes:
						no_more_cut = True
		
			snapshot = self.to_string(
				nodes = nodes,
				show_tines = show_tines, 
				show_matrix = show_matrix, 
				sort_by_splitting_point = sort_by_splitting_point,
				block_encoding = block_encoding, 
				prune_slot_at = prune_slot_at 
				)
			result.append(snapshot)

		# finally
		# unmark all nodes that were marked as non-trimmable
		to_do = [self.root]
		while to_do:
			node = to_do.pop(0)
			del node.no_trim
			[to_do.append(c) for c in node.children if hasattr(c, 'no_trim')]

		return result

	def delete_rightmost_nonempty(self, row, last_scanned = None, EMPTY = '0', SPLIT = '*'):
		if not last_scanned:
			last_scanned = len(row)
		right_end = last_scanned - 1

		# skip trailing EMPTY cells 
		while right_end >= 0 and right_end <= len(row) and row[right_end] == EMPTY:
			right_end -= 1
		# now either right_end == 0 or row[right_end] is non-empty
		# if this cell is non-empty, delete it
		# but don't delete blocks on the longest tines (i.e., value >= 5)
		if right_end >= 0 and right_end < len(row) and row[right_end] != EMPTY:
			# delete this block
			row[right_end] = EMPTY
		# finally
		return row, right_end


	def trim_tines_and_get_matrix_stable(self, 
		max_delete_blocks =  0, 
		show_matrix = True, 
		show_tines = False,
		sort_by_splitting_point = False,
		verbose = False		):

		# a snapshot is a matrix of string symbols
		snapshots = []
		n = self.w.len

		# all leaf nodes
		nodes = self.tines.values()

		# take the first snapshot
		# it encodes the fork
		matrix, tine_paths, tines_in_matrix = self.to_matrix(
			nodes = nodes, 
			show_tines = show_tines, 
			block_encoding = True,
			sort_by_splitting_point = sort_by_splitting_point)

		# which rows belong to the longest tines?
		rows_for_longest_tines = []
		for i in range(len(tines_in_matrix)):
			t = tines_in_matrix[i]
			if t in self.longest_tines:
				rows_for_longest_tines.append(i)

		# print("tines_in_matrix = {}".format(tines_in_matrix))
		if verbose:
			print("rows_for_longest_tines = {}".format(rows_for_longest_tines))


		snapshots.append(matrix)

		prev_matrix = matrix
		num_rows = len(matrix)
		# initially, use the last column for every row
		last_col = self.w.len
		last_scanned_in_row = [last_col + 1] * num_rows


		for k in range(1, max_delete_blocks + 1):
			# use previous snapshot
			matrix = [row.copy() for row in matrix]

			# at each row, starting from the right, delete the last non-zero entry
			for r in range(num_rows):
				# if this row belongs to a longest tine, don't change it
				if r in rows_for_longest_tines:
					continue

				# start scanning from the last non-zero column in this row
				row, right_end = self.delete_rightmost_nonempty(row = matrix[r], last_scanned = last_scanned_in_row[r])
				# save this position
				matrix[r] = row
				last_scanned_in_row[r] = right_end

			snapshots.append(matrix)


		# finally
		result = [self._matrix_to_string(m) for m in snapshots]
		return result


	def _prune_charstring(self, at_slot):
		# update global information
		self._num_slots_seen = at_slot - 1

		# finally, set charstring
		self._w = self.w.prefix(at_slot - 1)

		# update per-slot information
		self._nodes_by_slot = self._nodes_by_slot[0 : at_slot]
		self._honest_depths = self._honest_depths[0 : at_slot]

		# both w and honest_depths must be updated before checking tine viability

		# update critical tines
		self._find_critical_tines()

		# update longest tines
		self.update_longest_tines()

    # update the list of all adversarial slots
		self.adversarial_slots = self.w.all_adversarial_slots()
		self.num_adversarial_slots = len(self.adversarial_slots)


	# delete all blocks from sltos >= at_slot
	def prune_slot(self, at_slot):
		# delete blocks
		if at_slot > self.w.len:
			raise ValueError("at_slot > w.len")
		elif at_slot < 0:
			raise ValueError("at_slot < 0")
		else:
			to_do = [self.root]
			while to_do:
				node = to_do.pop(0)
				children = [c for c in node.children] # make a copy
				for c in children:
					if c.label < at_slot:
						to_do.append(c)
					else:
						# remove
						node.remove_child(child = c, fork = self)

			# delete_if = lambda c :  c.label >= at_slot
			# self.root.prune_subtree(cond = delete_if, fork = self)

		# update charstring and related info
		self._prune_charstring(at_slot)

		# update tines
		self.update_tines()


	#============ Methods for maintaining tines =================

	def visit_leaves(self, func):
		node_is_leaf = lambda x : x.num_children() == 0
		self.visit_nodes(cond = node_is_leaf, func = func)


	def visit_nodes(self, func, cond = None, root = None):
		if root is None:
			root = self.root
		
		to_do = [root]

		while to_do:
			node = to_do.pop(0)
			if cond is None or cond(node):
				func(node)
			else:
				[to_do.append(c) for c in node.children]
					

	def update_tines(self):
		# update tine list
		self.tines = {self.root.id : self.root}
		add_tine = lambda t : self.tines.update({t.id : t})
		self.visit_leaves(add_tine)
		# longest tines
		self.update_longest_tines()


	def update_longest_tines(self):
		tines, length = self.find_longest_tines()
		self._longest_tines = tines
		self._longest_tine = tines[0]


	# returns all longest viable tines
	def find_longest_tines(self):
		if not self.tines:
			# no tines
			raise ValueError("No tines in fork")

		import priorityqueue as q
		pq = q.MaxPriorityQueue()

		# insert tines into priority queue
		for t in self.tines.values():
			if t.is_viable():
				pq.insert(t, t.depth)
			# print("tine {} len: {}".format(t.path, t.len))

		# touch_tine = lambda t : pq.insert(t, t.depth) 
		# self.root.visit_leaves(touch_tine)

		if pq.isempty():
			print("tines: ")
			for t in self.tines.values():
				t.diagnostics(verbose = True)
			raise ValueError("Not a single viable tine")

		max_length = pq.peek()[0].depth
		tines = []
		while (not pq.isempty()) and pq.peek()[0].depth == max_length:
			tines.append(pq.pop())

		# finally
		return (tines, max_length)

	def update_heights(self):
		tines = self.tines.values()
		for t in tines:
			t.update_height_upstream()



#============ Methods for fork-prefix =================

	# returns nodes upto and including SLOT
	def get_nodes_upto_slot(self, slot = None):
		if not slot or slot > self.w.len:
			slot = self.w.len
		return [n for slot in range(slot + 1) for n in self.nodes_by_slot[slot] ]

	def get_nodes(self):
		return self.get_nodes_upto_slot()


	# returns nodes that are located before SLOT but with no children before SLOT
	def get_nodes_in_forefront_before_slot(self, slot, nodes = None):
		if not nodes:
			nodes = self.get_nodes_upto_slot(slot - 1)
		in_forefront = lambda n : n.label < slot and (n.isleaf or min([c.label for c in n.children]) >= slot)
		forefront = [n for n in nodes if in_forefront(n)]
		return forefront

	# returns balanced, tine1, tine2
	# The two witness tines must have the same (maximal) length and distinct slots
	def is_prefix_balanced_before_slot(self, slot, forefront = None, suffix_start = None):
		# slot must be honest
		if not self.w.is_honest(slot):
			raise ValueError("Slot {} is not honest".format(slot))
		if slot <= 1:
			raise ValueError("Slot {} is too small".format(slot))

		# which suffix should the tines be disjoint over?
		if not suffix_start:
			suffix_start = 1

		if not forefront:
			forefront = self.get_nodes_in_forefront_before_slot(slot)
		num_nodes = len(forefront)
		# longest tine in the forefront
		max_length = max([n.len for n in forefront])

		for one in range(num_nodes - 1):			
			t1 = forefront[one]
			for two in range(1, num_nodes):
				t2 = forefront[two]

				if 	t1.is_disjoint(t2, suffix_start = suffix_start) and \
						t1.len == t2.len and \
						t1.len == max_length: 
					# print("balanced fork witness: {}, {}".format(t1.slots(), t2.slots()) )
					return True, t1, t2

		return False, None, None

	# returns balanced, t1, t2, honest_slot
	# If true, t1 and t2 are the witness tines at the onset of HONEST_SLOT
	def has_forkable_prefix(self, start_slot = None):
		if start_slot is None or start_slot < 2:
			start_slot = 2

		if self.w.len >= 2:

			# start checking from slot 2
			for slot in range(start_slot, self.w.len + 1):

				if self.w.is_honest(slot):
					balanced, t1, t2 = self.is_prefix_balanced_before_slot(slot)
					if balanced:
						return True, t1, t2, slot

		return False, None, None, None

	# w must end in an honest slot
	# the fork-prefix upto the penultimate slot must contain two tines:
	#		both of maximal length, distinct slots
	# returns balanced, t1, t2
	# If true, t1 and t2 are the witness tines
	def is_forkable(self):
		if self.w.is_honest(self.w.len):
			balanced, t1, t2, slot = self.is_prefix_balanced_before_slot(self.w.len)
			return balanced, t1, t2
		else:
			raise ValueError("CharString w: {} does not end in an honest slot".format(w))



################# End Fork class ###################


	#======================== Other methods ==================

def _bubblesort(self, arr, increasing = True):
	n = len(arr)
	if n <= 1:
		return arr
	else:
		sorted_arr = []
		for i in range(n):
			sorted_arr.append(arr[i])
		for i in range(n - 1):
			for j in range(i + 1, n):
				shall_swap = sorted_arr[i] > sorted_arr[j] if increasing else sorted_arr[i] < sorted_arr[j]
				if shall_swap:
					temp = sorted_arr[i]
					sorted_arr[i] = sorted_arr[j]
					sorted_arr[j] = temp
	return sorted_arr

# SORTED_BY is one of "slot", "label", "len", "depth", "reach", "height"
def sorted_nodes(nodes, by = None, reverse = False):
	if nodes is None or len(nodes) == 1:
		return nodes

	if by is None or by == "slot" or by == "label":
		key = lambda n: n.label
	elif by == "len" or by == "depth":
		key = lambda n : n.len
	elif by == "reach":
		key = lambda n : n.reach
	elif by == "height":
		key = lambda n : n.height
	else:
		raise ValueError("Unknown SORT_BY: {}".format(by))

	return sorted(nodes, key = key, reverse = reverse)















class KeyValuePair:
	def __init__(self, key, value):
		self.key = key
		self.value = value

	def __lt__(left, other):
		return left.key < other.key
	def __str__(self):
		return str(self.key)

	# def __le__(this, other):
	# 	return this if this.key <= other.key else other



