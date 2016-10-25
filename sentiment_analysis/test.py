# encoding=utf-8
import jieba
import re
jieba.load_userdict('data/car_corpus.txt')


def get_car_str():  # 读取汽车品牌数据，存储为ls并返回
    fin = open('data/car_list.txt', 'r')
    ls = '$'
    for line in fin:
        ls += line.strip() + '$'
    return ls.lower().decode('utf-8')


def has_same_pre(s):
    return '$' + s.lower() in car_str


def is_in(s):
    return '$' + s.lower() + '$' in car_str

car_str = get_car_str()
seg_list = jieba.cut('【易手好车】经典Polo求带走~')
word_list = []
for word in seg_list:
    word_list.append(word)
l = []
view_list = []
i = 0
while i < len(word_list):
    word = word_list[i]
    view = ''
    while has_same_pre(word):
        if is_in(word):
            view = word
        if i == len(word_list) - 1:
            break
        if has_same_pre(word + word_list[i+1]):
            word = word + word_list[i+1]
            i += 1
        else:
            break

    if view != '':
        l.append(view)
        if view not in view_list:
            view_list.append(view)
    else:
        l.append(word)
    i += 1
print '/'.join(l)
print '/'.join(view_list)
