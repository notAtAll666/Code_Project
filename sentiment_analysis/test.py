# encoding=utf-8
import jieba

fin = open('original/view.csv', 'r')
fo = open('data/car_corpus.txt', 'w')

for line in fin:
    arr = line.strip().split('\t')
    if len(arr) == 2:
        fo.write(arr[1] + ' nz' + '\n')

