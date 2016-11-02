# encoding=utf-8

import time
import random

from sklearn import linear_model
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from sklearn import cross_validation

trainFile = ''  # sys.argv[1] # gamble / drug
trainModel = 'lr'  # sys.argv[2] # lr / gbdt


def proc_train_data():
    """
    读取训练数据，放入docs和labels里
    """
    fin = open('original/train.csv', 'r')
    label_dic = joblib.load('data/train_label.dump')
    text_dic = joblib.load('data/prase_train_doc.dump')
    docs = []
    labels = []
    for sentence_id in label_dic.keys():
        for view1 in label_dic[sentence_id].keys():
            if sentence_id in text_dic.keys():
                for view2 in text_dic[sentence_id].keys():
                    if view1 == view2:
                        content = ' '.join(text_dic[sentence_id][view2])
                        label = label_dic[sentence_id][view1]
                        docs.append(content)
                        labels.append(label)
    fin.close()
    return cross_validation.train_test_split(docs, labels, test_size=0.2, random_state=random.randint(0, 100))  # 划分验证集


def train_tfidf_model(train_data, test_data):
    """
    训练tfidf模型，保存模型和词典
    """
    tfidf_model = TfidfVectorizer(encoding='utf-8', use_idf=False, sublinear_tf=True, min_df=10)
    train_vec = tfidf_model.fit_transform(train_data)
    test_vec = tfidf_model.transform(test_data)
    joblib.dump(tfidf_model, 'model/tf_idf')  # 保存模型
    # 保存词典
    fout = open('result/ivoca_to_see', 'w')
    i = 0
    ivoca = {}
    for value, number in tfidf_model.vocabulary_.items():
        ivoca[number] = value
        # print >> fout, value
        i += 1
    fout.close()
    print '\t词典长度为:' + str(i)
    return train_vec, test_vec, ivoca


def train_classify_model(test_data, train_vec, test_vec, train_labels, test_labels, ivoca):
    """
    训练分类模型,保存分类模型和对应的importance
    """
    # 训练模型并保存模型和对应的importance
    if trainModel == 'lr': # 定义模型
        content_model = linear_model.LogisticRegression(n_jobs=8, solver='liblinear', class_weight='balanced', C=0.8, penalty='l2')
        content_model.fit(train_vec, train_labels)  # 训练
        importance = content_model.coef_[0]
    elif trainModel == 'gbdt':
        content_model = GradientBoostingClassifier(learning_rate=0.01, n_estimators=1000, max_depth=1, random_state=random.randint(0,100))
        content_model.fit(train_vec, train_labels)  # 训练
        importance = content_model.feature_importances_

    joblib.dump(content_model, 'model/content_' + trainModel)
    fout = open('result/model_coe_' + trainModel, 'w')
    for i in range(len(importance)):
        if importance[i] != 0:
            print >> fout, '%s\t%f' % (ivoca[i], importance[i])

    # 训练集结果
    pred_y = content_model.predict(train_vec.toarray())
    pred_y_train = pred_y[:]
    # 测试集结果
    pred_y = content_model.predict(test_vec.toarray())
    pred_y_test = pred_y[:]
    # 模型效果
    calc_train_effect(importance, train_labels, test_labels, pred_y_train, pred_y_test, test_data)


def calc_train_effect(importance, train_labels, test_labels, pred_y_train, pred_y_test, test_data):
    """
    评估训练模型效果
    """
    print '\t训练集样本数:'+str(len(train_labels))
    # print '\t训练集上AUC:'+str(metrics.roc_auc_score(train_labels, pred_y_train))
    print '\t测试集样本数:'+str(len(test_labels))
    # print '\t测试集上AUC:'+str(metrics.roc_auc_score(test_labels, pred_y_test))
    pred_y_test_value = [round(line, 0) for line in pred_y_test]

    # 把某种形式错分的样本存储到文件里
    fout = open('result/wrong.txt', 'w')
    for k in range(len(pred_y_test_value)):
        if pred_y_test_value[k] == 1 and test_labels[k] == 0:
            print >> fout, test_data[k].encode('utf-8')
    fout.close()

    # 评估模型效果
    confusion_value = confusion_matrix(test_labels, pred_y_test_value)
    s00 = confusion_value[0][0]
    s01 = confusion_value[0][1]
    s02 = confusion_value[0][2]
    s10 = confusion_value[1][0]
    s11 = confusion_value[1][1]
    s12 = confusion_value[1][2]
    s20 = confusion_value[2][0]
    s21 = confusion_value[2][1]
    s22 = confusion_value[2][2]
    print confusion_value
    print '\t总准确率:'+str((s00 + s11 + s22)*1.0 / (s00 + s01 + s02 + s10 + s11 + s12 + s20 + s21 + s22))
    print '\t正样本准确率:' + str(s22 * 1.0 / (s02 + s12 + s22))
    print '\t正样本召回率:' + str(s22 * 1.0 / (s20 + s21 + s22))
    print '\t负样本准确率:' + str(s00 * 1.0 / (s00 + s10 + s20))
    print '\t负样本召回率:' + str(s00 * 1.0 / (s00 + s01 + s02))
    print '\t中样本准确率:' + str(s11 * 1.0 / (s01 + s11 + s21))
    print '\t中样本召回率:' + str(s11 * 1.0 / (s10 + s11 + s12))
    l = joblib.load('data/oid_temp.temp')
    tp = s00 + s11 + s22
    fp = s01 + s02 + s10 + s12 + s20 + s21
    fn1 = l[3] * 1.0 / 5
    fn2 = l[4] * 1.0 / 5
    p = tp * 1.0 / (tp + fp + fn2)
    r = tp * 1.0 / (tp + fn1)
    f1 = 2.0 * p * r / (p + r)
    print '\t准确率P:' + str(p)
    print '\t召回率R:' + str(r)
    print '\t总得分F1:' + str(f1)


if __name__ == '__main__':
    print "模型构建:start..."
    start = time.time()
    print "处理数据中..."
    train_data, test_data, train_labels, test_labels = proc_train_data()
    print "训练tf_idf模型中..."
    train_vec, test_vec, ivoca = train_tfidf_model(train_data, test_data)
    print "训练分类模型中..."
    train_classify_model(test_data, train_vec, test_vec, train_labels, test_labels, ivoca)
    end = time.time()
    print "用时%f 分钟:end..." % round((end - start)/60, 4)