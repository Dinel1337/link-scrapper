class MyRange:
    def __init__(self, start, stop=None, step=1):
        if stop is None:
            start, stop = 0, start
        self.start = start
        self.stop = stop
        self.step = step
    
    def __iter__(self):
        self.current = self.start
        return self
    
    def __next__(self):
        if (self.step > 0 and self.current >= self.stop) or \
           (self.step < 0 and self.current <= self.stop):
            raise StopIteration
        value = self.current
        self.current += self.step
        return value

# Использование
for i in MyRange(5, 10, 2):
    print(i)  # 0 1 2 3 4