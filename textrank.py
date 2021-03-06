# coding:utf-8
import re
import time
import jieba
from math import sqrt
import os


def ReadFile(txtname):
    fp = open(txtname,'r')
    data = []
    for line in fp.readlines():
        line = line.strip()
        data.append(line)

    claims_num = 0 # 权利要求书所在的行号
    description_num = 0 # 说明书所在的行号
    for i in range(len(data)):
        if data[i] == '权利要求书':
            claims_num = i
        if data[i] == '说明书':
            description_num = i

    PatentClaims = ''
    for i in range(claims_num+1,description_num):
        PatentClaims += data[i].strip()

    PatentDescription = ''
    for i in range(description_num+1,len(data)):
        PatentDescription += data[i].strip()

    PatentString = PatentClaims + PatentDescription

    AllPatentData={}
    AllPatentData['PatentNumber'] = data[0]
    AllPatentData['PatentName'] = data[1]
    AllPatentData['PatentAbstract'] = data[3]
    AllPatentData['PatentClaims'] = PatentClaims
    AllPatentData['PatentDescription'] = PatentDescription
    AllPatentData['PatentContent'] = PatentString

    return AllPatentData


def get_similarity(sentence1,sentence2):
    lst = []
    seg_list1 = jieba.lcut(sentence1)
    seg_list2 = jieba.lcut(sentence2)
    lst.append(seg_list1)
    lst.append(seg_list2)
    for each in lst:
        while '.' in each:
            each.remove('.')
        while '：' in each:
            each.remove('：')
        while '(' in each:
            each.remove('(')
        while ')' in each:
            each.remove(')')
        while '、' in each:
            each.remove('、')
        while '“' in each:
            each.remove('“')
        while '”' in each:
            each.remove('”')
        while '-' in each:
            each.remove('-')
    tag_dict1 = {}
    tag_dict2 = {}
    for item in seg_list1:
        if item in tag_dict1:
            tag_dict1[item] = tag_dict1[item] + 1
        else:
            tag_dict1[item] = 1
    for item in seg_list2:
        if item in tag_dict2:
            tag_dict2[item] = tag_dict2[item] + 1
        else:
            tag_dict2[item] = 1
    a1 = sum(tag_dict1[item]**2 for item in tag_dict1)
    a2 = sum(tag_dict2[item]**2 for item in tag_dict2)
    b = sum(tag_dict1[item] * tag_dict2[item] for item in tag_dict1 if item in tag_dict2)
    return b/sqrt(a1*a2)


def get_simall(doc,sentence):
    sim = []
    for i in sentence:
        sim.append(get_similarity(doc,i))
    return sim

def GetDigest(content):
    sentence = re.split(r'[，；？。！：]',content)

    while '' in sentence:
        sentence.remove('')

    D = len(sentence)
    weight = []
    weight_sum = []
    vertex = []
    max_iter = 200
    min_diff = 0.0001

    for cnt,doc in enumerate(sentence):
        scores = get_simall(doc,sentence)
        weight.append(scores)
        weight_sum.append(sum(scores)-scores[cnt])
        vertex.append(1.0)

    for _ in range(max_iter):
        m = []
        max_diff = 0
        for i in range(D):
            m.append(0.15)
            for j in range(D):
                if j==i or weight_sum[j] == 0:
                    continue
                m[-1] = m[-1] + (0.85 * weight[j][i] / weight_sum[j] * vertex[j])
            if abs(m[-1] - vertex[i]) > max_diff:
                max_diff = abs(m[-1] - vertex[i])
        vertex = m
        if max_diff <= min_diff:
            break

    top = list(enumerate(vertex))
    top = sorted(top,key=lambda x:x[1],reverse=True)

    summary_str = ''
    for i in range(len(top)):
        summary_str = summary_str + '，' + sentence[top[i][0]]
        if len(summary_str) >= 260:
            break
    summary_str = summary_str[1:]
    print(summary_str)
    print(len(summary_str))
    return summary_str

def main():
    starttime = time.clock()

    PatentData = ReadFile("CN208315896U.txt")
    summary = GetDigest(PatentData['PatentContent'])
    
    endtime = time.clock()
    print("花费时间为:" , endtime - starttime)

if __name__ == '__main__':
    main()