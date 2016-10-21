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
    fin = open('data/car_corpus.txt', 'r')
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


def get_prase_doc(name):  # 获取解析后文档数据，存储为oid_doc文件
    car_list = get_car_list()
    original_dic = get_original_doc(name)
    prase_dic = {}
    for sentence_id in original_dic.keys():
        sentence = original_dic[sentence_id]
        seg_list = jieba.cut(sentence)
        view_list = []
        word_list = []
        temp_dic = {}
        for word in seg_list:
            word_list.append(word)
            if word in car_list:
                if word not in view_list:
                    # dic[word][1] += 1
                    view_list.append(word)
        if len(view_list) == 1:
            view = view_list[0]
            for s in word_list:
                if s == view:
                    word_list.remove(view)
            temp_dic = {view: word_list}
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
                    # else:
                    #     temp_list.append(word)
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

#
# get_car_corpus()
jieba.load_userdict('data/car_corpus.txt')
get_train_label()
get_prase_doc('train.csv')
get_prase_doc('test.csv')

# dic = {}
# car_list = get_car_list()
# print car_list
# for car in car_list:
#     dic[car] = [0, 0]
# label_dic = joblib.load('data/oid_label.train')
# for key in label_dic.keys():
#     for view in label_dic[key]:
#         view = view.decode('utf-8')
#         if view in dic.keys():
#             dic[view][0] += 1
# print dic
# get_prase_doc('train.csv')
# print dic
# fo = open('a.txt', 'w')
# for key in car_list:
#     c = key.encode('utf-8')
#     fo.write(c + '\t' + str(dic[key][0]) + '\t' + str(dic[key][1]) + '\n')
# fo.close()
