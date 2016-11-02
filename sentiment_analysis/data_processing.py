# encoding=utf-8
import re
import time
import jieba
from sklearn.externals import joblib


def get_car_set():  # 读取汽车品牌存储为字符串，品牌中间用'!'符号隔开
    f_in = open('data/car_list.txt', 'r')
    s = '!'
    for line in f_in:
        s += line.strip() + '!'
    return s.lower().decode('utf-8')


def get_train_label():  # 将训练集标签数据存储为{id:{view:label}}形式的train_label
    start = time.time()

    f_in = open('original/label.csv', 'r')
    train_label_dic = {}
    for line in f_in:
        arr = line.strip().split('\t')
        arr[1] = arr[1].decode('utf-8')
        if arr[0] in train_label_dic:
            train_label_dic[arr[0]][arr[1]] = 0 if arr[2] == 'neg' else 2 if arr[2] == 'pos' else 1
        else:
            label = 0 if arr[2] == 'neg' else 2 if arr[2] == 'pos' else 1
            train_label_dic[arr[0]] = {arr[1]: label}
    joblib.dump(train_label_dic, 'data/train_label.dump')
    end = time.time()
    print "处理解析标签数据用时%f 秒:end..." % (end - start)


def get_original_doc():  # 将原始文档数据存储为original_train_doc和original_test_doc，并处理相同句子并存入answer.csv
    start = time.time()
    # 将原始训练文档数据存储为{id:doc}形式的字典
    train_label_dic = joblib.load('data/train_label.dump')
    f_in = open('original/train.csv', 'r')
    original_train_doc = {}
    original_train_doc_re = {}
    for line in f_in:
        arr = line.strip().split('\t')
        arr[1] = arr[1].strip().decode('utf-8')
        original_train_doc[arr[0]] = arr[1]
        original_train_doc_re[arr[1]] = arr[0]
    joblib.dump(original_train_doc, 'data/original_train_doc.dump')
    # 将原始测试文档数据存储为{id:doc}形式的字典
    f_in = open('original/test.csv', 'r')
    original_test_doc = {}
    original_test_doc_re = {}
    for line in f_in:
        arr = line.strip().split('\t')
        arr[1] = arr[1].strip().decode('utf-8')
        original_test_doc[arr[0]] = arr[1]
        original_test_doc_re[arr[1]] = arr[0]
    f_out = open('result/answer.csv', 'w')
    f_out.write('SentenceId,View,Opinion\n')
    # 查找文档相同项从测试字典中删除，并将结果存入answer.csv中
    for doc in original_train_doc_re:
        if doc in original_test_doc_re:
            id1 = original_train_doc_re[doc]
            id2 = original_test_doc_re[doc]
            del original_test_doc[id2]
            if id1 in train_label_dic:
                for view in train_label_dic[id1]:
                    opinion = train_label_dic[id1][view]
                    opinion = 'neg' if opinion == 0 else 'pos' if opinion == 2 else 'neu'
                    line = (id2 + ',' + view + ',' + opinion + '\n').encode('utf-8')
                    f_out.write(line)
    joblib.dump(original_test_doc, 'data/original_test_doc.dump')
    f_in.close()
    f_out.close()

    end = time.time()
    print "处理原始文本数据用时%f 秒:end..." % (end - start)


def prefix_match(s):  # 判断是否是某车品牌的前缀拼配
    return '!' + s.lower() in car_set


def entire_match(s):  # 判断是否是某车品牌
    return '!' + s.lower() + '!' in car_set


def get_view_and_word(name):  # 从句子中找出视角并缓存视角list和词list
    start = time.time()
    car_regex = u'(^新)|(汽车)|(轿车)|(车$)'
    sep_str = u'!，!,!。!；!;!?!？!'
    and_str = u'!、!和!还有!包括!或!'
    if name == 'train':
        original_doc = joblib.load('data/original_train_doc.dump')
    else:
        original_doc = joblib.load('data/original_test_doc.dump')
    prase_word_dic = {}
    for id1 in original_doc:
        prase_word_dic[id1] = {}
        view_list = []
        word_list = []
        view_and_sep_index = []
        sentence = original_doc[id1]
        seg_list = list(jieba.cut(sentence))
        seg_list.append(u'。')
        length, p, q = len(seg_list), 0, 0
        while p < length:
            cur_word = seg_list[p]
            cur_view = ''
            while prefix_match(cur_word):
                if entire_match(cur_word):
                    cur_view = cur_word
                if prefix_match(cur_word + seg_list[p + 1]):
                    cur_word = cur_word + seg_list[p + 1]
                    p += 1
                else:
                    break
            if cur_view != '':
                cur_view = re.sub(car_regex, '', cur_view)
                word_list.append([cur_view, 'car'])
                view_and_sep_index.append([q, 'car'])
                q += 1
                if cur_view not in view_list:
                    view_list.append(cur_view)
            elif '!' + cur_word + '!' in sep_str:
                view_and_sep_index.append([q, 'sep'])
                word_list.append([cur_word, 'sep'])
                q += 1
            else:
                word_list.append([cur_word, 'unknown'])
                q += 1
            p += 1
        if len(word_list) == 0:
            continue

        length, i = len(word_list), 0
        while i < length - 1:
            if word_list[i][1] == 'car' or word_list[i][1] == 'and':
                if word_list[i + 1][1] == 'car':
                    word_list[i][1] = word_list[i + 1][1] = 'and'
                elif i < length - 2 and '!' + word_list[i + 1][0] + '!' in and_str and word_list[i + 2][1] == 'car':
                    word_list[i][1] = word_list[i + 2][1] = 'and'
                    word_list[i + 1][1] = 'useless'
                    i += 1
                elif i < length - 3 and '!' + word_list[i + 1][0] + '!' in and_str and word_list[i + 3][1] == 'car':
                    word_list[i][1] = word_list[i + 3][1] = 'and'
                    word_list[i + 1][1] = word_list[i + 2][1] = 'useless'
                    i += 2
            i += 1

        length, i = len(view_and_sep_index), 0
        flag = False
        while i < length:
            if view_and_sep_index[i][1] == 'sep':
                if flag:
                    while i < length - 1 and view_and_sep_index[i + 1][1] == 'sep':
                        i += 1
                    word_list[view_and_sep_index[i][0]][1] = 'cut'
            else:
                flag = True
            i += 1

        prase_word_dic[id1][0] = view_list
        prase_word_dic[id1][1] = word_list
    if name == 'train':
        joblib.dump(prase_word_dic, 'data/prase_train_dic.dump')
    else:
        joblib.dump(prase_word_dic, 'data/prase_test_dic.dump')
    end = time.time()
    print "获取视角和词语用时%f 秒:end..." % (end - start)


def get_prase_doc(name):  # 获取解析后文档数据，存储为oid_doc文件
    start = time.time()
    if name == 'train':
        dic1 = joblib.load('data/prase_train_dic.dump')
    else:
        dic1 = joblib.load('data/prase_test_dic.dump')
    prase_dic = {}
    for sentence_id in dic1.keys():
        view_list = dic1[sentence_id][0]
        word_list = dic1[sentence_id][1]
        temp_dic = {}
        temp_list = []
        if len(view_list) == 1:
            view = view_list[0]
            for word, flag in word_list:
                if flag != 'car' and flag != 'cut' and flag != 'sep' and flag != 'car':
                    temp_list.append(word)
            temp_dic = {view: temp_list}
        if len(view_list) > 1:
            same_view_list = []
            for view in view_list:
                temp_dic[view] = []
            cur_view = ''
            for word, flag in word_list:
                if flag == 'car':
                    if cur_view == '' and len(same_view_list) == 0:
                        pass
                    elif cur_view == '' and len(same_view_list) != 0:
                        for view in same_view_list:
                            temp_dic[view] += temp_list
                        same_view_list = []
                    elif word != cur_view:
                        temp_dic[cur_view] += temp_list
                        temp_list = []
                    cur_view = word
                elif flag == 'and':
                    if cur_view != '':
                        temp_dic[cur_view] += temp_list
                        temp_list = []
                    cur_view = ''
                    same_view_list.append(word)
                elif flag == 'cut':
                    if cur_view != '':
                        temp_dic[cur_view] += temp_list
                        cur_view = ''
                    elif len(same_view_list) != 0:
                        for view in same_view_list:
                            temp_dic[view] += temp_list
                        same_view_list = []
                    temp_list = []
                else:
                    if flag != 'sep' and flag != 'useless' and word != ' ':
                        temp_list.append(word)
        l = temp_dic.keys()
        r = []
        for view in l:
            for view1 in l:
                if view != view1 and view in view1:
                    temp_dic[view1] += temp_dic[view]
                    r.append(view)
                    break
        for view in r:
            del temp_dic[view]
        prase_dic[sentence_id] = temp_dic

    if name == 'train':
        joblib.dump(prase_dic, 'data/prase_train_doc.dump')
        f = open('data/prase_train_doc.txt', 'w')
        d = joblib.load('data/original_train_doc.dump')
    else:
        joblib.dump(prase_dic, 'data/prase_test_doc.dump')
        f = open('data/prase_test_doc.txt', 'w')
        d = joblib.load('data/original_test_doc.dump')

    for sentence_id in prase_dic.keys():
        temp = prase_dic[sentence_id]
        if len(temp) != 0:
            f.write(sentence_id)
            f.write('\n')
            f.write(d[sentence_id].encode('utf-8') + '\n')
            for v_view in temp.keys():
                str1 = v_view.encode('utf-8')
                str2 = '/'.join(temp[v_view]).encode('utf-8')
                f.write(str1 + '\n' + str2 + '\n')
            f.write('\n')
    end = time.time()
    print "划分视角语句用时%f 秒:end..." % (end - start)


def out_log():  # 打印解析结果到文件
    start = time.time()
    original_train_doc_dic = joblib.load('data/original_train_doc.dump')
    dic1 = joblib.load('data/train_label.dump')
    dic2 = joblib.load('data/prase_train_doc.dump')
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
        fo1.write(original_train_doc_dic[key].encode('utf-8') + '\n')
        fo1.write('/'.join(l).encode('utf-8') + '\n')
        fo1.write('/'.join(g).encode('utf-8') + '\n')
        q += len(g)
        flag = True
        if len(l) == len(g):
            for view in l:
                if view not in g:
                    j += 1
                    flag = False
                else:
                    i += 1
        else:
            flag = False
            for view in l:
                if view not in g:
                    j += 1
                else:
                    i += 1
        if not flag:
            fo.write('\n' + key + '\n')
            fo.write(original_train_doc_dic[key].encode('utf-8') + '\n')
            fo.write('/'.join(l).encode('utf-8') + '\n')
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
                f.write(original_train_doc_dic[key].encode('utf-8') + '\n')
                f.write('/'.join(l).encode('utf-8') + '\n')
    print '从没有视角的句子中解析出' + str(i) + '条数据'
    end = time.time()
    print "分析处理效果用时%f 秒:end..." % (end - start)

jieba.load_userdict('data/car_corpus.txt')
ss = u'&a&ad&an&d&n&vg&v&vd&vn&vg&'
car_set = get_car_set()
get_train_label()
get_original_doc()
get_view_and_word('train')
get_view_and_word('test')
get_prase_doc('train')
get_prase_doc('test')
out_log()
