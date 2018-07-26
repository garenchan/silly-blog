#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools


class Test:

    def test(self, a):
        print(a)


t = Test()
orig = t.test

def replace(orig, e):
    #print(self)
    print(orig)
    print(e)

t.test(123)
t.test = functools.partial(replace, t.test)
print(t.test)
t.test(123)