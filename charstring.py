
# import array

class CharString:
    '''Characteristic string
    We can build it from scratch, or 
    we can build a new characterstic string on top of another one using a new bit
    '''
    def __init__(self, s = None, prev = None, new_bit = None):
        self.prev = prev
        self.new_bit = new_bit


        self._adversarial_slots = [] # initially empty; compute on demand     
        self.num_adversarial_slots = 0

        if prev is not None and isinstance(prev, CharString):
            if new_bit in ['0', '1']:
                self._w = prev._w + new_bit
                self._len = prev._len + 1
                self._valid_flag = True
                self._validity_checked = True

                self._adversarial_slots = prev._adversarial_slots
                self.num_adversarial_slots = prev.num_adversarial_slots
                if new_bit == '1':
                    self.num_adversarial_slots += 1
                    self._adversarial_slots.append(self.len)

            else:
                raise ValueError("Invalid w = " + self._w + new_bit)
        else:
            self._w = s
            self._len = len(self._w)
            self._valid_flag = False
            self._validity_checked = False
    
        if not self.valid():
            raise ValueError("Invalid w = " + self._w)

        self._reserves = []
        self._precompute_reserve()

    def _get_w(self):
        return self._w
    
    w = property(_get_w)
    

    def _get_len(self):
        return self._len
    len = property(_get_len)

    def valid(self):
        if self._validity_checked:
            return self._valid_flag
        else:
            return self.calc_valid()

    # costly
    def calc_valid(self):
        if self._w is None:
            # empty
            self._valid_flag = True
        else:
            self._valid_flag = True
            for c in self.w:
                if (c != '0') and (c != '1'):
                    self._valid_flag = False
                    break
        self._validity_checked = True
        return self._valid_flag

    def at(self, index):
        if index == 0:
            return "*" # bit at the root node
        elif index >= 1 and index <= self.len:
            return self.w[index - 1]
        else:
            raise IndexError('Invalid index {}; w: {} has length {}'.format(index, self, self.len))

    def is_honest(self, index):
        return index == 0 or self.at(index) == "0"

    def is_adversarial(self, index):
        return self.at(index) == "1"

    # index 0 means the reserve of w
    def reserve(self, slot):
        invalid_or_empty = (not self._valid_flag) or (self._len == 0)
        bad_slot = slot < 0 or slot > self.len
        if invalid_or_empty or bad_slot:
            return 0
        return self._reserves[slot]

    def str(self):
        return self.w
    def __str__(self):
        return self.w

    # reserve(slot): # of ones AFTER slot
    def _precompute_reserve(self):
        # the reserve does not change if the new_bit is 0
        n = self._len
        if self.prev is not None:
            if self.new_bit is '0':
                self._reserves = self.prev._reserves
                self._reserves.append(0)
            else:
                # new bit is one
                # add one to every element
                self._reserves = [(1 + r) for r in self.prev._reserves]
                # the last element
                self._reserves.append(0)
                # now discard the previous charstring
                del self.prev

        else:
            # self._reserves = []
            # for pos in range(n + 1): # n + 1 items
            #     self._reserves.append(0)

            self._reserves = [0] * (n + 1)

            # self._reserves = [0] * (n+1)
            # self._reserves = array.array('I', (0 for i in range(0, n + 1)))

            # if self.valid() and n >= 1:
            if n >= 1:
                res = 0
                for pos in range(n - 1 , -1, -1):
                    c = self.at(pos + 1)
                    if (c == '1'):
                        res += 1
                    self._reserves[pos] = res

        self.num_adversarial_slots = self._reserves[0]

    def adversarial_slot_after(self, current_slot):
        slot = current_slot + 1
        while self.is_honest(slot):
            slot += 1            
        # now slot is adversarial
        return slot

    # What are the reserve slots?
    def adversarial_slots_after(self, slot = None, num_slots = None):
        # if slot >= self.len:
        #     return []
        
        slots = []

        if slot is None:
            raise ValueError("Slot is None")
        # check index validity
        self.at(slot)

        res = self.reserve(slot)

        if num_slots is None:
            num_slots = res
        if num_slots < 0 or num_slots > res:
            raise ValueError("Reserve {} but requested {} slots".format(res, num_slots))

        remaining = num_slots # reserve is non-negative
        while remaining >= 1:
            slot = self.adversarial_slot_after(slot)
            slots.append(slot)
            remaining -= 1
        return slots

    # returns a CharString
    def prefix(self, length):
        return CharString(self._w[0 : length])

    def all_adversarial_slots(self):
        if self._adversarial_slots == []:
            all_slots = range(1, self.len + 1)
            for slot in all_slots:
                if self.is_adversarial(slot):
                    self._adversarial_slots.append(slot)
            
        return self._adversarial_slots