import numpy as np
import pandas as pd
import pyodbc
from jinja2 import Template


class CellObject:
    lst_source = []
    lst_target = []

    def __init__(self, row):
        self.BSC = row['BSC']
        self.CI = row['CI']
        self.SAC = row['SAC']
        self.LAC = row['LAC']
        if row['Channel'] not in (1700, 2900, 3676):
            self.RAC = int(row['RAC'])
        else:
            self.RAC = row['RAC']
        self.Site_Name = row['Site Name']
        self.BSIC = int(row['BSIC'])
        self.Channel = row['Channel']
        self.Azimuth = row['Azimuth']


class GetRpdbCell:
    lst_pre_df = []     # Итоговый лист, с сформированными соседними отношениями. Готов к созданию DataFrame
    df_cocite = ''      # переменная для хранения итогового DataFrame

    def __init__(self):
        self.dct_BCCH = {'GSM': range(1, 124),
                         'DCS': range(125, 950),
                         'UMTS': (10712, 10737, 10762),
                         'L09': (3676,),
                         'L18': (1700,),
                         'L26': (2900,)}
        self.connect_sql_rpdb()
        self.check_null_data()
        self.search_user_cell()
        self.search_target_cell()
        self.create_ho_table()
        self.lst_to_df()

    def connect_sql_rpdb(self):
        # обработка имени БС от юзера и подставка в шаблон для запроса
        user_bs = input('Введите имя БС: ').replace(' ', '_')
        t = Template(open('zte_template/rpdb_request.txt').read())
        render_request = t.render(user_bs=user_bs)

        # коннект к bd rpdb и обработка запроса
        connect_bd = pyodbc.connect('DRIVER={SQL Server};SERVER=172.20.215.71;DATABASE=rpdb;UID=center;PWD=center')
        # cursor = connect_bd.cursor()
        query = render_request
        self.rpdb_df = pd.read_sql(query, connect_bd)

    def check_null_data(self):
        for index, row in self.rpdb_df.iterrows():
            # Убираю возможные задвоения в азимуте (330°&330°)
            if '°' in row['Azimuth']:
                self.rpdb_df.loc[index, 'Azimuth'] = row['Azimuth'].split('&')[0]

            # Если в рпдб отсутвует bsic
            if np.isnan(row['BSIC']):
                self.rpdb_df.loc[index, 'BSIC'] = input(f'Введи Bsic для соты {row["CI"]}: ')

            # 3G Azimuth пустые ячейки ( без null )
            if row['Channel'] in (10712, 10737, 10762) and row['Azimuth'] == '':
                for index_j, row_j in self.rpdb_df.iterrows():
                    if row['SAC'] == row_j['CI']:
                        self.rpdb_df.loc[index, 'Azimuth'] = row_j['Azimuth']

    def search_user_cell(self):
        choice_standard = input('Укажите для каких стандартов нужно посчитать Co-cite \n'
                                'GSM, DCS, UMTS, L09, L18, L26 or all: ').replace(' ', '').split(',')

        if 'all' in choice_standard:
            for index, rpdb_row in self.rpdb_df.iterrows():                 # Создаю обьект класса CellObject
                CellObject.lst_source.append(CellObject(rpdb_row))          # и сразу добавляю его в lst_source
        else:
            for i in choice_standard:
                for index, rpdb_row in self.rpdb_df.iterrows():
                    if rpdb_row['Channel'] in self.dct_BCCH[i]:             # Создаю обьект класса CellObject
                        CellObject.lst_source.append(CellObject(rpdb_row))  # и сразу добавляю его в lst_source

    def search_target_cell(self):
        for index, rpdb_row in self.rpdb_df.iterrows():
            CellObject.lst_target.append(CellObject(rpdb_row))

    def create_ho_table(self):
        """Генерю итоговый список со всеми нужными строками"""
        for s in CellObject.lst_source:
            for t in CellObject.lst_target:
                source_part = []       # Source Cell > Target Cell
                target_part = []       # Target Cell > Source Cell

                if s.CI != t.CI:
                    for k, v in s.__dict__.items():
                        source_part.append(v)
                    for k, v in t.__dict__.items():
                        target_part.append(v)

                if len(source_part + target_part) > 0:
                    self.__class__.lst_pre_df.append(source_part + target_part)     # прямое соседство
                    self.__class__.lst_pre_df.append(target_part + source_part)     # сосед в обратную сторону

    def lst_to_df(self):
        self.__class__.df_cocite = pd.DataFrame(self.__class__.lst_pre_df, columns=[
         'BSC', 'Cell_ID', 'SAC', 'LAC', 'RAC', 'Site Name', 'BSIC', 'BCCH', 'Azimuth', 'Target BSC', 'Target Cell_',
         'Target SAC', 'Target LAC', 'Target RAC', 'Target Site ', 'Target BSIC', 'Target BCCH', 'Target Azimuth'])




