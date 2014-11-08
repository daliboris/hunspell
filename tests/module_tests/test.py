# -*- coding:utf-8 -*-


import common



class Test(object):

    def __init__(self):
        self.errors = 0


    def report(self):
        if self.errors == 0:
            common.output(u"  ✓ All tests passed.\n")
        elif self.errors == 1:
            common.output(u"  ✗ 1 test failed.\n")
        else:
            common.output(u"  ✗ {} tests failed.\n".format(self.errors))


    def run(self, spellCheckerManager):
        raise Exception("Abstract method")