
from enum import Enum, unique

@unique
class	Encoding(Enum):
		ABSENT = 0
		PRESENT = 1
		HONEST = 2
		ON_LONGEST_TINE = 4
	

class Node:
	'''Node of the tree'''
	def __init__(self, parent = None):
		self._depth = 0
		self._height = 0
		# id
		self.id = None
		self._num_children = 0

		if parent is None:
			# I am a root node
			self._parent = None
		else:
			self.parent = parent
			self.parent.add_child(self)
		self._children = [] # no children now

		self.visited_lca = None

		# important for it to be None
		self.encoding = None

	def _get_parent(self):
		return self._parent
	
	def _set_parent(self, value):
		if isinstance(value, Node):
			self._parent = value
			self._depth = self.parent.depth + 1
		else:
			raise TypeError("Parent must be a Node.")

	parent = property(_get_parent, _set_parent)

	
	def _get_depth(self):
		return self._depth

	depth = property(_get_depth)

	
	def num_children(self):
		return self._num_children


	def _get_height(self):
		return self._height

	# don't call it lightly
	def _set_height(self, h):
		self._height = h


	height = property(_get_height)

	def _get_children(self):
		return self._children

	children = property(_get_children)

	def add_child(self, child):
		if isinstance(child, Node):
			self.children.append(child)
			self._num_children += 1
		else:
			raise ValueError("Attempting to add an invalid child")

	def prune_subtree(self, cond, fork = None):
		if not self.isleaf:
			unfortunate_ones = [c for c in self.children if cond(c)]
			# print("unfortunate_ones: {}".format([t.id for t in unfortunate_ones]))
			for c in unfortunate_ones: 
				self.remove_child(child = c, fork = fork)
				
			for c in self.children:
				c.prune_subtree(cond = cond, fork = fork)


	# removal is non-recursive
	def remove_child(self, child, cond = None, fork = None):
		if isinstance(child, Node):
			if child in self.children:
				if (cond is None) or cond(child):
					
					cpath = child.path

					self.children.remove(child)
					self._num_children -= 1
					if fork:
						fork.on_node_deleted(child, parent = self)
					print("Removed {}".format(cpath))
			else:
				print("\n\n#### PANIC ####")
				if fork:
					fork.diagnostics(matrix = False, tines = True)
				print("Attempting to remove {}".format(child.path))
				print("Problem node: {} children: {}".format(self.path, [c.label for c in self.children]))
				raise ValueError("Child not in children")
		else:
			raise ValueError("Child not a node")


	def _isleaf(self):
		# return len(self.children) == 0
		return self._num_children == 0
    
	isleaf = property(_isleaf)


	# def visit_subtree(self, func):
	# 	func(self)
	# 	if not self.isleaf:
	# 		arr = list(self.children)
	# 		for child in arr:
	# 			child.visit_subtree(func)
	
	# def visit_leaves(self, func):
	# 	if self.isleaf:
	# 		func(self)
	# 	else:
	# 		arr = list(self.children)
	# 		for child in arr:
	# 			child.visit_leaves(func)


	# ============= Methods for height ===================

	# propagate height upstream
	def update_height_upstream(self, removal = False):
		# print("In update_height_upstream for node: {}".format(self.id))
		if self.isleaf:
			# leaf node
			if self._height is not 0:
				self._height = 0

			# print("Leaf node: {}".format(self.id))
			p = self.parent
			# child = self
		else:
			# internal node
			# print("Internal node: {}".format(self.id))
			p = self

		while p is not None:
			new_parent_height = p.calculate_height()
			# print("Node: {} current height: {}".format(p.id, p.height))
			# print("Node: {} proposed height: {}".format(p.id, new_parent_height))

			if removal:
				need_update = (new_parent_height < p.height)
			else:
				need_update = (new_parent_height > p.height)
			if need_update:
				# print("Update node: {} height to: {}".format(p.id, new_parent_height))
				# update
				p._set_height(new_parent_height)
				# prepare for next iteration
				# child = p
				p = p.parent
			else:
				# no change in height
				break

	# height of this node is 1 + max_{child} child.height
	def calculate_height(self):
		if self.isleaf:
			self.height = 0
		else:
			child_heights = [c.height for c in self.children]
			return 1 + max(child_heights)


	# ============ Methods for encoding ===========

	def is_encoding_on_longest_tine(self):
		return (self.encoding is not None) and \
			(int(self.encoding) & Encoding.ON_LONGEST_TINE.value) is not 0

	def calculate_and_set_encoding(self, on_longest_tine = False):
		value = Encoding.PRESENT.value  # Present bit
		if self.label == 0 or self.honest:
			value += Encoding.HONEST.value # Honest bit
		if on_longest_tine:
			value += Encoding.ON_LONGEST_TINE.value # The G bit
		# finally
		s_value = str(value)

		# remember encoding as it does not change
		self.encoding = value
		return value

	def reset_encoding(self):
		self.encoding = None


