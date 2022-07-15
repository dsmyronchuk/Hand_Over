from sqlalchemy import create_engine
import pandas as pd
import datetime
import os
import account_info


class primary:
    lst_row = []
    duplicate_check = []
    path_directory = ''
    index_BSC_Huawei = {'383': '703', '384': '713', '395': '723', '15290': '733', '15394': '743', '15395': '753',
                        '259': '903', '359': '913', '381': '923', '382': '933', '62233': '210', '62236': '220',
                        '62526': '230', '22207': '503', '22279': '513', '402': '523', '22349': '533', '20705': '543',
                        '20704': '553', '20703': '563', '61602': '112', '61526': '102', '22461': '1503',
                        '22623': '1513', '368': '1543', '366': '1703', '15396': '1723', '360': '1903', '365': '1923',
                        '356': '1862', '22178': '1872', '260': '1340', '22832': '1380', '377': '1608'}

    def __init__(self, row):
        self.Source_BSC = row[0]
        self.Source_Cell_ID = row[1]
        self.Source_SAC = row[2]
        self.Source_LAC = row[3]
        if row[7] not in (1700, 2900, 3676):
            self.Source_RAC = int(row[4])
        self.Source_Site_Name = row[5]
        self.Source_BSIC = int(row[6])
        self.Source_BCCH = row[7]
        self.Source_Azimuth = row[8]
        self.Target_BSC = row[9]
        self.Target_Cell_ID = row[10]
        self.Target_SAC = row[11]
        self.Target_LAC = row[12]
        if row[16] not in (1700, 2900, 3676):
            self.Target_RAC = int(row[13])
        self.Target_Site_Name = row[14]
        self.Target_BSIC = int(row[15])
        self.Target_BCCH = row[16]
        self.Target_Azimuth = row[17]
        self.Date_Add = row[18]
        self.User = row[19]
        self.Source_full_name = self.used_name_bs(self.Source_Azimuth, self.Source_Site_Name, self.Source_BCCH)
        self.Target_full_name = self.used_name_bs(self.Target_Azimuth, self.Target_Site_Name, self.Target_BCCH)
        self.Source_ncc = self.ncc(self.Source_BSIC, self.Source_BCCH)
        self.Target_ncc = self.ncc(self.Target_BSIC, self.Target_BCCH)
        self.Source_bcc = str(self.Source_BSIC)[-1]
        self.Target_bcc = str(self.Target_BSIC)[-1]
        if self.Source_BCCH in (1700, 2900, 3676):
            self.Source_ENB = str(self.Source_Cell_ID)[:6]
            self.Source_ENB_CI = str(self.Source_Cell_ID)[-2:]
            self.Source_CI_256 = (int(str(self.Source_Cell_ID)[:6]) * 256) + int(str(self.Source_Cell_ID)[-2:])
        if self.Target_BCCH in (1700, 2900, 3676):
            self.Target_ENB = str(self.Target_Cell_ID)[:6]
            self.Target_ENB_CI = str(self.Target_Cell_ID)[-2:]
            self.Target_CI_256 = (int(str(self.Target_Cell_ID)[:6]) * 256) + int(str(self.Target_Cell_ID)[-2:])

        self.Source_vendor = self.check_vendor(self.Source_BSC)
        self.Target_vendor = self.check_vendor(self.Target_BSC)
        self.Type_ho = self.check_type_ho()
        self.Source_BSC__Target_CI_LAC = f'{self.Source_BSC}_{self.Target_Cell_ID}_{self.Target_LAC}'

        # Проверка на дубликаты и добавление в список обьектов
        main_values = [self.Source_BSC, self.Source_Cell_ID, self.Source_LAC,
                       self.Target_BSC, self.Target_Cell_ID, self.Target_LAC]
        if main_values not in self.__class__.duplicate_check:
            self.__class__.lst_row.append(self)
            self.__class__.duplicate_check.append(main_values)

    def check_vendor(self, bsc):
        if bsc in (252, 322, 338, 358, 432, 452, 732, 822, 832, 922, 1252, 1322, 1432):
            return 'ZTE'

        elif bsc in (210, 220, 230, 1340, 1380, 503, 513, 523, 533, 543, 553, 1608,
                     563, 703, 713, 723, 733, 743, 753, 903, 913, 923, 933, 1503,
                     1513, 1543, 1703, 1723, 1903, 1923, 1862, 1872, 112, 102, 528,):
            return 'Huawei'

        elif bsc in (801, 811, 821, 831, 841, 851, 861, 871, 881, 891, 901, 911, 941, 921, 931,
                     1801, 1811, 1821, 1831, 1901, 1911, 1921, 711, 731, 741, 991, 992, 993):
            return 'NSN'

    def check_type_ho(self):
        if self.Source_BCCH < 950 and self.Target_BCCH < 950:
            return '2G>2G'
        elif self.Source_BCCH < 950 and self.Target_BCCH in (10712, 10737, 10762, 10662):
            return '2G>3G'
        elif self.Source_BCCH in (10712, 10737, 10762, 10662) and self.Target_BCCH < 950:
            return '3G>2G'
        elif self.Source_BCCH in (10712, 10737, 10762, 10662) and self.Target_BCCH in (10712, 10737, 10762, 10662):
            return '3G>3G'
        elif self.Source_BCCH in (1700, 2900, 3676) and self.Target_BCCH in (1700, 2900, 3676):
            return 'LTE>LTE'
        elif self.Source_BCCH in (1700, 2900, 3676) and self.Target_BCCH < 950:
            return 'LTE>2G'
        elif self.Source_BCCH < 950 and self.Target_BCCH in (1700, 2900, 3676):
            return '2G>LTE'
        elif self.Source_BCCH in (1700, 2900, 3676) and self.Target_BCCH in (10712, 10737, 10762, 10662):
            return 'LTE>3G'
        elif self.Source_BCCH in (10712, 10737, 10762, 10662) and self.Target_BCCH in (1700, 2900, 3676):
            return '3G>LTE'

    @staticmethod
    def used_name_bs(rpdb_azimuth, rpdb_name, rpdb_bcch):
        def azimuth():
            azz = rpdb_azimuth[:-1]
            if len(azz) == 2 or len(azz) == 1:
                azz = azz.zfill(3)
            if azz == 'indoor':
                azz = 'ind'
            return azz

        def u1u2u3(bcch):
            if bcch == 10712:
                return 'U1'
            if bcch == 10737:
                return 'U2'
            if bcch == 10762:
                return 'U3'
            if bcch == 10662:
                return 'U4'

        def l09l18l26(bcch):
            if bcch == 1700:
                return 'L18'
            if bcch == 3676:
                return 'L09'
            if bcch == 2900:
                return 'L26'

        if rpdb_bcch < 950:
            return f'{rpdb_name[:11]}_{azimuth()}_{rpdb_name[-1]}'
        elif rpdb_bcch in (10712, 10737, 10762, 10662):
            return f'{rpdb_name[:11]}_{azimuth()}_{u1u2u3(rpdb_bcch)}'
        elif rpdb_bcch in (1700, 2900, 3676):
            return f'{rpdb_name[:11]}_{azimuth()}_{l09l18l26(rpdb_bcch)}'

    @staticmethod
    def check_append_dict(input_dict, key, value):
        if key in input_dict:
            input_dict[key].append(value)
        else:
            input_dict[key] = [value]

    @staticmethod
    def connect_sql():
       # sqlbd_vf_work = account_info.vf_vd  # БД Войтыка
        sqlbd_vf_work = account_info.local_bd     # Локальная БД на пк
        connsqlbd_vf_work = create_engine(sqlbd_vf_work)
        return connsqlbd_vf_work

    @staticmethod
    def ncc(bsic, bcch):
        if bcch < 950:
            if len(str(bsic)) == 1:
                return 0
            if len(str(bsic)) == 2:
                return str(bsic)[0]

    @staticmethod
    def get_lst_3column(path, column_1, column_2, column_3):
        sql_table = pd.read_sql(path, primary.connect_sql())
        if column_1 == 'fdn':
            sql_table[column_1] = sql_table[column_1].map(lambda x: str(x.split(",")[0].split("=")[1]))
            sql_table[column_1] = sql_table[column_1].map(primary.index_BSC_Huawei).fillna(sql_table[column_1])
        sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}',
                                                   axis=1)
        out_lst = [i for i in sql_table['correct_key']]
        return out_lst

    # функция для коннекта к SQL и вывода словаря ключ: 3 колонки; значение: 4 колонка
    @staticmethod
    def get_dct_4column(path, column_1, column_2, column_3, column_4, type):
        sql_table = pd.read_sql(path, primary.connect_sql())

        if type == '3key_1value':       # Используется в Huawei
            if column_1 == 'fdn':
                sql_table[column_1] = sql_table[column_1].map(lambda x: str(x.split(",")[0].split("=")[1]))
                sql_table[column_1] = sql_table[column_1].map(primary.index_BSC_Huawei).fillna(sql_table[column_1])
            sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}',
                                                       axis=1)
            out_dict = {row['correct_key']: row[column_4] for index, row in sql_table.iterrows()}
            return out_dict     # пример - {'BSC_CI_LAC': 'Ext_ID'}

        if type == '2key_2value':      # Используется в ZTE
            sql_table = pd.read_sql(path, primary.connect_sql())
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

        # возвращаю кортеж с самой встречаемой БС и путем к папке
        return name_bs, path_folder




