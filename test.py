# -*- coding: utf-8 -*-

class A(object):
    def __init__(self, name):
        self.name = name

    def __gt__(self, other):
        return "%s > %s" % (self.name, str(other))

    def __repr__(self):
        return self.name


print(A("X") > A("Y"))
