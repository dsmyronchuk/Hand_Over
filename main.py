from rows_initialization import primary
from Huawei_processing import Huawei
from NSN_processing import NSN
from ZTE_processing import ZTE
import pandas as pd
import fsspec    # Библиотека для pyinstaller


data = pd.read_excel('C:\Python\File for open\Hand Over rpdb.xlsx')
for index, row in data.iterrows():
    primary(row)

# Название основной БС, путь для создания файлов
main_bs, path_folder = primary.create_folder(primary.lst_row)


if len([i for i in primary.lst_row if i.Source_vendor == 'Huawei']):
    Huawei(main_bs, path_folder)

if len([i for i in primary.lst_row if i.Source_vendor == 'NSN']):
    NSN(main_bs, path_folder)

if len([i for i in primary.lst_row if i.Source_vendor == 'ZTE']):
    ZTE(main_bs, path_folder)

