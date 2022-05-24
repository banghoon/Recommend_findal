import pymysql
import pandas as pd


db = pymysql.connect(host='dev.gooodcare.com',
                     port=3308,
                     user='iitpdev',
                     passwd='Fz8E}?=VM%|W',
                     db='iitp',
                     charset='utf8')


def get_sql(query, database=db):
    return pd.read_sql(query, database)


if __name__ == "__main__":
    print(get_sql("select * from tb_care"))
    print(get_sql("select * from tb_svc_locale"))
    print(get_sql("select * from tb_caregiver"))



'''
0             tb_care
1        tb_caregiver
2          tb_disease
3       tb_disease_en
4       tb_disease_ko
5           tb_review
6       tb_svc_locale
7  tb_svc_locale_item
'''