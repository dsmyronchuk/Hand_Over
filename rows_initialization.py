from sqlalchemy import create_engine
import pandas as pd


class rpdb_cls:
    lst_row = []
    amount_Huawei = 0
    amount_NSN = 0
    amount_ZTE = 0

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
        self.gi = self.ncc(self.Target_BSIC, self.Target_BCCH)
        self.Source_bcc = str(self.Source_BSIC)[-1]
        self.Target_bcc = str(self.Target_BSIC)[-1]
        if self.Source_BCCH in (1700, 2900, 3676):
            self.Source_ENB = str(self.Source_Cell_ID)[:6]
            self.Source_ENB_CI = str(self.Source_Cell_ID)[-2:]
        if self.Target_BCCH in (1700, 2900, 3676):
            self.Target_ENB = str(self.Target_Cell_ID)[:6]
            self.Target_ENB_CI = str(self.Target_Cell_ID)[-2:]

        self.Source_vendor = self.check_vendor(self.Source_BSC)
        self.Target_vendor = self.check_vendor(self.Target_BSC)
        self.Type_ho = self.check_type_ho()
        self.Source_BSC__Target_CI_LAC = f'{self.Source_BSC}_{self.Target_Cell_ID}_{self.Target_LAC}'

        self.__class__.lst_row.append(self)

    def check_vendor(self, bsc):
        if bsc in (252, 322, 338, 358, 432, 452, 732, 822, 832, 922, 1252, 1322, 1432):
            self.__class__.amount_ZTE += 1
            return 'ZTE'

        elif bsc in (210, 220, 230, 1340, 1380, 503, 513, 523, 533, 543, 553,
                     563, 703, 713, 723, 733, 743, 753, 903, 913, 923, 933, 1503,
                     1513, 1543, 1703, 1723, 1903, 1923, 1862, 1872, 112, 102, 528):
            self.__class__.amount_Huawei += 1
            return 'Huawei'

        elif bsc in (801, 811, 821, 831, 841, 851, 861, 871, 881, 891, 901, 911, 941, 921, 931,
                     1801, 1811, 1821, 1831, 1901, 1911, 1921, 711, 731, 741, 991, 992, 993):
            self.__class__.amount_NSN += 1
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
       # sqlbd_vf_work = 'mysql+pymysql://Dmyronchuk:NoMercy2017!@172.20.186.42:3306'  # БД Войтыка
        sqlbd_vf_work = 'mysql+pymysql://root:NoizeMc2011!@localhost:3306/vf_work'     # Локальная БД на пк
        connsqlbd_vf_work = create_engine(sqlbd_vf_work)
        return connsqlbd_vf_work

    @staticmethod
    def ncc(bsic, bcch):
        if bcch < 950:
            if len(str(bsic)) == 1:
                return 0
            if len(str(bsic)) == 2:
                return str(bsic)[0]

    # функция для коннекта к БД и вывода списка строк BSC, Target Cell ID, Target LAC
    @staticmethod
    def ext_sql_lst(path, column_1, column_2, column_3):
        sql_table = pd.read_sql(path, rpdb_cls.connect_sql())
        sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}'
                                                   , axis=1)
        out_lst = [i for i in sql_table['correct_key']]
        return out_lst  # данные в виде 'SourceBSC_CI_LAC'

    # функция для коннекта к БД и вывода словаря ключ: BSC, Target Cell ID, Target LAC; значение: index/name
    @staticmethod
    def ext_sql_dict(path, column_1, column_2, column_3, column_4):
        sql_table = pd.read_sql(path, rpdb_cls.connect_sql())
        sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}'
                                                   , axis=1)
        out_dict = {row['correct_key']: row[column_4] for index, row in sql_table.iterrows()}
        return out_dict  # ключи в виде 'SourceBSC_CI_LAC'
