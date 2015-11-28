from longinttable import LongIntTable

class DiceInfo(object):
    def __init__(self, num, size):
        if isinstance(size, int):
            self._dic = dict((val, 1) for val in range(1,size+1))
            self._size = size
            self._num = num
            self._weight = None
        else:
            self._dic = self._make_dic(size)
            temp_size = self._dic.keys()
            temp_size.sort()
            self._size = temp_size[-1]
            self._num = num
            self._weight = sum(self._dic.values())
            
    def _make_dic(self, lst):
        if isinstance(lst, dict):
            return lst
        if isinstance(lst[0], int):
            out = {}
            for val in lst:
                out[val] = out.get(val, 0) + 1
            return out
        else:
            return dict((val, freq) for val, freq in lst)
    def get_num(self):
        return self._num
    def get_size(self):
        return self._size
    def get_dic(self):
        return self._dic        
    def get_weight(self):
        return self._weight
    def weight_info(self):
        print self
        if self._weight == None:
            print '    No weights\n'
        else:
            
            for val, freq in self._dic.items():
                print ('    a roll of %s has a weight of %s' % (val, freq))
            
    def add_num(self, num):
        self._num += num
    def __lt__(self, other):
        if self.get_size() != other.get_size():
            if self.get_size() < other.get_size():
                return True
            else:
                return False
        else:
            if self.get_weight() < other.get_weight():
                return True
            else:
                return False
    def __eq__(self, other):
        if self.get_dic() == other.get_dic():
            return True
        else:
            return False
    def __str__(self):
        
        out = '%sD%s' % (self._num, self._size)
        if self._weight == None:
            return out
        else:
            return out + ' W: %s' % (self._weight)
            
class DiceTable(LongIntTable):
    def __init__(self, dic = {0:1}, dice_list = []):
        LongIntTable.__init__(self, dic)
        self._dice_list = dice_list
        self._last_die = None
        
    def update_list(self, new_dice_info):
        done = False
        for dice_info in self._dice_list:
            if new_dice_info == dice_info:
                dice_info.add_num(new_dice_info.get_num())
                done = True
                break
        if not done:
            self._dice_list.append(new_dice_info)
        self._dice_list.sort()
        self._last_die = new_dice_info.get_dic()
    def get_list(self):
        return self._dice_list
    def get_last(self):
        return self._last_die
    def weights_info(self):
        for dice_info in self._dice_list:
            dice_info.weight_info()
    def __str__(self):
        out_str = ''
        for dice_info in self._dice_list:
            out_str = out_str + str(dice_info) + '\n'
        return out_str.rstrip('\n')

def add_dice(table, num = 1, size = 'last'):
    if size == 'last':
        size = table.get_last()
    dice_to_add = DiceInfo(num, size)
    table.update_list(dice_to_add)
    table.add(num, dice_to_add.get_dic())