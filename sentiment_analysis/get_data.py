# encoding=utf-8

import jieba
from sklearn.externals import joblib


def get_train_label():  # 读取训练集标签数据，存储为{id:{view:label}}形式的label_dic
    fin = open('original/label.csv', 'r')
    train_label_dic = {}
    for line in fin:
        arr = line.strip().split('\t')
        if arr[0] in train_label_dic:
            train_label_dic[arr[0]][arr[1]] = 0 if arr[2] == 'neg' else 2 if arr[2] == 'pos' else 1
        else:
            label = 0 if arr[2] == 'neg' else 2 if arr[2] == 'pos' else 1
            train_label_dic[arr[0]] = {arr[1]: label}
    joblib.dump(train_label_dic, 'data/oid_label.' + 'train')
    fin.close()


def get_car_list():  # 读取汽车品牌数据，存储为ls并返回
    fin = open('data/car_list.txt', 'r')
    ls = []
    for line in fin:
        ls.append(line.strip().decode('utf-8'))
    return ls


def get_car_corpus():  # 获取汽车语料库，存储为car_corpus.txt文件
    fin = open('original/view.csv', 'r')
    fout = open('data/car_corpus.txt', 'w')
    for line in fin:
        arr = line.strip().split('\t')
        fout.write(arr[1] + '\n')


def get_original_doc(name):  # 获取原始文档数据，存储为dic并返回，utf-8编码
    fin = open('original/' + name, 'r')
    dic = {}
    for line in fin:
        arr = line.strip().split('\t')
        dic[arr[0]] = arr[1].strip()
    return dic


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


def get_view_and_word(l):  # 从句子中找出视角并返回视角list和词list
    word_list = []
    view_list = []
    i = 0
    while i < len(l):
        word = l[i]
        view = ''
        while has_same_pre(word):
            if is_in(word):
                view = word
            if i == len(l) - 1:
                break
            if has_same_pre(word + l[i + 1]):
                word = word + l[i + 1]
                i += 1
            else:
                break
        if view != '':
            word_list.append(view)
            if view not in view_list:
                view_list.append(view)
        else:
            word_list.append(word)
        i += 1
    return view_list, word_list


def get_prase_doc(name):  # 获取解析后文档数据，存储为oid_doc文件
    original_dic = get_original_doc(name)
    prase_dic = {}
    for sentence_id in original_dic.keys():
        sentence = original_dic[sentence_id]
        seg_list = jieba.cut(sentence)
        l = []
        for word in seg_list:
            l.append(word)
        view_list, word_list = get_view_and_word(l)
        temp_dic = {}
        if len(view_list) == 1:
            view = view_list[0]
            l = []
            for s in word_list:
                if s != view:
                    l.append(s)
            temp_dic = {view: l}
        elif len(view_list) > 1:
            for view in view_list:
                temp_dic[view] = []
            temp_list = []
            cur_view = view_list[0]
            flag = 0
            for word in word_list:
                if word in view_list:
                    if word == cur_view:
                        flag = 1
                    else:
                        flag += 1
                    if flag == 2:
                        if len(temp_list) != 0:
                            temp_dic[cur_view] += temp_list
                            temp_list = []
                    cur_view = word
                elif word == u'，' or word == u'。':
                    temp_list.append(word)
                    if len(temp_list) != 0:
                        temp_dic[cur_view] += temp_list
                    temp_list = []
                    flag = 0
                else:
                    temp_list.append(word)
        prase_dic[sentence_id] = temp_dic
    if name == 'train.csv':
        joblib.dump(prase_dic, 'data/oid_doc.' + 'train')
        fo = open('data\prase_train_doc.txt', 'w')
    elif name == 'test.csv':
        joblib.dump(prase_dic, 'data/oid_doc.' + 'test')
        fo = open('data\prase_test_doc.txt', 'w')
    for sentence_id in prase_dic.keys():
        temp = prase_dic[sentence_id]
        if len(temp) != 0:
            fo.write('\n')
            fo.write(sentence_id)
            fo.write('\n')
            for view in temp.keys():
                str1 = view.encode('utf-8')
                str2 = ' '.join(temp[view]).encode('utf-8')
                fo.write(str1)
                fo.write('\n')
                fo.write(str2)
                fo.write('\n')

# get_car_corpus()
car_str = get_car_str()
car_list = get_car_list()
jieba.load_userdict('data/car_corpus.txt')
get_train_label()
get_prase_doc('train.csv')
get_prase_doc('test.csv')

doc_dic = get_original_doc('train.csv')
dic = {}
dic1 = joblib.load('data/oid_doc.train')
dic2 = joblib.load('data/oid_label.train')

# i = 0
# for key in dic2:
#     for view in dic2[key]:
#         i += 1
#         view = view.decode('utf-8')
#         if view in dic.keys():
#             dic[view][0] += 1
#         else:
#             dic[view] = [1, 0]
# j = 0
# k = 0
# for key in dic1.keys():
#     for view in dic1[key]:
#         if view in dic.keys():
#             dic[view][1] += 1
#             j += 1
#         else:
#             k += 1
# print '测试数据共有' + str(i) + '个视角'
# print '共解析出' + str(j + k) + '个视角'
# print '共解析错' + str(k) + '个视角'
# fo = open('a.txt', 'w')
# for key in dic.keys():
#     c = key.encode('utf-8')
#     fo.write(c + '\t' + str(dic[key][0]) + '\t' + str(dic[key][1]) + '\n')
# fo.close()

i = 0
j = 0
fo = open('b.txt', 'w')
for key in dic2.keys():
    if key in dic1.keys():
        l = []
        g = []
        for s in dic2[key].keys():
            l.append(s)
        for s in dic1[key].keys():
            g.append(s)
        if len(l) == len(g):
            flag = True
            for view in l:
                if view.decode('utf-8') not in g:
                    flag = False
            if not flag:
                j += 1
                fo.write('\n' + key + '\n')
                fo.write(doc_dic[key] + '\n')
                fo.write('/'.join(l) + '\n')
                fo.write('/'.join(g).encode('utf-8') + '\n')
            else:
                i += 1
        else:
            j += 1
    else:
        j += 1
print '共解析正确' + str(i) + '条数据'
print '共解析错误' + str(j) + '条数据'