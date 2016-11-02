# encoding=utf-8
import jieba
import re


def prefix_match(s):  # 判断是否是某车品牌的前缀拼配
    return '!' + s.lower() in car_set


def entire_match(s):  # 判断是否是某车品牌
    return '!' + s.lower() + '!' in car_set


def get_car_set():  # 读取汽车品牌存储为字符串，品牌中间用'!'符号隔开
    f_in = open('data/car_list.txt', 'r')
    s = '!'
    for line in f_in:
        s += line.strip() + '!'
    return s.lower().decode('utf-8')

jieba.load_userdict('data/car_corpus.txt')
car_set = get_car_set()
car_regex = u'(^新)|(汽车)|(轿车)|(车$)'
sep_str = u'!，!,!。!；!;!?!？!'
and_str = u'!、!和!还有!包括!或!'
view_list = []
word_list = []
view_and_sep_index = []
sentence = '看大家说明锐后备箱空间无敌，上周六去店里看了现车，感觉并不大。'
seg_list = list(jieba.cut(sentence))
print '/'.join(seg_list)
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
length, i = len(word_list), 0
# for a, b in word_list:
#     print a, b
while i < length - 1:
    if word_list[i][1] == 'car' or word_list[i][1] == 'and':
        if word_list[i + 1][1] == 'car':
            word_list[i][1] = word_list[i + 1][1] = 'and'
        elif i < length - 2 and '!' + word_list[i+1][0] + '!' in and_str and word_list[i+2][1] == 'car':
            word_list[i][1] = word_list[i + 2][1] = 'and'
            word_list[i+1][1] = 'useless'
            i += 1
        elif i < length - 3 and '!' + word_list[i+1][0] + '!' in and_str and word_list[i+3][1] == 'car':
            word_list[i][1] = word_list[i+3][1] = 'and'
            word_list[i+1][1] = word_list[i+2][1] = 'useless'
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

# for a, b in word_list:
#     print a, b

temp_dic = {}
temp_list = []
if len(view_list) == 1:
    view = view_list[0]
    for word, flag in word_list:
        if flag != 'car' and flag != 'cut' and flag != 'sep' and flag != 'car' and flag != 'useless':
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

for view in temp_dic:
    print view
    print '/'.join(temp_dic[view])
