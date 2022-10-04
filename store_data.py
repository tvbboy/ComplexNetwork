import time

from get_data import get_repo_repo_edge, get_repos
from mysql_connect.mysql_tool import execute_sql

date_list = ["201901", "201902", "201903", "201904", "201905", "201906", "201907", "201908", "201909", "201910", "201911", "201912", "202001"]

def store_repo():
    repo_list = get_repos()
    for repo in repo_list:
        sql = "INSERT INTO repo VALUES( " + str(repo['repo_id']) + ",\"" + str(repo['repo_name']) + "\")"
        execute_sql(sql)



def store_edge(date_month_start, date_month_end):
    repo_repo_map = get_repo_repo_edge(lamda1=1, date_month_start=date_month_start, date_month_end=date_month_end)
    print(repo_repo_map)
    for edge in repo_repo_map.values():
        sql = "INSERT INTO edge VALUES( " + str(edge['repo1']) + "," + str(edge['repo2']) + "," + str(edge['weight']) + "," + date_month_start + " )"
        execute_sql(sql)

store_repo()
start_time = time.time()
for i in range(0,12):
    store_edge(date_list[i], date_list[i+1])
end_time = time.time()
print('程序运行时间:%s秒' % (end_time - start_time))