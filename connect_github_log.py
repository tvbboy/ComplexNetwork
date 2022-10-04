import traceback
import pandas as pd
import sys
from sshtunnel import SSHTunnelForwarder
from clickhouse_driver import Client
# ----------------------------general final host------------------------
SERVER_IP = 0
SERVER_PORT = 1
USERNAME = 2
PASSWORD = 3
DBMS_USERNAME = 10
DBMS_PASSWORD = 11
USE_DATABASE = 12
# ----------------------------------Aliyun------------------------------
# Aliyun clickhouse GUI: https://signin.aliyun.com/1224904496484627.onaliyun.com/login.htm#/main
SERVER_IP_INTMED_1 = -10
SERVER_PORT_INTMED_1 = -11
USERNAME_INTMED_1 = -12
PASSWORD_INTMED_1 = -13
SERVER_IP_INTMED_2 = -20
SERVER_PORT_INTMED_2 = -21
USERNAME_INTMED_2 = -22
PASSWORD_INTMED_2 = -23
auth_settings_aliyun_intermediate_hosts = {
    SERVER_IP_INTMED_1: "106.15.200.87",
    SERVER_PORT_INTMED_1: 22,
    USERNAME_INTMED_1: "21xlabStudent",
    PASSWORD_INTMED_1: "21xlabStu", # replace '\' with '\\'.
    SERVER_IP_INTMED_2: "cc-uf6s6ckq946aiv4jy.ads.rds.aliyuncs.com",
    SERVER_PORT_INTMED_2: 3306,
    USERNAME_INTMED_2: None,
    PASSWORD_INTMED_2: None,
    SERVER_IP: '127.0.0.1',
    SERVER_PORT: 10022, # any available port.
    DBMS_USERNAME: 'xlab',
    DBMS_PASSWORD: 'Xlab2021!',
    USE_DATABASE: 'github_log'
}
class ConnDB():
    auth_settings_dict = auth_settings_aliyun_intermediate_hosts
    sql = None
    rs = None
    df_rs = None
    columns = None
    client = None
    def __init__(self, sql: str = None):
        self.sql = sql
        self.SERVER_IP_INTMED_1 = self.auth_settings_dict[SERVER_IP_INTMED_1]
        self.SERVER_PORT_INTMED_1 =self.auth_settings_dict[SERVER_PORT_INTMED_1]
        self.USERNAME_INTMED_1 = self.auth_settings_dict[USERNAME_INTMED_1]
        self.PASSWORD_INTMED_1 = self.auth_settings_dict[PASSWORD_INTMED_1]
        self.SERVER_IP_INTMED_2 = self.auth_settings_dict[SERVER_IP_INTMED_2]
        self.SERVER_PORT_INTMED_2 = self.auth_settings_dict[SERVER_PORT_INTMED_2]
        self.SERVER_IP = self.auth_settings_dict[SERVER_IP]
        self.SERVER_PORT = self.auth_settings_dict[SERVER_PORT]
        self.DBMS_USERNAME = self.auth_settings_dict[DBMS_USERNAME]
        self.DBMS_PASSWORD = self.auth_settings_dict[DBMS_PASSWORD]
        self.USE_DATABASE = self.auth_settings_dict[USE_DATABASE]
    def query_clickhouse(self):
        try:
            with SSHTunnelForwarder(
                       (self.SERVER_IP_INTMED_1, self.SERVER_PORT_INTMED_1),
                        ssh_username=self.USERNAME_INTMED_1,
                        ssh_password=self.PASSWORD_INTMED_1,
                        remote_bind_address=(self.SERVER_IP_INTMED_2, self.SERVER_PORT_INTMED_2),
                        local_bind_address=('0.0.0.0', self.SERVER_PORT)) as tunnel:
                        self.client = Client(host=self.SERVER_IP, port=tunnel.local_bind_port,
                                         user=self.DBMS_USERNAME,
                                         password=self.DBMS_PASSWORD,
                                         database=self.USE_DATABASE,
                                         send_receive_timeout=600)
                        self.rs = self.client.execute(self.sql)
        except BaseException as e:
            sql_log = self.sql[:500] + ("..." if self.sql[500:] else "")
            print("DB Exception happened while querying sql: \n\t{}\n".format(sql_log))
            print('Check the connection settings.\n' +
                  traceback.format_exc())
            sys.exit()
        self.df_rs = pd.DataFrame(self.rs, columns=self.columns)
        return pd.DataFrame(self.rs, columns=self.columns)


    def execute(self, sql=None, columns=None):
        self.sql = sql or self.sql
        self.columns = columns or self.columns
        self.query_clickhouse()
        return self.df_rs

if __name__ == '__main__':
    conndb = ConnDB()
    conndb.columns = ["actor_id", "actor_login", "repo_id", "repo_name",
                      "issue_id", "type", "action", "created_at", "created_date",
                      "pull_merged"]
    conndb.sql = "SELECT {select_columns} FROM github_log.year2020 LIMIT 10;".format(select_columns=', '.join(conndb.columns))
    conndb.execute()
    rs = conndb.df_rs
    print(rs.get("actor_id"))