import json

import numpy as np
from matplotlib import pyplot as plt
from redis import Redis
from scipy.optimize import curve_fit
from sklearn import linear_model

from clickHouseConnect import wssRequest

def pk_predict(x, a):
    return x ** ((-1) *a)

def DataFitAndVisualization(X,Y):
    # # 模型数据准备
    # X_parameter=[]
    # Y_parameter=[]
    # for single_square_feet ,single_price_value in zip(X,Y):
    #    X_parameter.append([float(single_square_feet)])
    #    Y_parameter.append(float(single_price_value))

    # 模型拟合
    popt_1, pcov_1 = curve_fit(pk_predict, X, Y)
    # regr = linear_model.LinearRegression()
    # regr.fit(X_parameter, Y_parameter)
    # # 模型结果与得分
    # print('Coefficients: \n', regr.coef_,)
    # print("Intercept:\n",regr.intercept_)
    # # The mean square error
    # print("Residual sum of squares: %.8f"
    #   % np.mean((regr.predict(X_parameter) - Y_parameter) ** 2))  # 残差平方和
    print("gama params: ", popt_1)

    # 可视化
    plt.title("Network Degree Distribution")
    plt.ylabel("log(P(k))")
    plt.xlabel("log(k)")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlim(1000, 100000)
    plt.ylim(0.00001, 1)
    plt.scatter(X, Y,  color='black', marker='o')
    # plt.plot(X, [pk_predict(x, popt_1[0]) for x in X], color='blue',linewidth=1)

    # plt.xticks(())
    # plt.yticks(())
    plt.show()

def store_data():
    get_all_repos_in_2019sql = "SELECT DISTINCT(repo_id) FROM year2019"
    cur_page = 0
    res = []
    repo_list = [] # pick 10000 repos as sample
    ops_count_list = [] # ops count
    while cur_page == 0 or len(res) >= 3000:
        cur_page += 1
        res = wssRequest(get_all_repos_in_2019sql,cur_page)
        for i in range(0, len(res)):
            repo_list.append(res[i]['C_1'])

    for i in range(0, len(repo_list)):
        get_all_ops = "SELECT COUNT(*) FROM year2019 WHERE repo_id=" + repo_list[i] \
                      + " AND (type='CommitCommentEvent' OR type='IssueCommentEvent' OR type='IssuesEvent' OR type='PullRequestReviewCommentEvent' OR type='PullRequestEvent' OR type='PushEvent')"
        ops_count_list.append(wssRequest(get_all_ops, 1)[0]['C_1'])

    cache = Redis(host='localhost', port=6379, decode_responses=True)
    cache.hset(name="all_repos", key='all_repos_ops_list', value=json.dumps(ops_count_list))

# store_data()
cache = Redis(host='localhost', port=6379, decode_responses=True)
ops_count_list = json.loads(cache.hget(name="all_repos", key='all_repos_ops_list'))

X = []
Y = []
counting = [] # [2^0 - 2^16]
for i in range(0, 20):
    counting.append(0)
    X.append(0)
    Y.append(0)
for ops_count in ops_count_list:
    if int(int(ops_count)/3000) < 20:
        counting[int(int(ops_count)/3000)] += 1
for i in range(0, 20):
    X[i] = i * 3000 + 1
    Y[i] = counting[i] / 10000
DataFitAndVisualization(X,Y)