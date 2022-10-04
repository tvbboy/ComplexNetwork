import json
import math
import numpy as np
from scipy.optimize import curve_fit
from mysql_connect.mysql_tool import execute_sql
from redis import Redis
from math import e
from sklearn.linear_model import LassoCV, RidgeCV

def linear_predict(x, a, b):
    return a * x + b

def Bass_predict(x, m, p, q):
    return m * (p * (p + q) ** 2) * e ** (x) / ((p + q * e ** (x)) ** 2)
    # return (p+(q/m)*(x))*(m-x)

def Gompertz_predict(x, k, a):
    return k * np.e ** a ** x

def BA_predict(x, b):
    return b * (x ** 0.5)

def BB_predict(x, a, b):
    return b * (x ** a)

# Mean Squared Error
def MSE(n, expects, reals):
    mse = 0
    for i in range(0, n):
        mse += math.pow(expects[i] - reals[i], 2)
    mse /= n
    return np.round(mse, 2)

# Root Mean Squared Error
def RMSE(n, expects, reals):
    rmse = 0
    for i in range(0, n):
        rmse += math.pow(expects[i] - reals[i], 2)
    rmse /= n
    rmse = math.pow(rmse, 0.5)
    return np.round(rmse, 2)

# Mean absolute Error
def MAE(n, expects, reals):
    mae = 0
    for i in range(0, n):
        mae += abs(expects[i] - reals[i])
    mae /= n
    return np.round(mae, 2)

# Root Mean Squared Logaritmic Error
def RMSLE(n, expects, reals):
    rmsle = 0
    for i in range(0, n):
        rmsle += math.pow(math.log(expects[i]+1) - math.log(reals[i]+1), 2)
    rmsle /= n
    rmsle = math.pow(rmsle, 0.5)
    return round(rmsle, 2)

#   res_map = {
#       "repo_id" : {
#           "repo_name": xxx,
#           "201901" : 123,
#           "201902" : 456
#           ...
#       }
#       ...
#   }
date_list = ["201901", "201902", "201903", "201904", "201905", "201906", "201907", "201908", "201909", "201910", "201911", "201912"]
def get_map(lamda_2):
    res_map = {}
    repo_ids = []
    repo_ids_raw_data = execute_sql("select distinct(repo_i) from edge")
    for r in repo_ids_raw_data:
        repo_ids.append(str(r).split("'")[1])
    for repo_id in repo_ids:
        map = {}
        repo_name = execute_sql("select repo_name from repo where repo_id = " + str(repo_id))[0][0]
        map["repo_name"] = repo_name
        sum_weight = 0
        # 第二个超参：控制度有增加的月数在总月数的占比，太低会出现无法拟合的情况
        add_weight_threshold = 0
        for date in date_list:
            add_weight = 0
            weights = execute_sql("select weight from edge where (repo_i = " + repo_id + " or " + "repo_j = " + repo_id + ") and " + "date = " + date)
            for weight in weights:
                add_weight += int(str(weight).split(",")[0].split("(")[1])
            sum_weight += add_weight
            if add_weight > 0:
                add_weight_threshold += 1
            map[date] = sum_weight
        if add_weight_threshold > lamda_2:
            res_map[repo_id] = map
    print(res_map)
    return res_map


# prediect_list = [
#       {
#          "repo_name": xxx,
#          "t_start": "2019-01",
#          "t_end": "2019-12",
#          "real": 1000,
#          "linear_predict": 1200,
#          "BA_predict": 1500,
#          "BB_predict": 2100
#          "fitness": 2.2
#       },
#       ...
# ]
def predict(lamda2):
    # res_map = json.loads(cache.hget(name='lamda2=' + str(lamda2), key='data_1'))
    res_map = json.loads(cache.hget(name="lamda1=30", key='lamda2='+str(lamda2)))
    predict_list = []
    reals = []
    expect_1 = []
    expect_2 = []
    expect_3 = []
    expect_4 = []
    expect_5 = []
    expect_6 = []
    expect_7 = []
    linear_params = []
    BA_params = []
    BB_params = []
    Base_params = []
    Gompertz_params = []
    C = 1.255
    num_of_repo = 0
    for key in res_map.keys():
        repo_predict_res = {}
        num_of_repo += 1
        x_data = [1,2,3,4,5,6,7,8,9,10,11]
        y_data = []
        for date in date_list:
            if(date != "201912"):
                y_data.append(res_map[key][date])
        popt_1, pcov_1 = curve_fit(linear_predict, x_data, y_data)
        popt_2, pcov_2 = curve_fit(BA_predict, x_data, y_data)
        popt_3, pcov_3 = curve_fit(BB_predict, x_data, y_data, maxfev=100000)
        popt_4, pcov_4 = curve_fit(Bass_predict, x_data, y_data, maxfev=500000)
        popt_5, pcov_5 = curve_fit(Gompertz_predict, x_data, y_data, maxfev=500000)
        # 0.01 - 100 中选择 alpha
        alpha_range = np.logspace(-6, 6, 200, base=10)
        # 交叉验证正则化参数，默认5折
        lasso = LassoCV(cv=5, max_iter=100000)
        lasso.fit(np.array(x_data).reshape(-1, 1), y_data)
        # # 查看最佳正则化系数
        # print("Lasso best alpha: " ,lasso.alpha_)
        ridge = RidgeCV(cv=5)
        ridge.fit(np.array(x_data).reshape(-1, 1), y_data)
        # # 查看最佳正则化系数
        # print("Ridge best alpha: ", lasso.alpha_)

        linear_params.append(popt_1)
        BA_params.append(popt_2)
        BB_params.append(popt_3)
        # Base_params.append(popt_4)
        # Gompertz_params.append(popt_5)
        reals.append(res_map[key]["201912"])

        x_data.append(12)
        y_data_1 = [linear_predict(i, popt_1[0], popt_1[1]) for i in x_data]
        y_data_2 = [BA_predict(i, popt_2[0]) for i in x_data]
        y_data_3 = [BB_predict(i, popt_3[0], popt_3[1]) for i in x_data]
        y_data_4 = [Bass_predict(i, popt_4[0], popt_4[1], popt_4[2]) for i in x_data]
        y_data_5 = [Gompertz_predict(i, popt_5[0], popt_5[1]) for i in x_data]
        y_data_6 = lasso.predict(np.array(x_data).reshape(-1,1))
        y_data_7 = ridge.predict(np.array(x_data).reshape(-1,1))

        expect_1.append(round(y_data_1[11], 2))
        expect_2.append(round(y_data_2[11], 2))
        expect_3.append(round(y_data_3[11], 2))
        expect_4.append(round(y_data_4[11], 2))
        expect_5.append(round(y_data_5[11], 2))
        expect_6.append(round(y_data_6[11], 2))
        expect_7.append(np.round(y_data_7[11], 2))

        fitness = popt_3[0] * C

        repo_predict_res["repo_name"] = res_map[key]["repo_name"]
        repo_predict_res["t_start"] = "2019-01"
        repo_predict_res["t_end"] = "2019-12"
        repo_predict_res["real"] = res_map[key]["201912"]
        repo_predict_res["linear_predict"] = round(y_data_1[11], 2)
        repo_predict_res["BA_predict"] = round(y_data_2[11], 2)
        repo_predict_res["BB_predict"] = round(y_data_3[11], 2)
        repo_predict_res["Bass_predict"] = round(y_data_4[11], 2)
        repo_predict_res["Gompertz_predict"] = round(y_data_5[11], 2)
        repo_predict_res["lasso_predict"] = round(y_data_6[11], 2)
        repo_predict_res["ridge_predict"] = np.round(y_data_7[11], 2)
        repo_predict_res["fitness"] = round(fitness, 2)
        predict_list.append(repo_predict_res)

    for p in predict_list:
        print(p)

    print("Mean Squared Error Of linear_predict: " + str(MSE(num_of_repo, expect_1, reals)))
    print("Root Mean Squared Error Of linear_predict: " + str(RMSE(num_of_repo, expect_1, reals)))
    print("Mean absolute Error Of linear_predict: " + str(MAE(num_of_repo, expect_1, reals)))
    print()
    print("Mean Squared Error Of BA_predict: " + str(MSE(num_of_repo, expect_2, reals)))
    print("Root Mean Squared Error Of BA_predict: " + str(RMSE(num_of_repo, expect_2, reals)))
    print("Mean absolute Error Of BA_predict: " + str(MAE(num_of_repo, expect_2, reals)))
    print()
    print("Mean Squared Error Of BB_predict: " + str(MSE(num_of_repo, expect_3, reals)))
    print("Root Mean Squared Error Of BB_predict: " + str(RMSE(num_of_repo, expect_3, reals)))
    print("Mean absolute Error Of BB_predict: " + str(MAE(num_of_repo, expect_3, reals)))
    print()
    print("Mean Squared Error Of Bass_predict: " + str(MSE(num_of_repo, expect_4, reals)))
    print("Root Mean Squared Error Of Bass_predict: " + str(RMSE(num_of_repo, expect_4, reals)))
    print("Mean absolute Error Of Bass_predict: " + str(MAE(num_of_repo, expect_4, reals)))
    print()
    print("Mean Squared Error Of Gompertz_predict: " + str(MSE(num_of_repo, expect_5, reals)))
    print("Root Mean Squared Error Of Gompertz_predict: " + str(RMSE(num_of_repo, expect_5, reals)))
    print("Mean absolute Error Of Gompertz_predict: " + str(MAE(num_of_repo, expect_5, reals)))
    print()
    print("Mean Squared Error Of lasso_predict: " + str(MSE(num_of_repo, expect_6, reals)))
    print("Root Mean Squared Error Of lasso_predict: " + str(RMSE(num_of_repo, expect_6, reals)))
    print("Mean absolute Error Of lasso_predict: " + str(MAE(num_of_repo, expect_6, reals)))
    print()
    print("Mean Squared Error Of ridge_predict: " + str(MSE(num_of_repo, expect_7, reals)))
    print("Root Mean Squared Error Of ridge_predict: " + str(RMSE(num_of_repo, expect_7, reals)))
    print("Mean absolute Error Of ridge_predict: " + str(MAE(num_of_repo, expect_7, reals)))
    res = {}
    res["predict_list"] = predict_list
    res["linear_params"] = linear_params
    res["BA_params"] = BA_params
    res["BB_params"] = BB_params
    return res
cache = Redis(host='localhost', port=6379, decode_responses=True)
# cache.hset(name="lamda1=10", key='lamda2=0.00', value=json.dumps(get_map(0)))
# cache.hset(name="lamda1=10", key='lamda2=0.08', value=json.dumps(get_map(1)))
# cache.hset(name="lamda1=10", key='lamda2=0.17', value=json.dumps(get_map(2)))
# cache.hset(name="lamda1=1", key='lamda2=0.25', value=json.dumps(get_map(3)))
# cache.hset(name="lamda1=1", key='lamda2=0.33', value=json.dumps(get_map(4)))
# cache.hset(name="lamda1=1", key='lamda2=0.42', value=json.dumps(get_map(5)))
# cache.hset(name="lamda1=1", key='lamda2=0.50', value=json.dumps(get_map(6)))
# cache.hset(name="lamda1=1", key='lamda2=0.58', value=json.dumps(get_map(7)))
# cache.hset(name="lamda1=1", key='lamda2=0.67', value=json.dumps(get_map(8)))
# cache.hset(name="lamda1=1", key='lamda2=0.75', value=json.dumps(get_map(9)))
# cache.hset(name="lamda1=1", key='lamda2=0.83', value=json.dumps(get_map(10)))
# cache.hset(name="lamda1=1", key='lamda2=0.92', value=json.dumps(get_map(11)))
# cache.hset(name="lamda1=1", key='lamda2=1.00', value=json.dumps(get_map(12)))
# print(json.loads(cache.hget(name="lamda1=1", key='lamda2=0.00')))
predict("0.25")
predict("0.42")
predict("0.58")
predict("0.75")

# print(len(json.loads(cache.hget(name="lamda1=10", key='lamda2=0.17')).keys()))