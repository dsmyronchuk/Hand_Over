import pandas as pd
import datetime
import os
import numpy as np
from sqlalchemy import create_engine
import secret_info


class StaticCls:
    name_bs = ''
    path_folder = ''
    index_BSC_Huawei = {'383': '703', '384': '713', '395': '723', '15290': '733', '15394': '743', '15395': '753',
                        '259': '903', '359': '913', '381': '923', '382': '933', '62233': '210', '62236': '220',
                        '62526': '230', '22207': '503', '22279': '513', '402': '523', '22349': '533', '20705': '543',
                        '20704': '553', '20703': '563', '61602': '112', '61526': '102', '22461': '1503',
                        '22623': '1513', '368': '1543', '366': '1703', '15396': '1723', '360': '1903', '365': '1923',
                        '356': '1862', '22178': '1872', '260': '1340', '22832': '1380', '377': '1608', '66844': '608',
                        '66139': '618', '66140': '628', '378': '1518', '66619': '991', '66620': '992', '66621': '993'}

    @staticmethod
    def check_append_dict(input_dict, key, value):
        if key in input_dict:
            input_dict[key].append(value)
        else:
            input_dict[key] = [value]

    @staticmethod
    def connect_sql():
        sqlbd_vf_work = secret_info.vf_bd     # Коннект к БД
        connsqlbd_vf_work = create_engine(sqlbd_vf_work)
        return connsqlbd_vf_work

    @staticmethod
    def get_lst_3column(path, column_1, column_2, column_3):
        sql_table = pd.read_sql(path, StaticCls.connect_sql())
        if column_1 == 'fdn':
            sql_table[column_1] = sql_table[column_1].map(lambda x: str(x.split(",")[0].split("=")[1]))
            sql_table[column_1] = sql_table[column_1].map(StaticCls.index_BSC_Huawei).fillna(sql_table[column_1])
        sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}',
                                                   axis=1)
        out_lst = [i for i in sql_table['correct_key']]
        return out_lst

    # функция для коннекта к SQL и вывода словаря ключ: 3 колонки; значение: 4 колонка
    @staticmethod
    def get_dct_4column(path, column_1, column_2, column_3, column_4, type_dct):
        sql_table = pd.read_sql(path, StaticCls.connect_sql())

        if type_dct == '3key_1value':       # Используется в Huawei
            if column_1 == 'fdn':
                sql_table[column_1] = sql_table[column_1].map(lambda x: str(x.split(",")[0].split("=")[1]))
                sql_table[column_1] = sql_table[column_1].map(StaticCls.index_BSC_Huawei).fillna(sql_table[column_1])
            sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}',
                                                       axis=1)
            out_dict = {row['correct_key']: row[column_4] for index, row in sql_table.iterrows()}
            return out_dict     # пример - {'BSC_CI_LAC': 'Ext_ID'}

        if type_dct == '2key_2value':      # Используется в ZTE
            sql_table = pd.read_sql(path, StaticCls.connect_sql())
            sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}', axis=1)
            out_dict = {row['correct_key']: [row[column_3], row[column_4]] for index, row in sql_table.iterrows()}
            return out_dict  # пример - {'BSC_CI': ['BTS_ID', 'Gsm_Cell_ID'}

    # Сортировка Команд ( Используется в ZTE_processing, Huawei_Processing )
    @staticmethod
    def command_sort(original_dct, lst_command):
        new_dct = {}
        for k in sorted(original_dct):              # создаю отсортированый словарь {ключ:пустой список}
            new_dct[k] = []

            for ls in lst_command:                  # прохожусь по каждой команде из списка
                for v in original_dct[k]:           # прохожусь по старому словарю в новом порядке
                    if ls in v[1]:                  # если команда из списка есть у данного ключа словаря
                        new_dct[k].append(v)        # добавляю в новый словарь

        # словарь с отсортированными командами переделываю в DataFrame
        def dct_to_pd():
            nonlocal new_dct
            refresh_dct = {k: list(zip(*v)) for k, v in new_dct.items()}
            df = pd.DataFrame.from_dict(refresh_dct, orient='index')
            df = df.apply(pd.Series.explode)

            if len(df.columns) == 2:    # для Huawei
                df.columns = ['HandOver Type', 'Command']
            if len(df.columns) == 3:    # для ZTE
                df.columns = ['HandOver Type', 'Command', 'Source>>>Target']
            return df

        return dct_to_pd()

    # функция для подсчета максимально встречаемого имени БС и создания пути к папке
    @staticmethod
    def create_folder(lst_obj_ho):
        # Создание списка из всех имен БС
        lst_name = []
        for i in lst_obj_ho:
            lst_name.append(i.Source_Site_Name)
            lst_name.append(i.Target_Site_Name)

        # Выбор максимально встречаемой БС
        max_amount = 0
        name_bs = ''
        for i in set(lst_name):
            if lst_name.count(i) > max_amount:
                max_amount = lst_name.count(i)
                name_bs = i[:11]

        # создание пути
        path_folder = f'C://Python/Hand Over/{name_bs}___{datetime.datetime.now().date()}'
        os.mkdir(path_folder)

        StaticCls.name_bs = name_bs
        StaticCls.path_folder = path_folder

    # функция для проверки на пустые значание df
    @staticmethod
    def check_null_data(df):
        """Проверка excel на пустые значения. Если такие имеются, скрипт остановится"""
        for index, row in df.iterrows():

            # Source/Target BSC, LAC, BSIC, BCCH
            for ind in (0, 3, 6, 7, 9, 12, 15, 16):
                if np.isnan(ind):
                    raise ValueError('Обраружены пустые ячейки в входных данных')

            # Source RAC
            if row[4] not in (1700, 2900, 3676) and np.isnan(row[16]):
                raise ValueError('Обраружены пустые ячейки в входных данных')

            # Source LAC
            if row[16] not in (1700, 2900, 3676) and np.isnan(row[16]):
                raise ValueError('Обраружены пустые ячейки в входных данных')
