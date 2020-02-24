
import fork as f

########### Unitity functions ###############
def tine_with_earliest_slot(tines, verbose = False):
	if verbose:
		print("Judging earliest slot among tines: {}".format([t.slots() for t in tines]))
	slot = float("inf")
	tine = None
	for t in tines:
		if t.label < slot:
			tine = t
			slot = t.label
	return tine

def tine_with_smallest_reach(tines, verbose = False):
	if verbose:
		print("Judging smallest reach among tines: {}".format([(t.slots(), t.reach) for t in tines]))
	r = float("inf")
	tine = None
	for t in tines:
		tine_reach = t.reach
		if tine_reach < r:
			tine = t
			r = tine_reach
	return tine

# returns candidate_tine, which_ref_tine, split_slot
def tine_with_oldest_split(tines, ref_tines, verbose = False):
	oldest_split = float("inf")
	candidate_tine = None
	which_ref_tine = None

	if len(tines) == 1:
		if verbose:
			print("Only one candidate tine; extend anyway")
			return tines[0], ref_tines[0], None

	for t_largest_reach in ref_tines:			
		# for critical_tine in self.fork.critical_tines:
		for tine in tines:
			# critical tines do not have to be viable
			# assert self.fork.is_viable_tine(critical_tine)

			if tine == t_largest_reach:
				# a tine does not split from itself
				continue

			lca = tine.lca(t_largest_reach)
			# lca = self.fork.lca(critical_tine, t_largest_reach)
			split = lca.label

			if split < oldest_split:
				candidate_tine = tine
				oldest_split = split
				which_ref_tine = t_largest_reach

	return candidate_tine, which_ref_tine, oldest_split



#########################################################


class Adversary:
	def __init__(
		self, 
		w = "", 
		verbose = False, 
		double_charstring = False
		):

		self.verbose = verbose
		self.double_charstring = double_charstring
		n = len(w)
		# print("Adversary initial w: " + w)

		if double_charstring:
			self.prune_slot_at = n + 1
			zeros = "0" * n
			w += zeros

		self._fork = f.Fork("", force_viable = True)
		
		# if str not empty, build the fork
		# print("Adversary using w: " + w)
		slot = 0
		if w != "":
			for c in w:
				slot = slot + 1
				self._build(suffix = c)

		# if double_charstring:
		# 	print("pruning")
		# 	self.fork.prune_slot(n + 1)


	def _get_fork(self):
		return self._fork

	fork = property(_get_fork)
	    
	def on_adversarial_slot(self, label):
		# do nothing
		pass
	    
	def on_honest_slot(self, label):
		# do nothing
		pass

	# returns the fork
	def on_slot(self, label):
		if self.fork.w.is_adversarial(label):
			self.on_adversarial_slot(label)
		else:
			self.on_honest_slot(label)

	# takes action on a series (suffeix) of slots
	def _play(self, start_slot = 1):
		new_slots = range(start_slot, self.fork.w.len + 1)
		# print("About to play new slots: {}".format([s for s in new_slots]))
		for slot in new_slots:
			self.on_slot(slot)

	# Builds on top of an existing fork
	def _build(self, suffix, no_action = False):
		new_slot = self.fork.w.len + 1 # before advancing
		self.fork.advance_charstring(suffix)

		if not no_action:
			self._play(new_slot)
		# return self.fork

	def extension_candidates(self):
		return []

	def extension_slots_for_longest_tine(self, tine):
		return []

	def extension_slots_for_critical_tine(self, tines_to_extend):
		return []

	# # extend using minimal number of adversarial blocks
	# #	that is, use tine.gap adversarial blocks but no more
	# # return the extended tines in an array
	# def add_honest_block(self, tine, label):
	# 	# if label == 19:
	# 	# 	breakpoint()

	# 	slots_per_extension = []
	# 	extended_tines = []
	# 	# extend the tine by adding adversarial blocks
	# 	# we are guaranteed to have tine.gap adversarial slots
	# 	# get the first tine.gap adversarial slots after tine.label

	# 	# print("tine.gap: {}".format(tine.gap))

	# 	if tine.gap == 0:
	# 		# longest tine
	# 		slots_per_extension = self.extension_slots_for_longest_tine(tine)
	# 	else:
	# 		slots_per_extension = self.extension_slots_for_critical_tine(tine)

	# 	# complete the extension(s)
	# 	for slots in slots_per_extension:
	# 		# finally, add the honest block at the end
	# 		slots.append(label)
	# 		# now create the new tine
	# 		new_tine = self.fork.extend_tine(tine, slots)
	# 		extended_tines.append(new_tine)
		
	# 	return extended_tines


#########################################################



class OnlineAdversary(Adversary):
	'''	The online adversary.
		Constructor parameters:
		w: (optional, default empty string)
			the characteristic string to build a fork on.
		splitting_probability: (optional, default zero) 
			the probability with which an adversarial slot ``splits''
			all existing tines, i.e., tines that end before that slot
			A large splitting probability will produce a voluminous fork.
			Note that the adversary in the Linear Consistency paper has this parameter zero, 
			i.e., he never splits existing tines on adversarial slots. 


		Suppose you run the code
			a = OnlineAdversary(w = "0101")

		The fork built by the adversary can be accessed as a.fork, and can be 
		viewed as
			a.fork.diagnostics()
		You can ask to see specific diagnosits info, such as:
			a.fork.diagnostics(matrix = True, verbose = True, tines = True)
		See Fork.diagnostics() for details.

		To build on top of an existing fork, you can feed a suffix to the adversary
		as follows:
			a.build(suffix = "110")
		As you have guessed, the constructor repeatedly calls build() to build 
		on w.

	'''

	def __init__(
		self, 
		w = "", 
		verbose = False,
		double_charstring = False,
		early_diverging_critical_only = True
		):
		# super(OnlineAdversary, self).__init__(w)
		# super().__init__(w)

		# consider only critical tines for choosing early-diverging tines for extension
		self.early_diverging_critical_only = early_diverging_critical_only
		self.pq_tines = None



		Adversary.__init__(self, w = w, verbose = verbose, double_charstring = double_charstring)
		

	# all tines with zero or positive reach
	# returns the sequence (tines_of_interest, has_critical_tine)
	def tines_of_interest(self):
		# Min priority queue of nodes by reach
		# That is, nodes in the order of reach 0, 1, 2, ...
		# if self.verbose:
		# 	print("_nodes_by_slot: {}".format([node.label for arr in self.fork.nodes_by_slot for node in arr]))

		has_critical_tine = False
		tines_of_interest = []

		self.pq_tines = self.fork.pq_nodes_by_reach_increasing(honest_only = True)
		if self.verbose:			
			print("pq_tines: {}".format([node.label for node in self.pq_tines.items()]))

		if self.pq_tines.isempty():
			return tines_of_interest, has_critical_tine

		# print("pq.peek: tine at slot: {}".format(pq.peek_item().label))

		# smallest_reach = self.pq_tines.peek_item().reach

		# are there any critical tines?
		has_critical_tine = not self.pq_tines.isempty() and self.pq_tines.peek_priority() == 0
		if has_critical_tine:
			if self.verbose:
				print("Has critical honest tines")			
			# extract the critical tines
			one_more_critical_tine = True
			while one_more_critical_tine:
				tines_of_interest.append(self.pq_tines.pop())
				one_more_critical_tine = not self.pq_tines.isempty() and self.pq_tines.peek_priority() == 0
			# no more critical tines
			if self.verbose:
				print("critical honest tines: {}".format([t.path for t in tines_of_interest]))
		else:
			# no critical tine to begin with
			if self.verbose:
				print("No critical honest tines")
				# print("early_diverging_critical_only: {}".format(self.early_diverging_critical_only))
				# print("Branching expects: ^^^^^ False")

			# can we consider non-critical tines?
			if self.early_diverging_critical_only:
				# no
				return [], has_critical_tine
			else:
				# yes
				# all tines with positive reach
				tines_of_interest = self.pq_tines.items()
				if self.verbose:
					print("non-critical honest tines: {}".format([t.path for t in tines_of_interest]))

		return tines_of_interest, has_critical_tine



	# simply select the first item in the list
	def arbtirary_candidate_tine(self, tines_of_interest, has_critical_tine):
		if tines_of_interest:
			if self.verbose:
				print("Selecting the first candidate tine: {}".format(tines_of_interest[0].path))
			return tines_of_interest[0]
		else:
			return None

	def break_tie_without_ref_tines(self, tines_of_interest, has_critical_tine):
		# Don't know how to break tie
		# It doesn't matter
		# give up, cannot break tie
		if has_critical_tine: 
			# we have to break tie
			return self.arbtirary_candidate_tine(tines_of_interest, has_critical_tine)
		else:
			if self.verbose:
				print("Non critical tines; cannot break tie; give=ing up")
			return None

	def break_tie_early_diverging_tines(self, tines_of_interest, ref_tines, has_critical_tine):
		candidate_tine = None
		if self.fork.root in ref_tines:
			# cannot break tie via oldest split
			if self.verbose:
				print("Root is a reference tine; cannot break tie by oldest split")
			return self.break_tie_without_ref_tines(tines_of_interest, has_critical_tine)
		else:
			# break tie via oldest split
			candidate_tine, ref_tine, split_slot = tine_with_oldest_split(tines_of_interest, ref_tines, self.verbose)
			if self.verbose:
				print("\nfound early-diverging tine: {} ref tine: {} split at slot: {}"\
					.format(candidate_tine.path, ref_tine.path, split_slot))
		return candidate_tine


	def reference_tines(self):
		ref_tines = self.fork.honest_tines_with_largest_reach()

		if self.verbose:
			print("reference tines: {}".format([t.path for t in ref_tines]))

		return ref_tines

	# critical tines with earliest split from the tine with the largest reach
	#	if some critical tine exists
	# returns the list candidate_tines
	# the pq now contains all non-critical positive-reach tines
	def early_diverging_tines(self):
		candidate_tine = None
		tines_of_interest, has_critical_tine = self.tines_of_interest()
		if self.verbose:
			print("has_critical_tine: {}".format(has_critical_tine))

		num_tines_of_interest = len(tines_of_interest)
		
		if num_tines_of_interest == 1:
			# only one candidate tine; extend it anyway
			return tines_of_interest
		elif num_tines_of_interest == 0 and self.early_diverging_critical_only:
			# no critical tines, bummer
			return []
		else:
			# we have to break tie among multiple tines of interest
			ref_tines = self.reference_tines()
			candidate_tine = self.break_tie_early_diverging_tines(tines_of_interest, ref_tines, has_critical_tine)

			if candidate_tine:
				return [candidate_tine]
			else:
				return []


	def adversarial_slots_for_extending_tine(self, tine):
		slots_per_extension = []
		g = tine.gap
		slots = []
		res = None
		try:
			reserve_slots = self.fork.w.adversarial_slots_after(slot = tine.label)
			slots = reserve_slots[0 : tine.gap] # first slots
		except Exception as e:
			print(e)
			print("IndexError: w: {} len: {} slot: {} reserve: {}"
				.format(self.fork.w, self.fork.w.len, tine.label, res))

		# only one extension
		slots_per_extension.append(slots) 
		return slots_per_extension

	# the first extension gets the honest block
	# other extensions end in adversarial blocks
	def extend_tine_with_adv_slots(self, tine, adv_slots_per_extension, honest_slot):
		extended_tines = []
		added_honest_block = False
		for slots_this_extension in adv_slots_per_extension:
			# add the honest block to exactly one extension
			if not added_honest_block:
				slots_this_extension.append(honest_slot)
				added_honest_block = True
			
			# print("Extend slot {} using slots {}".format(tine.label, slots_this_extension))

			# now create the new tine
			try:
				new_tine = self.fork.extend_tine(tine, slots_this_extension)
			except Exception as e:
				print("Failed to extend tine: {} with slots: {}".format(tine.path, slots_this_extension))
				raise e
			extended_tines.append(new_tine)
		return extended_tines

	def extend_tines(self, tines, honest_slot):
		extended_tines = []
		prev_longest = self.fork.longest_tine.len

		for tine in tines:
			adv_slots_per_extension = self.adversarial_slots_for_extending_tine(tine)			
			new_tines = self.extend_tine_with_adv_slots(tine, adv_slots_per_extension, honest_slot)

			for t in new_tines:
				assert t.len == prev_longest + 1

			extended_tines.extend(new_tines)
		return extended_tines

	def on_honest_slot(self, label):			
		tines_to_extend = []
		new_tines = []


		if self.verbose and self.double_charstring and label == self.prune_slot_at:
			print("\n>>>>>>>> Onset of first slot to be pruned: {} =========".format(label))
			self.fork.diagnostics(tines = True, matrix = False, verbose = False, include_root = True)

		if self.verbose:
			print("\n>>>>>>>> Onset of honest slot {} =========".format(label))
			self.fork.diagnostics(nodes = True, matrix = False, verbose = True, include_root = True)
			print("\nLongest tine: ")
			self.fork.longest_tine.diagnostics(verbose = True)

		# need to place an honest node
		# are there any critical tines?
		tines_to_extend = self.early_diverging_tines()

		# if tines_to_extend:
		# 	if self.verbose:
		# 		print("\nAt slot {} found early-diverging tine: {}".format(label, tines_to_extend[0].path))

		if not tines_to_extend:
			# extend a longest tine
			# print("######## Extending a non-critical tine #########")
			
			# tines_to_extend = self.candidate_non_critical_tines()			
			tines_to_extend = [self.fork.longest_tine]

			if self.verbose:
				print("\nExtending longest tine: {} at slot {}".format(tines_to_extend[0].path, label))

		new_tines = self.extend_tines(tines_to_extend, label)
		if self.verbose:
			for t in new_tines:
				print("Added new tine: {}".format(t.path))
			# self.fork.diagnostics(matrix = False, nodes = True, verbose = True, include_root = True)

		# return the newly extended tines
		return new_tines





#########################################################

''' The ``branching'' online adversary
	He differs from the adversary from the paper in that 
	he exploits his legal options 
'''
class BranchingAdversary(OnlineAdversary):
	def __init__(	self, 
								w = "", verbose = False, double_charstring = False,
								# root_ref_tine_okay = True, 
								break_tie = None):
		# super(RevealingOnlineAdversary, self).__init__(w)
		# super().__init__(w)
		
		# self.root_ref_tine_okay = True
		# if verbose:
		# 	print("Constructor: break_tie: {}".format(break_tie))
		self.break_tie = break_tie

		OnlineAdversary.__init__(self, 
			w = w, 
			verbose = verbose,
			double_charstring = double_charstring,
			early_diverging_critical_only = False 
			)


	def break_tie_without_ref_tines(self, tines_of_interest, has_critical_tine):
		# always break tie
		return self.arbtirary_candidate_tine(tines_of_interest, has_critical_tine)

	# cannot break tie by oldest split
	# use some other rule
	def arbtirary_candidate_tine(self, tines_of_interest, has_critical_tine):
		candidate_tine = None		
		if tines_of_interest:
			if self.verbose:
				print("break_tie: {}".format(self.break_tie))

			if self.break_tie == "slot":
				candidate_tine = tine_with_earliest_slot(tines_of_interest, self.verbose)
				if self.verbose:
					print("Selecting a tine with earliest slot: {}".format(candidate_tine.path))
			elif self.break_tie == "reach":
				# recall that tines returned by tines_of_interest() are sorted by reach, increasing
				# # cannot break tine among critical tines
				candidate_tine = tines_of_interest[0]
				if self.verbose:
					print("Selecting a tine with smallest reach: {}".format(candidate_tine.path))
			else:
				# if any unknown tie-breaking is used
				# resort to the detaulf tie-breaking mechanism
				if self.verbose:
					print("use super().arbtirary_candidate_tine")
				candidate_tine = super().arbtirary_candidate_tine(tines_of_interest, has_critical_tine)

		return candidate_tine


	# # this method specializes OnlineAdversary.reference_tine()
	# # for the case when root is a reference tine
	# def reference_tines(self):
	# 	ref_tines = super().reference_tines()

	# 	if self.verbose:
	# 		print("inside BranchingAdversary.reference_tines()")

	# 	# first, we have to sort out reference tines
	# 	if ref_tines == [self.fork.root]:
	# 		if not self.root_ref_tine_okay:
	# 			# give up
	# 			if self.verbose:
	# 				print("Root is the only reference tine; give up")
	# 			return None

	# 	# ref_tines still may contain the root
	# 	if len(ref_tines) >= 2 and self.root_ref_tine_okay is False:
	# 		# multiple reference tines
	# 		# and we are instructed to ignore the root
	# 		ref_tines.remove(self.fork.root)
	# 		if self.verbose:
	# 			print("Not considering the root as a reference tine")

	# 	# ref_tines may or may contain root
	# 	return ref_tines

