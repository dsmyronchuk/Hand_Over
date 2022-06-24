from rows_initialization import rpdb_cls
from Huawei_processing import Huawei
import pandas as pd


data = pd.read_excel('C:\Python\File for open\Hand Over rpdb.xlsx')
for index, row in data.iterrows():
    rpdb_cls(row)

# пройтись по всему изначалному списку
'''for i in rpdb_cls.lst_row:
    for j, v in i.__dict__.items():
        print(j, v, end=',')
    print()'''

Hua = Huawei()
# пройти по списку хуа в классе хуа
'''for i in Hua.lst_huawei:
    for j, v in i.__dict__.items():
        print(j, v, end=',')
    print()'''

# пройтись по хуа 2G2G
'''for v, k in Hua.Huawei_from_3G.items():
    print(v, k)'''

print(Hua.Huawei_from_LTE)
