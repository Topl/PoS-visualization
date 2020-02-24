
# entry point
import adversary as a

def build_fork(w, split_prob = 0.03, show_tines = False):
	adv = a.FluffyAdversary(w, split_prob)
	sort_by_splitting_point = True
	return adv.fork.to_string(",", show_tines, sort_by_splitting_point)	
