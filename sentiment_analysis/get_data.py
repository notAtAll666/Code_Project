# encoding=utf-8

import jieba
from sklearn.externals import joblib


def get_car_corpus():  # 获取汽车语料库，存储为car_corpus.txt文件
    fin = open('original/view.csv', 'r')
    fout = open('data/car_corpus.txt', 'w')
    for line in fin:
        arr = line.strip().split('\t')
        fout.write(arr[1] + '\n')


def get_car_list():  # 读取汽车品牌数据，存储为ls并返回
    fin = open('data/car_list.txt', 'r')
    v_list = []
    for line in fin:
        v_list.append(line.strip().decode('utf-8'))
    return v_list


def get_car_str():  # 读取汽车品牌数据，存储为ls并返回
    fin = open('data/car_list.txt', 'r')
    v_str = '$'
    for line in fin:
        v_str += line.strip() + '$'
    return v_str.lower().decode('utf-8')


def get_original_doc(name):  # 获取原始文档数据，存储为dic并返回，utf-8编码
    fin = open('original/' + name, 'r')
    v_dic = {}
    for line in fin:
        arr = line.strip().split('\t')
        v_dic[arr[0]] = arr[1].strip()
    return v_dic


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


def has_same_pre(v_str):
    return '$' + v_str.lower() in car_str


def is_in(v_str):
    return '$' + v_str.lower() + '$' in car_str


def get_view_and_word(v_list):  # 从句子中找出视角并返回视角list和词list
    word_list = []
    view_list = []
    v_i = 0
    while v_i < len(v_list):
        word = v_list[v_i]
        v_view = ''
        while has_same_pre(word):
            if is_in(word):
                v_view = word
            if v_i == len(v_list) - 1:
                break
            if has_same_pre(word + v_list[v_i + 1]):
                word = word + v_list[v_i + 1]
                v_i += 1
            else:
                break
        if v_view != '':
            v_view = v_view.replace('轿车'.decode('utf-8'), '')
            v_view = v_view.replace('汽车'.decode('utf-8'), '')
            v_view = v_view.replace('车'.decode('utf-8'), '')
            word_list.append(v_view)
            if v_view not in view_list:
                view_list.append(v_view)
        else:
            word_list.append(word)
        v_i += 1
        for v_view in view_list:
            for v_view1 in view_list:
                if v_view != v_view1:
                    if v_view in v_view1:
                        view_list.remove(v_view)
                        break
    return view_list, word_list


def get_prase_doc(v_str):  # 获取解析后文档数据，存储为oid_doc文件
    if v_str == 'train.csv':
        original_dic = original_train_doc_dic
    else:
        original_dic = original_test_doc_dic
    prase_dic = {}
    for sentence_id in original_dic.keys():
        sentence = original_dic[sentence_id]
        seg_list = jieba.cut(sentence)
        v_l = []
        for word in seg_list:
            v_l.append(word)
        view_list, word_list = get_view_and_word(v_l)
        temp_dic = {}
        if len(view_list) == 1:
            v_view = view_list[0]
            v_l = []
            for v_s in word_list:
                v_l.append(v_s)
            temp_dic = {v_view: v_l}
        elif len(view_list) > 1:
            for v_view in view_list:
                temp_dic[v_view] = []
            temp_list = []
            cur_view = view_list[0]
            v_flag = 0
            for word in word_list:
                if word in view_list:
                    if word == cur_view:
                        v_flag = 1
                    else:
                        v_flag += 1
                    if v_flag == 2:
                        if len(temp_list) != 0:
                            temp_dic[cur_view] += temp_list
                            temp_list = []
                    cur_view = word
                elif word == u'，' or word == u'。':
                    temp_list.append(word)
                    if len(temp_list) != 0:
                        temp_dic[cur_view] += temp_list
                    temp_list = []
                    v_flag = 0
                else:
                    temp_list.append(word)
        prase_dic[sentence_id] = temp_dic
    if v_str == 'train.csv':
        joblib.dump(prase_dic, 'data/oid_doc.' + 'train')
        f = open('data\prase_train_doc.txt', 'w')
    elif v_str == 'test.csv':
        joblib.dump(prase_dic, 'data/oid_doc.' + 'test')
        f = open('data\prase_test_doc.txt', 'w')
    for sentence_id in prase_dic.keys():
        temp = prase_dic[sentence_id]
        if len(temp) != 0:
            f.write('\n')
            f.write(sentence_id)
            f.write('\n')
            for v_view in temp.keys():
                str1 = v_view.encode('utf-8')
                str2 = '/'.join(temp[v_view]).encode('utf-8')
                f.write(str1 + '\n' + str2 + '\n')


def out_log():  # 打印解析结果到文件
    dic1 = joblib.load('data/oid_label.train')
    dic2 = joblib.load('data/oid_doc.train')
    p = 0
    q = 0
    i = 0
    j = 0
    fo = open('result/wrong_view.txt', 'w')
    fo1 = open('result/aa.txt', 'w')
    for key in dic1.keys():
        l = []
        g = []
        for s in dic1[key].keys():
            l.append(s)
        p += len(l)
        for s in dic2[key].keys():
            g.append(s)
        fo1.write('\n' + key + '\n')
        fo1.write(original_train_doc_dic[key] + '\n')
        fo1.write('/'.join(l) + '\n')
        fo1.write('/'.join(g).encode('utf-8') + '\n')
        q += len(g)
        flag = True
        if len(l) == len(g):
            for view in l:
                if view.decode('utf-8') not in g:
                    j += 1
                    flag = False
                else:
                    i += 1
        else:
            flag = False
            for view in l:
                if view.decode('utf-8') not in g:
                    j += 1
                else:
                    i += 1
        if not flag:
            fo.write('\n' + key + '\n')
            fo.write(original_train_doc_dic[key] + '\n')
            fo.write('/'.join(l) + '\n')
            fo.write('/'.join(g).encode('utf-8') + '\n')

    joblib.dump([p, q, i, p-i, q-i], 'data/oid_temp.' + 'temp')
    print '共有视角' + str(p) + '条'
    print '共解析出有视角' + str(q) + '条'
    print '共解析正确' + str(i) + '条数据'
    print '共解析错误' + str(q-i) + '条数据'

    i = 0
    f = open('result/wrong_view1.txt', 'w')
    for key in dic2.keys():
        if key not in dic1.keys():
            if len(dic2[key].keys()) != 0:
                l = []
                for view in dic2[key].keys():
                    l.append(view)
                    i += 1
                f.write('\n' + key + '\n')
                f.write(original_train_doc_dic[key] + '\n')
                f.write('/'.join(l).encode('utf-8') + '\n')
    print '多解析出' + str(i) + '条数据'



# get_car_corpus()
jieba.load_userdict('data/car_corpus.txt')
car_str = get_car_str()
car_list = get_car_list()
get_train_label()
original_train_doc_dic = get_original_doc('train.csv')
original_test_doc_dic = get_original_doc('test.csv')
get_prase_doc('train.csv')
get_prase_doc('test.csv')
out_log()
