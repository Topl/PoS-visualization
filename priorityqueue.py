# PriorityQueue implementation
# Source: https://brilliant.org/wiki/priority-queues/

# Maintains the queue as an array of tuples
# Query time is O(n) where n is the size of the pq
class MaxPriorityQueue:
    def __init__(self, exclude_item_if = None):
        self.qlist = []
        self.exclude_item_if = exclude_item_if
        self.n = 0

    def insert(self, item, priority = 0):
        # shall we exclude this item?
        if self.exclude_item_if is not None:
            if self.exclude_item_if(item, priority):
                return self.qlist

        if len(self.qlist) == 0:
            self.n += 1
            return self.qlist.append((item, priority))
        
        # for x in range(0, len(self.qlist)-1):
        for x in range(len(self.qlist)):
            if self.qlist[x][1] < priority:
            	# store as (item, priority) tuple
                self.n += 1
                return self.qlist.insert(x, (item, priority))
        self.n += 1
        return self.qlist.append((item, priority))

    def pop(self, with_priority = False):
        if self.isempty():
            raise IndexError('Queue empty')
        # return self.qlist.pop(0)
        pair = self.qlist.pop(0)
        self.n -= 1
        
        if with_priority:
            return pair
        else:
            return pair[0] # return only item, not priority
    
    # returns the pair (item, priority)
    def peek(self):
        return self.qlist[0]

    # returns the priority of the first entry
    def peek_priority(self):
        item, priority = self.qlist[0]
        return priority

    # returns the item of the first entry
    def peek_item(self):
        item, priority = self.qlist[0]
        return item


    def isempty(self):
    	# return len(self.qlist) == 0
        return self.n == 0

    def __repr__(self):
        return str(self.qlist)

    def items(self):
        return [pair[0] for pair in self.qlist]

    def size(self):
        return self.n
