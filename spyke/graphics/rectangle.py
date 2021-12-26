class RectangleF:
    def __init__(self, *args):
        self.x = 0.0
        self.y = 0.0
        self.width = 0.0
        self.height = 0.0

        self.__ParseArgs(args)
    
    def __ParseArgs(self, args):
        if len(args) == 0:
            return
        elif len(args) == 4:
            self.x = args[0]
            self.y = args[1]
            self.width = args[2]
            self.height = args[3]
        elif len(args) == 1:
            if isinstance(args[0], tuple) or isinstance(args[0], list):
                args = args[0]
                self.x = args[0]
                self.y = args[1]
                self.width = args[2]
                self.height = args[3]
            
            if isinstance(args[0], RectangleF):
                args = args[0]

                self.x = args.x
                self.y = args.y
                self.width = args.width
                self.height = args.height
            
    def __ne__(self, other):
        return not self.__eq__(other)
            
    def __eq__(self, other):
        return all(self.x == other.x, self.y == other.y, self.width == other.width, self.height == other.height)
    
    @property
    def left(self):
        return self.x
    
    @property
    def right(self):
        return self.x + self.width
    
    @property
    def bottom(self):
        return self.y + self.height
    
    @property
    def top(self):
        return self.y
    
    @classmethod
    def One(cls):
        return cls(0.0, 0.0, 1.0, 1.0)