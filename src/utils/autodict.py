# Autodict class
# Create new autodict if accessing undefined key
# support dot access syntax (mydict.test == mydict['test'])
class autodict(dict):
    def __getitem__(self, name):
        if not name in self:
            dict.__setitem__(self, name, autodict())
        return dict.__getitem__(self, name)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return self[name]

    def __setattr__(self, name, val):
        if name in self.__dict__:
            self.__dict__[name] = val
        else:
            self[name] = val


# Visit function for autodict like structure
# Call the given function on each leaf passing all keys in arguments
def visit(obj, func, args=[]):
    if isinstance(obj, dict):
        for key, val in obj.items():
            visit(val, func, args + [key])
    else:
        func(*(args + [obj]))
