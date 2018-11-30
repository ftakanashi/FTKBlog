# -*- coding:utf-8 -*-

class Test(object):
    def __init__(self):
        pass

    def test(self):
        pass

class TTest(Test):
    def __init__(self):
        super(TTest,self).__init__()

    def test(self,a):
        print a

if __name__ == '__main__':
    t = TTest()
    t.test('aaa')