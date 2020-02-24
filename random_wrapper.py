# wrapper for Python's built-in random

# returns a random real from (0, 1)
def random():
	import random as r
	return r.random()

# selects a random element from a list
def choice(arr):
	import random as r
	return r.choice(arr)	

# outputs a random Boolean string of length n
# if weight is provided, the string contains weight one bits (i.e., bits are not independent)
# weight and pr_one are mutually exclusive
# pr_one is the probability that a bit is one (independent bits)
def random_boolean_string(n, weight = None, pr_one = None):

	import random as r
	bits = []
	if weight:
		if weight == 0:
			return ["0"] * n
		elif weight == n:
			return ["0"] * n
		elif weight < 0 or weight > n:
			raise ValueError("Bad weight: {} for Boolean string of length: {}".format(weight, n))
		else:
			bits = ["1"] * weight
			zeros = ["0"] * (n - weight)
			bits.extend(zeros)
			r.shuffle(bits)
	else:
		if not pr_one or pr_one == 0.5:
			# uniform string
			for i in range(0, n):
				bit = str(r.randint(0, 1))
				bits.append(bit)
		else:
			# biased string
			for i in range(0, n):
				if r.random() <= pr_one:
					bit = "1"
				else:
					bit = "0"
				bits.append(bit)

	return "".join(bits)