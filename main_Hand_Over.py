from readrows import ReadRows
from Huawei_processing import Huawei
from NSN_processing import NSN
from ZTE_processing import ZTE
from rpdb import rpdb
import pandas as pd
import fsspec    # Библиотека для pyinstaller


print('Пишем соседей из excel или Co-cite из rpdb?')
User_Choice = input('excel/rpdb: ')
if User_Choice.lower() == 'excel':
    data = pd.read_excel('C:\Python\File for open\Hand Over rpdb.xlsx')
    ReadRows.check_null_data(data)


if User_Choice.lower() == 'rpdb':
    rpdb()
    data = rpdb.df_cocite

# data = pd.read_excel('C:\Python\File for open\Hand Over rpdb.xlsx')
for index, row in data.iterrows():
    ReadRows(row)

# Название основной БС, путь для создания файлов
main_bs, path_folder = ReadRows.create_folder(ReadRows.lst_row)


if len([i for i in ReadRows.lst_row if i.Source_vendor == 'Huawei']):
    Huawei(main_bs, path_folder)

if len([i for i in ReadRows.lst_row if i.Source_vendor == 'NSN']):
    NSN(main_bs, path_folder)

if len([i for i in ReadRows.lst_row if i.Source_vendor == 'ZTE']):
    ZTE(main_bs, path_folder)

