
# import charstring as c
import node as n



class Tine(n.Node):
	'''Class Tine'''

	def __init__(self, fork = None, label = 0, parent = None):
		# Set leaf node
		# super().__init__(parent)
		n.Node.__init__(self, parent)
		# Set fork
		if fork is None:
			raise ValueError("Invalid fork given to Tine constructor.")

		self.fork = fork
		# Set label and bit	
		self._label = 0 # label of an empty tine is zero
		# self._bit = None
		self._bit = 0 # initially
		if self.fork.w.len >= 1:
			# Non-empty fork
			self.label = label
			if label >= 1:
				self.bit = ord(fork.w.at(label)) - ord('0')

		# notify fork that you are done		
		self.fork.on_new_node(self)
		self._path = None		

	
	def _make_path(self):
		if self.label == 0:
			self._path = "(*)" # special marker for the root
		else:
			if self.honest:
				my_label = "(" + str(self.label) + ")"
			else:
				my_label = "[" + str(self.label) + "]"
			
			if self.parent is None:
				self._path = my_label
			else:
				middle = ""
				for skipping_slot in range(self.parent.label + 1, self.label):
					sep = "---" if skipping_slot < 10 else "----"
					middle += sep
				self._path = self.parent.path
				self._path += middle
				self._path += my_label

	def _get_bit(self):
		return self._bit
    
	def _set_bit(self, value):
		if (value == 0) or (value == 1):
			self._bit = value
		else:
			raise TypeError("Bit must be an integer, either 0 or 1.")
    
	bit = property(_get_bit, _set_bit)

	def _get_label(self):
		return self._label

	# value is in 0, ..., w.len() where 0 means an empty tine
	def _set_label(self, value):
		if isinstance(value, int) and (value >= 0) and (value <= self.fork.w.len):
			self._label = value
		else:
			raise TypeError("Label must be an integer >= 0 and <= w.len()")
    
	label = property(_get_label, _set_label)
            
	def _get_len(self):
		return self.depth

	len = property(_get_len)

	def _get_path(self):
		if not self._path:
			self._make_path()
		return self._path
    
	path = property(_get_path)

	def partial_path(self, prune_slot_at = None):
		if not prune_slot_at or self.label < prune_slot_at:
			return self.path
		else:
			# show an ancestor's path
			n = self
			while n.label >= prune_slot_at:
				n = n.parent
			return n.path
	

	def _get_honest(self):
		return self.bit == 0
    
	honest = property(_get_honest)
	

	def _get_adversarial(self):
		return self.bit == 1
    
	adversarial = property(_get_adversarial)


	def _get_reserve(self):
		# return self.fork.w.reserve(self.label, self.fork.num_slots_seen)
		return self.fork.w.reserve(self.label)
    
	reserve = property(_get_reserve)

	def _get_reach(self):
		r = self.reserve - self.gap
		return r
    
	reach = property(_get_reach)

	def _get_gap(self):
		return self.fork.longest_tine.len - self.len
    
	gap = property(_get_gap)

	def lca(self, other_tine):
		if self == other_tine:
			return self
		
		lca_node = None
		if self.len <= other_tine.len:
			shorter_tine = self
			longer_tine = other_tine
		else:
			shorter_tine = other_tine
			longer_tine	 = self

		original_shorter_tine = shorter_tine
		done = False

		while not done:
			# mark the current node at the short tine
			# setattr(shorter_tine, 'visited_lca', True)			
			shorter_tine.visited_lca = True

			# move up along both tines
			if not (shorter_tine.parent is None):
				shorter_tine = shorter_tine.parent	
			if not (longer_tine.parent is None):
				longer_tine = longer_tine.parent
				# did the longer tine hit the shorter one?
				visit_together = longer_tine is shorter_tine
				
				# visit_after = hasattr(longer_tine, "visited_lca") and (longer_tine.visited_lca is True)
				visit_after = longer_tine.visited_lca is True
				
				if visit_together or visit_after:
					lca_node = longer_tine
					done = True
			else:
				# reached the root of the fork along the longer tine
				lca_node = self.fork.root
				done = True
		# clean up: remove all the "visited_lca" fields
		done = False
		node = original_shorter_tine
		# while (not (node is None)) and hasattr(node, "visited_lca"):
		while (not (node is None)) and node.visited_lca is not None:
			# del node.visited_lca
			node.visited_lca = None
			node = node.parent
		# finally
		return lca_node

	# Once calculated for a node, its encoding does not change
	def to_row(self, w_len, block_encoding = True, longest_tine = False, prune_slot_at = None):
		row = ["0"] * (w_len + 1)
		node = self
		no_pruning = False
		while node is not None:
			if prune_slot_at is None or no_pruning or node.label < prune_slot_at:
				if not no_pruning:
					# no need to prune from now
					no_pruning = True

				if block_encoding:
					if not node.encoding:
						value = node.calculate_and_set_encoding(on_longest_tine = longest_tine)
					else:
						value = node.encoding
				else:
					if node.label == 0 or node.honest:
						# root or honest
						value = 1
					else:
						value = 2

				row[node.label] = str(value)

			# recurse
			node = node.parent
		return row

	def __str__(self):
		return ",".join(self.to_row(self.label))

	def diagnostics(self, verbose = False):
		print("tine {}".format(self.path))
		if verbose:
			print("\treserve: {} gap: {} reach: {} len: {} viable: {}".format(self.reserve, self.gap, self.reach, self.len, self.is_viable()))		
	


	def is_viable(self, onset_slot = None):
		return self.fork.is_viable_length(self.len, onset_slot)


	def slots(self):
		slots = []
		node = self
		while node:
			slots.insert(0, node.label)
			node = node.parent
		return slots

	# returns true if lca(t1, t2) is located before suffix_start
	def is_disjoint(self, other_tine, suffix_start = None):
		if not suffix_start:
			suffix_start = 1
		return self.lca(other_tine).label < suffix_start
