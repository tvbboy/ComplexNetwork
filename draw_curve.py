import json
from redis import Redis
import matplotlib.pyplot as plt
from handle_data import predict
import numpy as np

cache = Redis(host='localhost', port=6379, decode_responses=True)
predict_map = predict(lamda2="0.50")
map = json.loads(cache.hget("lamda1=10","lamda2=0.50"))
print(predict_map['predict_list'][3])
print(map['105314178'])

selected_repo = map['105314178']
x = [1,2,3,4,5,6,7,8,9,10,11,12]
x_range = np.arange(1, 12, 0.1)
y_linear = predict_map['linear_params'][3][0] * x_range + predict_map['linear_params'][3][1]
y_BA = predict_map['BA_params'][3][0] * (x_range ** 0.5)
y_BB = predict_map['BB_params'][3][1] * (x_range ** predict_map['BB_params'][3][0])
x_points = ['2019-01', '2019-02', '2019-03', '2019-04', '2019-05', '2019-06', '2019-07', '2019-08', '2019-09', '2019-10', '2019-11', '2019-12']
y_points = [selected_repo['201901'],selected_repo['201902'],selected_repo['201903'],
            selected_repo['201904'],selected_repo['201905'],selected_repo['201906'],
            selected_repo['201907'],selected_repo['201908'],selected_repo['201909'],
            selected_repo['201910'],selected_repo['201911'], selected_repo['201912']
            ]
x_expect = [12]
linear_predict = [predict_map['predict_list'][3]['linear_predict']]
BA_predict = [predict_map['predict_list'][3]['BA_predict']]
BB_predict = [predict_map['predict_list'][3]['BB_predict']]
plt.plot(x, y_points, 'co')
line1, = plt.plot(x_range, y_linear,'r--')
point1, = plt.plot(x_expect, linear_predict, 'r^')
line2, = plt.plot(x_range, y_BA,'g--')
point2, = plt.plot(x_expect, BA_predict, 'g^')
line3, = plt.plot(x_range, y_BB,'y--')
point3, = plt.plot(x_expect, BB_predict, 'y^')
plt.title("Azure/azure-libraries-for-java")
plt.xlabel("month")
plt.ylabel("repo's degree")
plt.legend([line1, line2, line3, point1, point2, point3],
           ["linear model", "BA model", "BB model", "linear model prediction", "BA model prediction", "BB model prediction"],
           loc="upper left")
plt.xticks(x, x_points, rotation='vertical')
plt.show()
