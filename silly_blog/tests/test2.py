#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.helpers import locked_cached_property


class Test:

    @locked_cached_property
    def test(self):
        print(123)
        return 22


if __name__ == '__main__':
    t = Test()
    t.test
    t.test
