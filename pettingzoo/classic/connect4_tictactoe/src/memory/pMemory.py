from memory.sumTree import SumTree
import random, threading

class PMemory:   # stored as ( s, a, r, s_ ) in SumTree

    def __init__(self, capacity):
        self.lock = threading.Lock()

        self.e = 0.01
        self.a = 0.6
        self.tree = SumTree(capacity)
        self.cnt = 0

    def _getPriority(self, error):
        return (error + self.e) ** self.a

    def add(self, error, sample):
#        print('acquiring lock under add')

        with self.lock:
#            print('lock acquired under add')

            p = self._getPriority(error)
            self.tree.add(p, sample) 
            self.cnt += 1
        
#        print('lock released under add')

    def sample(self, n):
#        print('acquiring lock under sample')
        self.lock.acquire()
#        print('lock acquired under sample')
        
        n = min(n, self.cnt)
        if n == 0: return []
        
        batch = []
        segment = self.tree.total() / n

        for i in range(n):
            a = segment * i
            b = segment * (i + 1)

            s = random.uniform(a, b)
            (idx, p, data) = self.tree.get(s)
            batch.append( (idx, data) )

        return batch

    def update(self, idx, error):
        p = self._getPriority(error)
        self.tree.update(idx, p)
        
    def releaseLock(self):
        self.lock.release()
#        print('lock released under releaseLock')
