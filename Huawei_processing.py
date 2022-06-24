from rows_initialization import rpdb_cls
import pandas as pd


class Huawei:
    lst_huawei = []
    index_BSC = {'383': '703', '384': '713', '395': '723', '15290': '733', '15394': '743', '15395': '753',
                 '259': '903', '359': '913', '381': '923', '382': '933', '62233': '210', '62236': '220',
                 '62526': '230', '22207': '503', '22279': '513', '402': '523', '22349': '533', '20705': '543',
                 '20704': '553', '20703': '563', '61602': '112', '61526': '102', '22461': '1503',
                 '22623': '1513', '368': '1543', '366': '1703', '15396': '1723', '360': '1903', '365': '1923',
                 '356': '1862', '22178': '1872', '260': '1340', '22832': '1380'}

    Huawei_from_2G = dict()    # Словарь с 2же командами
    Huawei_from_3G = dict()    # Словарь с 3же командами
    Huawei_from_LTE = dict()   # Словарь с LTE командами

    def __init__(self):
        self.search_huawei()

        # выгрузка имён из oss 2G,3G
        path_2g_oss_name = 'SELECT fdn, CI, LAC, CELLNAME FROM `parse_huawei`.`GSM_BSC6910GSMGCELL`'
        path_3g_oss_name = 'SELECT LOGICRNCID, CELLID, LAC, CELLNAME FROM`parse_huawei`.`UMTS_BSC6910UMTSUCELL`'
        path_lte_oss_name = 'SELECT ENODEBFUNCTIONNAME, CELLID, DLEARFCN, CELLNAME FROM`parse_huawei`.`BBU_BTS3900CELL`'
        self.oss_name_2g_dct = self.get_dct_4column(path_2g_oss_name, 'fdn', 'CI', 'LAC', 'CELLNAME')
        self.oss_name_3g_dct = self.get_dct_4column(path_3g_oss_name, 'LOGICRNCID', 'CELLID', 'LAC', 'CELLNAME')
        self.oss_name_lte_dct = self.get_dct_4column(path_lte_oss_name, 'ENODEBFUNCTIONNAME', 'CELLID', 'DLEARFCN',
                                                     'CELLNAME')

        # выгрузка NE имен из oss и создание имени self.Name_NE
        path_lte_oss_name = 'SELECT NAME FROM`parse_huawei`.`BBU_BTS3900NE`'
        self.oss_ne_name_lte_lst = self.get_lst_1column(path_lte_oss_name)
        self.get_ne_name()

        # обработка таблицы EXT 2G2G
        path_2g2g_ext = 'SELECT fdn, CI, LAC FROM `parse_huawei`.`GSM_BSC6910GSMGEXT2GCELL`'
        self.ext_2G2G_lst = self.get_lst_3column(path_2g2g_ext, 'fdn', 'CI', 'LAC')

        # обработка таблицы EXT 2G3G
        path_2g3g_ext = 'SELECT fdn, CI, LAC, EXT3GCELLNAME FROM `parse_huawei`.`GSM_BSC6910GSMGEXT3GCELL`'
        self.ext_2G3G_dict = self.get_dct_4column(path_2g3g_ext, 'fdn', 'CI', 'LAC', 'EXT3GCELLNAME')

        # обработка таблицы EXT 3G2G
        path_3g2g_ext = 'SELECT LOGICRNCID, CID, LAC, GSMCELLINDEX FROM `parse_huawei`.`UMTS_BSC6910UMTSGSMCELL`'
        self.ext_3G2G_dict = self.get_dct_4column(path_3g2g_ext, 'LOGICRNCID', 'CID', 'LAC', 'GSMCELLINDEX')

        # обработка таблицы EXT 3G3G
        path_3g3g_ext = 'SELECT LOGICRNCID, CELLID, LAC FROM `parse_huawei`.`UMTS_BSC6910UMTSNRNCCELL`'
        self.ext_3G3G_lst = self.get_lst_3column(path_3g3g_ext, 'LOGICRNCID', 'CELLID', 'LAC')

        # обработка таблицы EXT LTELTE
        path_ltelte_ext = 'SELECT ENODEBFUNCTIONNAME, ENODEBID, CELLID FROM ' \
                          '`parse_huawei`.`BBU_BTS3900EUTRANEXTERNALCELL`'
        self.ext_ltelte_lst = self.get_lst_3column(path_ltelte_ext, 'ENODEBFUNCTIONNAME', 'ENODEBID', 'CELLID')

        # обработка таблицы EXT LTE3G
        path_lte3g_ext = 'SELECT ENODEBFUNCTIONNAME, CELLID, LAC FROM `parse_huawei`.`BBU_BTS3900UTRANEXTERNALCELL`'
        self.ext_lte3g_lst = self.get_lst_3column(path_lte3g_ext, 'ENODEBFUNCTIONNAME', 'CELLID', 'LAC')

        # переменные для хранения EXT и ARFCN LTE<>2G
        self.ext_lte2g = []
        self.arfcn_lte2g = []
        self.ext_2glte = []

        self.name_correction_all_bs()

        self.create_ho_2g2g()
        self.create_ho_2g3g()
        self.create_ho_3g3g()
        self.create_ho_3g2g()
        self.create_ho_ltelte()
        self.create_ho_lte2g()
        self.create_ho_2glte()
        self.create_ho_lte3g()

        # сортирую команды в нужном формате для записи в xlsx
        self.__class__.Huawei_from_LTE = self.command_sort(self.__class__.Huawei_from_LTE,
                                                           ['ADD EUTRANEXTERNALCELL', 'ADD EUTRANINTRAFREQNCELL',
                                                            'ADD EUTRANINTERFREQNCELL', 'ADD GERANEXTERNALCELL',
                                                            'ADD GERANNFREQGROUPARFCN', 'ADD GERANNCELL',
                                                            'ADD UTRANEXTERNALCELL', 'ADD UTRANNCELL'])
        self.__class__.Huawei_from_2G = self.command_sort(self.Huawei_from_2G,
                                                          ['ADD GEXT2GCELL', 'ADD G2GNCELL', 'ADD GEXT3GCELL',
                                                           'ADD G3GNCELL', 'ADD GEXTLTECELL', 'ADD GLTENCEL'])
        self.__class__.Huawei_from_3G = self.command_sort(self.Huawei_from_3G,
                                                          ['ADD UEXT3GCELL', 'ADD UINTRAFREQNCELL',
                                                           'ADD UINTERFREQNCELL', 'ADD UEXT2GCELL', 'ADD U2GNCELL'
                                                           'ADD U2GNCELL'])

    def search_huawei(self):
        for i in rpdb_cls.lst_row:
            if i.Source_vendor == 'Huawei':
                self.__class__.lst_huawei.append(i)

    # функция для коннекта к SQL и вывода списка из 3х строк (по трём колонкам)
    @staticmethod
    def get_lst_3column(path, column_1, column_2, column_3):
        sql_table = pd.read_sql(path, rpdb_cls.connect_sql())
        if column_1 == 'fdn':
            sql_table[column_1] = sql_table[column_1].map(lambda x: str(x.split(",")[0].split("=")[1]))
            sql_table[column_1] = sql_table[column_1].map(Huawei.index_BSC).fillna(sql_table[column_1])
        sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}',
                                                   axis=1)
        out_lst = [i for i in sql_table['correct_key']]
        return out_lst

    # функция для коннекта к SQL и вывода словаря ключ: 3 колонки; значение: 4 колонка
    @staticmethod
    def get_dct_4column(path, column_1, column_2, column_3, column_4):
        sql_table = pd.read_sql(path, rpdb_cls.connect_sql())
        if column_1 == 'fdn':
            sql_table[column_1] = sql_table[column_1].map(lambda x: str(x.split(",")[0].split("=")[1]))
            sql_table[column_1] = sql_table[column_1].map(Huawei.index_BSC).fillna(sql_table[column_1])
        sql_table['correct_key'] = sql_table.apply(lambda row: f'{row[column_1]}_{row[column_2]}_{row[column_3]}',
                                                   axis=1)
        out_dict = {row['correct_key']: row[column_4] for index, row in sql_table.iterrows()}
        return out_dict

    # функция для коннекта к SQL и вывода списка из одной колонки
    @staticmethod
    def get_lst_1column(path):
        sql_table = pd.read_sql(path, rpdb_cls.connect_sql())
        out_lst = [row for row in sql_table['NAME']]
        return out_lst

    def get_ne_name(self):
        for i in self.__class__.lst_huawei:
            for j in self.oss_ne_name_lte_lst:
                if i.Source_Site_Name[:11] == j[:11]:
                    i.NE_Name = j

    # корректировка имени по OSS ( если сота есть в OSS - перезаписать имя из OSS )
    def name_correction_all_bs(self):
        for i in Huawei.lst_huawei:
            if i.Source_BCCH < 950 and f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}' in self.oss_name_2g_dct:
                i.Source_full_name = self.oss_name_2g_dct[f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}']

            if i.Source_BCCH in (10712, 10737, 10762, 10662) and f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}' \
                    in self.oss_name_3g_dct:
                i.Source_full_name = self.oss_name_3g_dct[f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}']

            if i.Source_BCCH in (1700, 3676, 2900) and f'{i.Source_Site_Name}_{i.Source_ENB_CI}_{i.Source_BCCH}'\
                    in self.oss_name_lte_dct:
                i.Source_full_name = self.oss_name_lte_dct[f'{i.Source_Site_Name}_{i.Source_ENB_CI}_{i.Source_BCCH}']

            if i.Target_BCCH < 950 and f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}' in self.oss_name_2g_dct:
                i.Target_full_name = self.oss_name_2g_dct[f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}']

            if i.Target_BCCH in (10712, 10737, 10762, 10662) and f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}' \
                    in self.oss_name_3g_dct:
                i.Target_full_name = self.oss_name_3g_dct[f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}']

            if i.Target_BCCH in (1700, 3676, 2900) and f'{i.Target_Site_Name}_{i.Target_ENB_CI}_{i.Target_BCCH}'\
                    in self.oss_name_lte_dct:
                i.Target_full_name = self.oss_name_lte_dct[f'{i.Target_Site_Name}_{i.Target_ENB_CI}_{i.Target_BCCH}']

    # Сортировка Команд
    @staticmethod
    def command_sort(original_dct, lst_command):
        new_dct = {}
        for k in sorted(original_dct):              # создаю отсортированый словарь {ключ:пустой список}
            new_dct[k] = []

            for ls in lst_command:                  # прохожусь по каждой команде из списка
                for v in original_dct[k]:           # прохожусь по старому словарю в новом порядке
                    if ls in v[0]:                  # если команда из списка есть у данного ключа словаря
                        new_dct[k].append(v)        # добавляю в новый словарь

        return new_dct

    # Функции вызовов генерации комманд
    def create_ho_2g2g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '2G>2G':
                if i.Source_BSC__Target_CI_LAC not in self.ext_2G2G_lst:
                    command_ext_2g2g = f'ADD GEXT2GCELL: EXT2GCELLNAME="{i.Target_full_name}",MCC="255",MNC="01",LAC=' \
                                       f'{i.Target_LAC},CI={i.Target_Cell_ID},BCCH={i.Target_BCCH},NCC={i.Target_ncc}' \
                                       f',BCC={i.Target_bcc},RA={int(i.Target_RAC)};'
                    self.ext_2G2G_lst.append(i.Source_BSC__Target_CI_LAC)
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC,
                                               [command_ext_2g2g, i.Type_ho])

                command_2g2g = f'ADD G2GNCELL:IDTYPE=BYCGI,SRCMCC="255",SRCMNC="01",SRCLAC={i.Source_LAC}' \
                               f',SRCCI={i.Source_Cell_ID},NBRMCC="255",NBRMNC="01",NBRLAC={i.Target_LAC}' \
                               f',NBRCI={i.Target_Cell_ID},NCELLTYPE=HANDOVERNCELL,SRCHOCTRLSWITCH=HOALGORITHM1;'
                rpdb_cls.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC, [command_2g2g, i.Type_ho])

    def create_ho_2g3g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '2G>3G':
                if i.Source_BSC__Target_CI_LAC not in self.ext_2G3G_dict:
                    command_ext_2g3g = f'ADD GEXT3GCELL:EXT3GCELLNAME={i.Target_full_name}",MCC="255",MNC="01",LAC=' \
                                       f'{i.Target_LAC},CI={i.Target_Cell_ID},RNCID={i.Target_BSC},DF={i.Target_BCCH}' \
                                       f',SCRAMBLE={i.Target_BSIC},DIVERSITY=NO,UTRANCELLTYPE=FDD,OPNAME="MTS Ukraine' \
                                       f'",RA={i.Target_RAC};'
                    self.ext_2G3G_dict[i.Source_BSC__Target_CI_LAC] = i.Target_full_name
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC,
                                               [command_ext_2g3g, i.Type_ho])

                # Source Name из oss_name_2g_dct; Target Name из ext_2G3G_dict
                command_2g3g = f'ADD G3GNCELL:IDTYPE=BYNAME,SRC3GNCELLNAME="{i.Source_full_name}",NBR3GNCELLNAME="' \
                               f'{self.ext_2G3G_dict[i.Source_BSC__Target_CI_LAC]}";'
                rpdb_cls.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC,
                                           [command_2g3g, i.Type_ho])

    def create_ho_3g3g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '3G>3G':
                if i.Source_BSC__Target_CI_LAC not in self.ext_3G3G_lst:
                    command_ext_3g3g = f'ADD UEXT3GCELL:LOGICRNCID={i.Source_BSC},NRNCID={i.Target_BSC},CELLID=' \
                                       f'{i.Target_Cell_ID},CELLHOSTTYPE=SINGLE_HOST,CELLNAME="{i.Target_full_name}"' \
                                       f',CNOPGRPINDEX=0,PSCRAMBCODE={i.Target_BSIC},BANDIND=Band1,UARFCNUPLINKIND=' \
                                       f'TRUE,UARFCNUPLINK={i.Target_BCCH - 950},UARFCNDOWNLINK={i.Target_BCCH},' \
                                       f'TXDIVERSITYIND=FALSE,LAC={i.Target_LAC},CFGRACIND=REQUIRE,RAC=' \
                                       f'{int(i.Target_RAC)},QQUALMININD=FALSE,QRXLEVMININD=FALSE,MAXALLOWEDULTXPOWER' \
                                       f'IND=FALSE,USEOFHCS=NOT_USED,CELLCAPCONTAINERFDD=HSDSCH_SUPPORT-1&EDCH_SUPP' \
                                       f'ORT-1&EDCH_2MS_TTI_SUPPORT-1&EDCH_2SF2_SUPPORT-1&FLEX_MACD_PDU_SIZE_SUPP' \
                                       f'ORT-1&HSPAPLUS_DL_64QAM_SUPPORT-1,EFACHSUPIND=FALSE;'
                    self.ext_3G3G_lst.append(i.Source_BSC__Target_CI_LAC)
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                               [command_ext_3g3g, i.Type_ho])

                if i.Source_BCCH == i.Target_BCCH:
                    command_3g3g = f'ADD UINTRAFREQNCELL:RNCID={i.Source_BSC},CELLID={i.Source_Cell_ID},NCELLRNCID=' \
                                   f'{i.Target_BSC},NCELLID={i.Target_Cell_ID},SIB11IND=TRUE,SIB12IND=FALSE,' \
                                   f'TPENALTYHCSRESELECT=D0,NPRIOFLAG=FALSE;'
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                               [command_3g3g, i.Type_ho])
                if i.Source_BCCH != i.Target_BCCH:

                    blind = 'FALSE'
                    if i.Source_SAC == i.Target_SAC:
                        blind = 'TRUE'

                    command_3g3g = f'ADD UINTERFREQNCELL:RNCID={i.Source_BSC},CELLID={i.Source_Cell_ID},NCELLRNCID=' \
                                   f'{i.Target_BSC},NCELLID={i.Target_Cell_ID},SIB11IND=TRUE,SIB12IND=FALSE,TPENALTY' \
                                   f'HCSRESELECT=D0,BLINDHOFLAG={blind},NPRIOFLAG=FALSE,INTERNCELLQUALREQFLAG=FALSE,' \
                                   f'CLBFLAG=FALSE;'
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                               [command_3g3g, i.Type_ho])

    def create_ho_3g2g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '3G>2G':
                if i.Source_BSC__Target_CI_LAC not in self.ext_3G2G_dict:
                    command_ext_3g2g = f'ADD UEXT2GCELL:LOGICRNCID={i.Source_BSC},GSMCELLINDEX={i.Target_Cell_ID},' \
                                       f'GSMCELLNAME="{i.Target_full_name}",MCC="255",MNC="01",CNOPGRPINDEX=0,LAC=' \
                                       f'{i.Target_LAC},CFGRACIND=REQUIRE,RAC={int(i.Target_RAC)},CID=' \
                                       f'{i.Target_Cell_ID},NCC={i.Target_ncc},BCC={i.Target_bcc},BCCHARFCN=' \
                                       f'{i.Target_BCCH},RATCELLTYPE=EDGE,USEOFHCS=NOT_USED,SUPPPSHOFLAG=TRUE;'
                    self.ext_3G2G_dict[i.Source_BSC__Target_CI_LAC] = i.Target_Cell_ID
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                               [command_ext_3g2g, i.Type_ho])

                command_3g2g = f'ADD U2GNCELL:RNCID={i.Source_BSC},CELLID={i.Source_Cell_ID},GSMCELLINDEX=' \
                               f'{self.ext_3G2G_dict[i.Source_BSC__Target_CI_LAC]},BLINDHOFLAG=FALSE,NPRIOFLAG=FALSE;'
                rpdb_cls.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                           [command_3g2g, i.Type_ho])

    def create_ho_ltelte(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == 'LTE>LTE':
                if f'{i.Source_Site_Name}_{i.Target_ENB}_{i.Target_ENB_CI}' not in self.ext_ltelte_lst:
                    command_ext_ltelte = f'ADD EUTRANEXTERNALCELL:MCC="255",MNC="01",ENODEBID={i.Target_ENB},CELLID=' \
                                         f'{i.Target_ENB_CI},DLEARFCN={i.Target_BCCH},ULEARFCNCFGIND=NOT_CFG,PHYCEL' \
                                         f'LID={i.Target_BSIC},TAC={i.Target_LAC},CELLNAME={i.Target_full_name},NCL' \
                                         f'UPDATEMODE=MFBI_UPDATE_MODE-1,SUPPORTEMTCFLAG=BOOLEAN_FALSE,AGGREGATIONAT' \
                                         f'TRIBUTE=MASTER_PLMN_RESERVED_FLAG-1;'
                    self.ext_ltelte_lst.append(f'{i.Source_Site_Name}_{i.Target_ENB}_{i.Target_ENB_CI}')
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_ext_ltelte,
                                               i.Type_ho])

                if i.Source_BCCH == i.Target_BCCH:
                    command_ltelte = f'ADD EUTRANINTRAFREQNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",' \
                                     f'ENODEBID={i.Target_ENB},CELLID={i.Target_ENB_CI},LOCALCELLNAME=' \
                                     f'{i.Source_full_name},NEIGHBOURCELLNAME={i.Target_full_name},AGGREGATIONATTRI' \
                                     f'BUTE=UL_INTRF_DET_COORD_NCELL_FLAG-0;'
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_ltelte,
                                               i.Type_ho])
                if i.Source_BCCH != i.Target_BCCH:
                    command_ltelte = f'ADD EUTRANINTERFREQNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",' \
                                     f'ENODEBID={i.Target_ENB},CELLID={i.Target_ENB_CI},LOCALCELLNAME=' \
                                     f'{i.Source_full_name}+ ,NEIGHBOURCELLNAME={i.Target_full_name} + ,AGGREGATIONP' \
                                     f'ROPERTY=BlindScellCfg-1,OVERLAPINDICATOREXTENSION=VIRTUAL_4T4R_' \
                                     f'OVERLAP_INDICATOR-1;'
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_ltelte,
                                               i.Type_ho])

    def create_ho_lte2g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == 'LTE>2G':
                if f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}' not in self.ext_lte2g:
                    command_ext_lte2g = f'ADD GERANEXTERNALCELL:MCC="255",MNC="01",GERANCELLID={i.Target_Cell_ID},LAC' \
                                        f'{i.Target_LAC},RACCFGIND=CFG,RAC={i.Target_LAC},BANDINDICATOR=GSM_dcs1800' \
                                        f',GERANARFCN={i.Target_BCCH},NETWORKCOLOURCODE={i.Target_ncc},BASESTATIONC' \
                                        f'OLOURCODE={i.Target_bcc},CELLNAME="{i.Target_full_name}";'
                    self.ext_lte2g.append(f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}')
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_ext_lte2g,
                                                                                                    i.Type_ho])

                if f'{i.Source_ENB}_{i.Source_ENB_CI}_{i.Target_BCCH}' not in self.arfcn_lte2g:
                    command_arfcn = f'ADD GERANNFREQGROUPARFCN:LOCALCELLID={i.Source_ENB_CI},BCCHGROUPID=0,GERANARFCN' \
                                    f'={i.Target_BCCH};'
                    self.ext_lte2g.append(f'{i.Source_ENB}_{i.Source_ENB_CI}_{i.Target_BCCH}')
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_arfcn,
                                                                                                    i.Type_ho])

                i.BLINDHOPRIORITY = '0'
                if i.Source_full_name[:15] == i.Target_full_name[:15]:
                    i.BLINDHOPRIORITY = '32'
                command_lte2g = f'ADD GERANNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",LAC={i.Target_LAC},' \
                                f'GERANCELLID={i.Target_Cell_ID},BLINDHOPRIORITY={i.BLINDHOPRIORITY},LOCALCELLNAME=' \
                                f'"{i.Source_full_name}"+ ,NEIGHBOURCELLNAME="{i.Target_full_name}";'
                rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_lte2g,
                                                                                                i.Type_ho])

    def create_ho_2glte(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '2G>LTE':
                if f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}' not in self.ext_2glte:
                    command_ext_2glte = f'ADD GEXTLTECELL:EXTLTECELLNAME="{i.Target_full_name}",MCC="255"MNC="01",' \
                                        f'ENODEBTYPE=MACRO,CI={(int(i.Target_ENB)*256)+int(i.Target_ENB_CI)},TAC=' \
                                        f'{i.Target_LAC},FREQ={i.Target_BCCH},PCID={i.Target_BSIC},' \
                                        f'EUTRANTYPE=FDD,OPNAME="MTS Ukraine";'
                    self.ext_2glte.append(f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}')
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC, [command_ext_2glte,
                                                                                              i.Type_ho])
                command_2glte = f'ADD GLTENCELL:IDTYPE=BYNAME,SRCLTENCELLNAME="{i.Source_full_name}"NBRLTENCELLNAME="' \
                                f'{i.Target_full_name}",SPTRESEL=SUPPORT,SPTRAPIDSEL=SUPPORT;'
                rpdb_cls.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC, [command_2glte, i.Type_ho])

    def create_ho_lte3g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == 'LTE>3G':
                if f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}' not in self.ext_lte3g_lst:
                    command_ext_lte3g = f'ADD UTRANEXTERNALCELL:MCC="255",MNC="01",RNCID={i.Target_BSC},CELLID=' \
                                        f'{i.Target_Cell_ID},UTRANDLARFCN={i.Target_BCCH},UTRANULARFCNCFGIND=NOT_CFG' \
                                        f',UTRANFDDTDDTYPE=UTRAN_FDD,RACCFGIND=CFG,RAC={i.Target_RAC},PSCRAMBCODE=' \
                                        f'{i.Target_BSIC},LAC={i.Target_LAC},CELLNAME="{i.Target_full_name}";'
                    self.ext_lte3g_lst.append(f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}')
                    rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_ext_lte3g,
                                                                                                   i.Type_ho])
                BLINDHOPRIORITY_part = 'LOCALCELLNAME='
                if i.Source_full_name[:15] == i.Target_full_name[:15]:
                    BLINDHOPRIORITY_part = 'BLINDHOPRIORITY=32,OVERLAPIND=YES,NCELLMEASPRIORITY=128, + LOCALCELLNAME='

                command_lte3g = f'ADD UTRANNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",RNCID=' \
                                f'{i.Target_BSC},CELLID={i.Target_Cell_ID},{BLINDHOPRIORITY_part}"' \
                                f'{i.Source_full_name}",NEIGHBOURCELLNAME="{i.Target_full_name}";'
                rpdb_cls.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [command_lte3g,
                                                                                                i.Type_ho])



