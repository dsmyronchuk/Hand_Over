from rows_initialization import rpdb_cls
from Huawei_processing import Huawei
from NSN_processing import NSN
from ZTE_processing import ZTE
import pandas as pd


data = pd.read_excel('C:\Python\File for open\Hand Over rpdb.xlsx')
for index, row in data.iterrows():
    rpdb_cls(row)

# Название основной БС, путь для создания файлов
main_bs, path_folder = rpdb_cls.create_folder(rpdb_cls.lst_row)
# пройтись по всему изначалному списку
'''for i in rpdb_cls.lst_row:
    for j, v in i.__dict__.items():
        print(j, v, end=',')
    print()'''

#if len([i for i in rpdb_cls.lst_row if i.Source_vendor == 'Huawei']):
#    Huawei(main_bs, path_folder)

#if len([i for i in rpdb_cls.lst_row if i.Source_vendor == 'NSN']):
#    NSN(main_bs, path_folder)

if len([i for i in rpdb_cls.lst_row if i.Source_vendor == 'ZTE']):
    ZTE(main_bs, path_folder)

