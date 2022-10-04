from clickHouseConnect import wssRequest

weight_map = {
    "WatchEvent": 0,
    "ForkEvent": 0,
    "GollumEvent": 0,
    "DeleteEvent": 0,
    "CommitCommentEvent": 1,
    "CreateEvent": 0,
    "MemberEvent": 0,
    "ReleaseEvent": 0,
    "PublicEvent": 0,
    "IssueCommentEvent": 1,
    "IssuesEvent": 2,
    "PullRequestReviewCommentEvent": 3,
    "PullRequestEvent": 4,
    "PushEvent": 5
}

def get_repos():
    sql = "SELECT repo_id, repo_name  \n    FROM year2019\n    WHERE org_login = 'Azure'\n    GROUP BY repo_id , repo_name \n"
    res = wssRequest(sql, 1)
    repo_list = []
    # repo_list = [
    #   {
    #       "repo_id": 123321,
    #       "repo_name": "Azure/xxxx"
    #   }
    # ]
    for i in range(0, len(res)):
        repo_id = res[i]["C_1"]
        repo_name = res[i]["C_2"]
        new_repo = {
            "repo_id": repo_id,
            "repo_name": repo_name
        }
        repo_list.append(new_repo)
    print(repo_list)
    return repo_list

def get_users():
    sql = ""

def get_repo_repo_edge(lamda1, date_month_start, date_month_end):
    # 201901 -> 2019-01-01
    date_start = date_month_start[0:4] + "-" + date_month_start[4:6] + "-" + "01"
    date_end = date_month_end[0:4] + "-" + date_month_end[4:6] + "-" + "01"
    # 获取org下所有user
    # 第一个超参：用户和目标仓库的粘合度，用户参与了该网络内百分之几的repo，表现用户对该网络内repo的重要程度。只考虑重要程度达到一定阈值的用户操作。
    sql1 = "SELECT actor_id  ,COUNT(id) AS ops  \n    FROM year2019\n    WHERE org_login = 'Azure' AND created_at  > '" + date_start + " 00:00:00' AND created_at  < '" + date_end + " 00:00:00'\n    GROUP BY actor_id  \n    HAVING COUNT( DISTINCT( repo_id))  > " + str(lamda1) +  "\n    -- 与user相关的repo数大于总repo数的百分之1"
    user_list = []
    repo_repo_map = {}
    cur_page = 0
    res = []
    while cur_page == 0 or len(res) >= 3000:
        cur_page += 1
        res = wssRequest(sql1, cur_page)
        for i in range(0, len(res)):
            user_list.append(res[i]['C_1'])
    # 获取user -> repo操作
    for user_id in user_list:
        sql2 = "SELECT actor_id, repo_id, type   FROM year2019 \nWHERE org_login = 'Azure' AND created_at  > '" + date_start + " 00:00:00' AND created_at  < '" + date_end + " 00:00:00' AND actor_id = " + user_id
        cur_page = 0
        while cur_page == 0 or len(res) >= 3000:
            cur_page += 1
            res = wssRequest(sql2, cur_page)
        # repo-repo_map: {
        #   "${repo1_id}-${repo2_id}": {
        #       "repo1": "123",
        #       "repo2": "321",
        #       "weight": 1
        #   }
        # }
            for i in range(0, len(res)):
                repo1_id = res[i]["C_2"]
                new_weight = weight_map[res[i]["C_3"]]
                for j in range(0, len(res)):
                    repo2_id = res[j]["C_2"]
                    if(repo1_id == repo2_id):
                        break
                    if(repo1_id > repo2_id):
                        # swap
                        temp = repo2_id
                        repo2_id = repo1_id
                        repo1_id = temp
                    key = repo1_id + "-" +repo2_id
                    # update map
                    if weight_map[res[j]["C_3"]] == 0 or weight_map[res[i]["C_3"]] == 0:
                        new_weight = 0
                    else:
                        new_weight += weight_map[res[j]["C_3"]]
                    new_weight = new_weight / 2
                    add_weight = new_weight
                    if repo_repo_map.get(key) is not None:
                        add_weight = repo_repo_map[key]["weight"] + new_weight
                    repo_repo_map[key] = {
                        "repo1": repo1_id,
                        "repo2": repo2_id,
                        "weight": add_weight
                    }
    print(repo_repo_map)
    print(len(repo_repo_map))
    return repo_repo_map