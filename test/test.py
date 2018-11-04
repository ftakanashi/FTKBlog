# -*- coding:utf-8 -*-

f = open('mat.txt','r')

line = f.readline()
while line:
    if not line.strip():
        line = f.readline()
        continue
    print 'INSERT INTO ftkuser_slogan("content","author") VALUES("%s","%s");' % tuple(line.split('--'))
    line = f.readline()

f.close()