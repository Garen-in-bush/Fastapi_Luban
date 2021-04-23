import pymysql
import json
import re
import os


class FastModelTran:
    def __init__(self, host, port, db, user, passwd):
        self.conn = pymysql.connect(
            host=host,
            port=port,
            db=db,
            user=user,
            passwd=passwd,
        )
        self.cursor = self.conn.cursor()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.mysql_type = json.load(open(os.path.join(current_dir, 'data/mysql.json')))

    def __del__(self):
        # 在使用完后请del实例
        self.conn.close()
        self.cursor.close()

    def get_table_structure(self, table_name):
        sql = "desc %s" % table_name
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def type_tans(self, col_type):
        return self.mysql_type.get(re.sub('[^a-zA-Z]+', '', col_type))

    def get_response_model(self, table_name_list, class_name_list, path):
        """
        :param table_name_list: 用来生成响应模型的表名列表
        :param class_name_list: 生成的响应模型类名列表
        :param path: 生成的py文件路径
        :return: py文件，包含所有待生成的响应模型
        """
        f = open(path, 'w', encoding='utf-8')
        f.write('from typing import List, Optional\nfrom pydantic import BaseModel\n\n\n')
        for i in range(len(table_name_list)):
            res = self.get_table_structure(table_name_list[i])  # 获取表结构信息
            f.write('class %s(BaseModel): \n' % class_name_list[i])
            for item in res:
                f.write('    %s: %s\n' % (item[0], self.type_tans(item[1])))
            f.write('\n    class Config:\n        orm_mode = True\n\n\n')
        f.close()

