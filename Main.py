from Readrows import ReadRows
from Common import StaticCls
from Huawei_processing import Huawei
from NSN_processing import NSN
from ZTE_processing import ZTE
from Rpdb import Rpdb
import pandas as pd
import time
import fsspec    # Библиотека для pyinstaller


print('Пишем соседей из excel или Co-cite из rpdb?')
User_Choice = input('excel/rpdb: ')
if User_Choice.lower() == 'excel':
    data = pd.read_excel('C:\Python\File for open\Hand Over rpdb.xlsx')
    StaticCls.check_null_data(data)


if User_Choice.lower() == 'rpdb':
    Rpdb()
    data = Rpdb.df_cocite

# data = pd.read_excel('C:\Python\File for open\Hand Over rpdb.xlsx')
for index, row in data.iterrows():
    ReadRows(row)

# Создаю folder
StaticCls.create_folder(ReadRows.lst_row)


if len([i for i in ReadRows.lst_row if i.Source_vendor == 'Huawei']):
    Huawei()

if len([i for i in ReadRows.lst_row if i.Source_vendor == 'NSN']):
    NSN()

if len([i for i in ReadRows.lst_row if i.Source_vendor == 'ZTE']):
    ZTE()

print('Process completed successfully')
time.sleep(60)
