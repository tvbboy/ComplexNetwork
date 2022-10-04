import websocket

# 注意：1. cookie要更新，2. token要更新
cookie = 'cna=lqkNGS+wCBUCAdvkkqVveGfp; login_aliyunid_pk=1432610791495765; aliyun_site=CN; aliyun_choice=CN; aliyun_lang=zh; idb_ticket=5eef7dbd-c33a-4827-b9c6-8b5bd9314056; _csrf=25cf07ca; _csrf_s=25cf07ca; login_aliyunid_csrf=2001323ea0e54104b803ad93fa64ab35; login_aliyunid="shuishan @ 1224904496484627"; login_aliyunid_ticket=Xdr5fkB9QnJ3ql8wFcjGzyaZBMVsWIpvLvFejqx953Afq1S1E2ml6JYlY4q9CyLstMknfiSc2GhOwNcWzj5bYLpKzKZ49O80KpzxYXWJ0WPzFXDzr7rhZ_Dua5Qyv2KMv85szYAdhP4$; login_aliyunid_sc=74u48x24xL7xCj1SQ9*cYL0T_GM6j755N7sioihe02YBTiMnByQYLGiIhJyEB8Sj56CirX_*9VBpfkTFdJTd570pfi0O5O2aEDMF1JGUziPrmJK*H1vT5ERPp2356A*R; tfstk=cwSABVqll7Vmv8vRLZUkbIk2BldOZ9kvsxOtXGsoXI9jpKnOiXshvxMuldJTi8C..; l=eBMUW6yIjXA48uKoBOfwhurza77OOIRf_uPzaNbMiOCPOB6B5PihW6Xvkpt6CnGVH6Y6R3SvCNIkB8LdwyCq1ZI32TTF6cMmndC..; isg=BPX1stVL-ySDhh2OOJIqR7hkBHGvcqmErl8aTHcanGy6ThRAP8ISVGGMmBL4CcE8'
token = "10771e98-eca0-4649-929a-b76e91987354"
sql = "SELECT *  FROM \n(\n    SELECT repo_id , COUNT( *) AS sum_ops  FROM year2017\n \tWHERE  repo_created_at > '2016-01-01 00:00:00' AND repo_created_at < '2016-04-01 00:00:00' \n    AND created_at > '2017-01-01 00:00:00' AND created_at < '2017-04-01 00:00:00'\n    AND type IN('WatchEvent','CreateEvent','PushEvent','IssuesEvent','PullRequestEvent','ForkEvent')\n\tGROUP BY repo_id \n)\nWHERE sum_ops > 100"
false = False
true = True

def wssRequest(sql, page):
    uri = "wss://dms.aliyun.com/ws/newwebsql/query"
    w1 = websocket.WebSocket()
    w1.connect(url=uri,header=["cookie:"+cookie])
    request = {"type":"execute","data":{"sql":sql,"dbId":12164148,"logic":"false","characterType":"","switchedHostPort":"","ignoreConfirm":"false","blobDirectDisplay":"false","binaryToHex":"false","sessionPersistence":"false","excutionAbort":"false", "page": page},"token":token}

    w1.send(str(request))
    print(f"> {request}")

    for i in range(3):
        response = w1.recv()
        print(f"< {response}")
    print(eval(response)["data"]["resultSet"]["result"])
    return eval(response)["data"]["resultSet"]["result"]

# res = wssRequest(sql)
# repos = []
# for i in range(len(res)):
#     repos.append(res[i]["C_1"])
# print(repos)

