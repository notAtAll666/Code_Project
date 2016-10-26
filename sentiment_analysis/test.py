# encoding=utf-8
import jieba
import re
jieba.load_userdict('data/car_corpus.txt')
jieba.suggest_freq(('宝马', '车'), True)


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
seg_list = jieba.cut('说底盘，人家博越是沃尔沃调教，高大上吧。')
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
        view = view.replace('轿车'.decode('utf-8'), '')
        view = view.replace('汽车'.decode('utf-8'), '')
        view = view.replace('车'.decode('utf-8'), '')
        l.append(view)
        if view not in view_list:
            view_list.append(view)
    else:
        l.append(word)
    i += 1
    for v_view in view_list:
        for v_view1 in view_list:
            if v_view != v_view1:
                if v_view in v_view1:
                    view_list.remove(v_view)
                    break
print '/'.join(l)
print '/'.join(view_list)
