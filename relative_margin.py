

# # recursive definition of reach
# # last_slot = 1, 2, ...
# def reach(w, slot = None):
# 	if w == "" or w is None:
# 		return 0

# 	if slot is None:
# 		slot = len(w)
	
# 	if slot == 0:
# 		return 0

# 	prev_reach =  reach(w, slot - 1)
# 	bit = w[slot - 1]
# 	if bit == "1":
# 		return prev_reach + 1

# 	# honest bit
# 	if prev_reach == 0:
# 		return 0
# 	else:
# 		return prev_reach - 1

# # recursive definition of margin
# def margin(w, x_len = 0, slot = None):
# 	if w == "" or w is None:
# 		return 0
	
# 	if slot is None:
# 		slot = len(w)
# 	if slot == x_len:
# 		return reach(w, x_len)

# 	prev_reach =  	reach(w, slot - 1)
# 	prev_margin =  	margin(w, slot - 1)
# 	bit = w[slot - 1]
# 	if bit == "1":
# 		return prev_margin + 1
# 	else:
# 		# honest bit
# 		if prev_margin == 0 and prev_reach > 0:
# 			return 0
# 		else:
# 			return prev_margin - 1


def reach_and_margin(w, x_len = None, reach = None):
	if w is None or w == "":
		return [], []
	if x_len is None or x_len < 0:
		x_len = 0

	n = len(w) 
	if reach is None:
		reach = [0] * (n + 1) 			# plus one for the genesis slot
		for i in range(n + 1):
			# calc reach
			if i == 0:
				reach[i] = 0 # the base case
			else:
				bit = w[i - 1]
				if bit == "1":
					reach[i] = reach[i-1] + 1
				else:
					if reach[i-1] == 0:
						reach[i] = 0
					else:
						reach[i] = reach[i-1] - 1

	assert len(reach) == (n+1)
	assert x_len <= n
	y_len = n - x_len
	margin = [0] * (y_len + 1)	# plus one for the base case (empty y)
	for i in range(x_len, n + 1):
		bit = w[i - 1]
		# calc relative margin
		j = i - x_len
		if j == 0:
			margin[j] = reach[x_len] # the base case
		else:
			if bit == "1":
				margin[j] = margin[j-1] + 1
			else:
				if margin[j-1] == 0 and reach[i - 1] > 0:
					margin[j] = 0
				else:
					margin[j] = margin[j-1] - 1

	return reach, margin


# the returned array includes the value at the starting position
def partial_sum_min(w):
	if w is None or w == "":
		return [], []

	n = len(w)
	psum = [0] * (n+1)
	pmin = [0] * (n+1)

	# initial values
	for i in range(n):
		if w[i] == "1":
			move = 1
		else:
			move = -1
		psum[i+1] = psum[i] + move		
		pmin[i+1] = min(pmin[i], psum[i+1])

	return psum, pmin

def left_catalan_slots(w):
	if w is None or w == "":
		return []

	lcat = []
	n = len(w)
	psum, pmin = partial_sum_min(w)
	for i in range(n):
		slot = i + 1
		if w[i] == "0" and psum[slot] == pmin[slot] and pmin[slot] < pmin[slot - 1]:
			lcat.append(slot)

	return lcat



def right_catalan_slots(w):
	if w is None or w == "":
		return []

	rcat = []
	n = len(w)
	psum, pmin = partial_sum_min(w)
	r_psum, r_pmin = partial_sum_min("".join(reversed(w)))
	# print("w: {}\nr_w: {}".format(w, w[::-1]))
	# print("psum:   {}\nr_psum: {}".format(psum, r_psum))
	# print("pmin:   {}\nr_pmin: {}".format(pmin, r_pmin))

	for i in range(n):
		slot = i + 1
		r_slot = n + 1 - slot
		# r_slot = slot
		if w[i] == "0" and r_psum[r_slot] == r_pmin[r_slot] and r_pmin[r_slot] < r_pmin[r_slot - 1]:
			rcat.append(slot)

	return rcat


def catalan_slots(w):
	if w is None or w == "":
		return []
	lcat = left_catalan_slots(w)
	rcat = right_catalan_slots(w)
	cat = set(lcat).intersection(rcat)
	return sorted(list(cat))



