import openpyxl
from Readrows import ReadRows
from Common import StaticCls
import pandas as pd
import SQL_request


class Huawei(StaticCls):
    lst_huawei = []

    Huawei_from_2G = dict()    # Словарь с 2же командами
    Huawei_from_3G = dict()    # Словарь с 3же командами
    Huawei_from_LTE = dict()   # Словарь с LTE командами

    def __init__(self):
        self.name_bs = StaticCls.name_bs
        self.path_folder = StaticCls.path_folder

        # переменные для хранения EXT и ARFCN LTE<>2G ( исключение дубликатов )
        self.ext_lte2g = []
        self.arfcn_lte2g = []
        self.ext_2glte = []

        self.search_huawei()                    # Из общего списка HandOver ищу Source Huawei обьекты
        self.names_functions()                  # Функции для выгрузки и обработки корректных имен из БД
        self.table_functions_external()         # работа с таблицами Externall Cell

        # Генерация команд
        self.create_ho_2g2g()
        self.create_ho_2g3g()
        self.create_ho_3g3g()
        self.create_ho_3g2g()
        self.create_ho_ltelte()
        self.create_ho_lte2g()
        self.create_ho_2glte()
        self.create_ho_lte3g()

        self.sorting_for_xlsx()                 # Сортировка комманд в нужном формате для записи в xlsx
        self.create_xlsx_file()                 # Создание итогового xlsx файла и запись в него команд

    def search_huawei(self):
        for i in ReadRows.lst_row:
            if i.Source_vendor == 'Huawei':
                self.__class__.lst_huawei.append(i)

    def names_functions(self):
        # выгрузка Cell Name из oss 2G,3G, LTE
        path_2g_oss_name = SQL_request.Huawei_2g_oss_name
        path_3g_oss_name = SQL_request.Huawei_3g_oss_name
        path_ne_oss_name = SQL_request.Huawei_lte_oss_name
        self.oss_name_2g_dct = self.get_dct_4column(path_2g_oss_name, 'fdn', 'CI', 'LAC', 'CELLNAME', '3key_1value')
        self.oss_name_3g_dct = self.get_dct_4column(path_3g_oss_name, 'LOGICRNCID', 'CELLID', 'LAC',
                                                    'CELLNAME', '3key_1value')
        self.oss_name_lte_dct = self.get_dct_4column(path_ne_oss_name, 'ENODEBFUNCTIONNAME', 'CELLID', 'DLEARFCN',
                                                     'CELLNAME', '3key_1value')

        # корректировка имени по OSS ( если сота есть в OSS - перезаписать имя из OSS )
        for i in Huawei.lst_huawei:
            if i.Source_BCCH < 950 and f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}' in self.oss_name_2g_dct:
                i.Source_full_name = self.oss_name_2g_dct[f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}']

            if i.Source_BCCH in (10712, 10737, 10762, 10662) and f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}' \
                    in self.oss_name_3g_dct:
                i.Source_full_name = self.oss_name_3g_dct[f'{i.Source_BSC}_{i.Source_Cell_ID}_{i.Source_LAC}']

            if i.Source_BCCH in (1700, 3676, 2900) and f'{i.Source_Site_Name}_{i.Source_ENB_CI}_{i.Source_BCCH}' \
                    in self.oss_name_lte_dct:
                i.Source_full_name = self.oss_name_lte_dct[
                    f'{i.Source_Site_Name}_{i.Source_ENB_CI}_{i.Source_BCCH}']

            if i.Target_BCCH < 950 and f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}' in self.oss_name_2g_dct:
                i.Target_full_name = self.oss_name_2g_dct[f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}']

            if i.Target_BCCH in (10712, 10737, 10762, 10662) and f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}' \
                    in self.oss_name_3g_dct:
                i.Target_full_name = self.oss_name_3g_dct[f'{i.Target_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}']

            if i.Target_BCCH in (1700, 3676, 2900) and f'{i.Target_Site_Name}_{i.Target_ENB_CI}_{i.Target_BCCH}' \
                    in self.oss_name_lte_dct:
                i.Target_full_name = self.oss_name_lte_dct[
                    f'{i.Target_Site_Name}_{i.Target_ENB_CI}_{i.Target_BCCH}']

        # выгрузка NE имен из oss и создание имени self.Name_NE
        path_ne_oss_name = SQL_request.Huawei_ne_oss_name
        sql_table = pd.read_sql(path_ne_oss_name, self.connect_sql())
        self.oss_ne_name = [row for row in sql_table['NAME']]

        # Если Source_Site_Name есть в БД подставить NE_Name ( имя БС в main topology ) из БД
        for i in self.__class__.lst_huawei:
            for j in self.oss_ne_name:
                if i.Source_Site_Name[:11] == j[:11]:
                    i.NE_Name = j

    def table_functions_external(self):
        # обработка таблицы EXT 2G2G
        path_2g2g_ext = SQL_request.Huawei_2g2g_ext
        self.ext_2G2G_lst = self.get_lst_3column(path_2g2g_ext, 'fdn', 'CI', 'LAC')

        # обработка таблицы EXT 2G3G
        path_2g3g_ext = SQL_request.Huawei_2g3g_ext
        self.ext_2G3G_dict = self.get_dct_4column(path_2g3g_ext, 'fdn', 'CI', 'LAC', 'EXT3GCELLNAME', '3key_1value')

        # обработка таблицы EXT 3G2G
        path_3g2g_ext = SQL_request.Huawei_3g2g_ext
        self.ext_3G2G_dict = self.get_dct_4column(path_3g2g_ext, 'LOGICRNCID', 'CID', 'LAC',
                                                  'GSMCELLINDEX', '3key_1value')

        # обработка таблицы EXT 3G3G
        path_3g3g_ext = SQL_request.Huawei_3g3g_ext
        self.ext_3G3G_lst = self.get_lst_3column(path_3g3g_ext, 'LOGICRNCID', 'CELLID', 'LAC')

        # обработка таблицы EXT LTELTE
        path_4g4g_ext = SQL_request.Huawei_4g4g_ext
        self.ext_ltelte_lst = self.get_lst_3column(path_4g4g_ext, 'ENODEBFUNCTIONNAME', 'ENODEBID', 'CELLID')

        # обработка таблицы EXT LTE3G
        path_4g3g_ext = SQL_request.Huawei_4g3g_ext
        self.ext_lte3g_lst = self.get_lst_3column(path_4g3g_ext, 'ENODEBFUNCTIONNAME', 'CELLID', 'LAC')

    def create_ho_2g2g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '2G>2G':
                if i.Source_BSC__Target_CI_LAC not in self.ext_2G2G_lst and i.Source_BSC != i.Target_BSC:
                    command_ext_2g2g = f'ADD GEXT2GCELL: EXT2GCELLNAME="{i.Target_full_name}",MCC="255",MNC="01",LAC=' \
                                       f'{i.Target_LAC},CI={i.Target_Cell_ID},BCCH={i.Target_BCCH},NCC={i.Target_ncc}' \
                                       f',BCC={i.Target_bcc},RA={int(i.Target_RAC)};'
                    self.ext_2G2G_lst.append(i.Source_BSC__Target_CI_LAC)
                    self.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC,
                                           [i.Type_ho, command_ext_2g2g])

                command_2g2g = f'ADD G2GNCELL:IDTYPE=BYCGI,SRCMCC="255",SRCMNC="01",SRCLAC={i.Source_LAC}' \
                               f',SRCCI={i.Source_Cell_ID},NBRMCC="255",NBRMNC="01",NBRLAC={i.Target_LAC}' \
                               f',NBRCI={i.Target_Cell_ID},NCELLTYPE=HANDOVERNCELL,SRCHOCTRLSWITCH=HOALGORITHM1;'
                self.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC, [i.Type_ho, command_2g2g])

    def create_ho_2g3g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '2G>3G':
                if i.Source_BSC__Target_CI_LAC not in self.ext_2G3G_dict:
                    command_ext_2g3g = f'ADD GEXT3GCELL:EXT3GCELLNAME="{i.Target_full_name}",MCC="255",MNC="01",LAC=' \
                                       f'{i.Target_LAC},CI={i.Target_Cell_ID},RNCID={i.Target_BSC},DF={i.Target_BCCH}' \
                                       f',SCRAMBLE={i.Target_BSIC},DIVERSITY=NO,UTRANCELLTYPE=FDD,OPNAME="MTS Ukraine' \
                                       f'",RA={i.Target_RAC};'
                    self.ext_2G3G_dict[i.Source_BSC__Target_CI_LAC] = i.Target_full_name
                    self.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC,
                                           [i.Type_ho, command_ext_2g3g])

                # Source Name из oss_name_2g_dct; Target Name из ext_2G3G_dict
                command_2g3g = f'ADD G3GNCELL:IDTYPE=BYNAME,SRC3GNCELLNAME="{i.Source_full_name}",NBR3GNCELLNAME="' \
                               f'{self.ext_2G3G_dict[i.Source_BSC__Target_CI_LAC]}";'
                self.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC,
                                       [i.Type_ho, command_2g3g])

    def create_ho_3g3g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '3G>3G':
                if i.Source_BSC__Target_CI_LAC not in self.ext_3G3G_lst and i.Source_BSC != i.Target_BSC:
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
                    self.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                           [i.Type_ho, command_ext_3g3g])

                if i.Source_BCCH == i.Target_BCCH:
                    command_3g3g = f'ADD UINTRAFREQNCELL:RNCID={i.Source_BSC},CELLID={i.Source_Cell_ID},NCELLRNCID=' \
                                   f'{i.Target_BSC},NCELLID={i.Target_Cell_ID},SIB11IND=TRUE,SIB12IND=FALSE,' \
                                   f'TPENALTYHCSRESELECT=D0,NPRIOFLAG=FALSE;'
                    self.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                           [i.Type_ho, command_3g3g])
                if i.Source_BCCH != i.Target_BCCH:

                    blind = 'FALSE'
                    if i.Source_SAC == i.Target_SAC:
                        blind = 'TRUE'

                    command_3g3g = f'ADD UINTERFREQNCELL:RNCID={i.Source_BSC},CELLID={i.Source_Cell_ID},NCELLRNCID=' \
                                   f'{i.Target_BSC},NCELLID={i.Target_Cell_ID},SIB11IND=TRUE,SIB12IND=FALSE,TPENALTY' \
                                   f'HCSRESELECT=D0,BLINDHOFLAG={blind},NPRIOFLAG=FALSE,INTERNCELLQUALREQFLAG=FALSE,' \
                                   f'CLBFLAG=FALSE;'
                    self.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                           [i.Type_ho, command_3g3g])

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
                    self.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                           [i.Type_ho, command_ext_3g2g])

                command_3g2g = f'ADD U2GNCELL:RNCID={i.Source_BSC},CELLID={i.Source_Cell_ID},GSMCELLINDEX=' \
                               f'{self.ext_3G2G_dict[i.Source_BSC__Target_CI_LAC]},BLINDHOFLAG=FALSE,NPRIOFLAG=FALSE;'
                self.check_append_dict(self.__class__.Huawei_from_3G, i.Source_BSC,
                                       [i.Type_ho, command_3g2g])

    def create_ho_ltelte(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == 'LTE>LTE':
                key = f'{i.Source_Site_Name}_{i.Target_ENB}_{i.Target_ENB_CI}'
                if key not in self.ext_ltelte_lst and i.Source_BSC != i.Target_BSC:
                    command_ext_ltelte = f'ADD EUTRANEXTERNALCELL:MCC="255",MNC="01",ENODEBID={i.Target_ENB},CELLID=' \
                                         f'{i.Target_ENB_CI},DLEARFCN={i.Target_BCCH},ULEARFCNCFGIND=NOT_CFG,PHYCEL' \
                                         f'LID={i.Target_BSIC},TAC={i.Target_LAC},CELLNAME="{i.Target_full_name}",NCL' \
                                         f'UPDATEMODE=MFBI_UPDATE_MODE-1,SUPPORTEMTCFLAG=BOOLEAN_FALSE,AGGREGATIONAT' \
                                         f'TRIBUTE=MASTER_PLMN_RESERVED_FLAG-1;'
                    self.ext_ltelte_lst.append(key)
                    self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                                command_ext_ltelte])

                if i.Source_BCCH == i.Target_BCCH:
                    command_ltelte = f'ADD EUTRANINTRAFREQNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",' \
                                     f'ENODEBID={i.Target_ENB},CELLID={i.Target_ENB_CI},LOCALCELLNAME=' \
                                     f'"{i.Source_full_name}",NEIGHBOURCELLNAME="{i.Target_full_name}",' \
                                     f'AGGREGATIONATTRIBUTE=UL_INTRF_DET_COORD_NCELL_FLAG-0;'
                    self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                                command_ltelte])
                if i.Source_BCCH != i.Target_BCCH:
                    command_ltelte = f'ADD EUTRANINTERFREQNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",' \
                                     f'ENODEBID={i.Target_ENB},CELLID={i.Target_ENB_CI},LOCALCELLNAME=' \
                                     f'"{i.Source_full_name}" ,NEIGHBOURCELLNAME="{i.Target_full_name}" ,AGGREGATIONP' \
                                     f'ROPERTY=BlindScellCfg-1,OVERLAPINDICATOREXTENSION=VIRTUAL_4T4R_' \
                                     f'OVERLAP_INDICATOR-1;'
                    self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                                command_ltelte])

    def create_ho_lte2g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == 'LTE>2G':
                if f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}' not in self.ext_lte2g:
                    command_ext_lte2g = f'ADD GERANEXTERNALCELL:MCC="255",MNC="01",GERANCELLID={i.Target_Cell_ID},LAC' \
                                        f'={i.Target_LAC},RACCFGIND=CFG,RAC={i.Target_RAC},BANDINDICATOR=GSM_dcs1800' \
                                        f',GERANARFCN={i.Target_BCCH},NETWORKCOLOURCODE={i.Target_ncc},BASESTATIONC' \
                                        f'OLOURCODE={i.Target_bcc},CELLNAME="{i.Target_full_name}";'
                    self.ext_lte2g.append(f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}')
                    self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                                command_ext_lte2g])

                if f'{i.Source_ENB}_{i.Source_ENB_CI}_{i.Target_BCCH}' not in self.arfcn_lte2g:
                    command_arfcn = f'ADD GERANNFREQGROUPARFCN:LOCALCELLID={i.Source_ENB_CI},BCCHGROUPID=0,GERANARFCN' \
                                    f'={i.Target_BCCH};'
                    self.ext_lte2g.append(f'{i.Source_ENB}_{i.Source_ENB_CI}_{i.Target_BCCH}')
                    self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                                command_arfcn])

                i.BLINDHOPRIORITY = '0'
                if i.Source_full_name[:15] == i.Target_full_name[:15]:
                    i.BLINDHOPRIORITY = '32'
                command_lte2g = f'ADD GERANNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",LAC={i.Target_LAC},' \
                                f'GERANCELLID={i.Target_Cell_ID},BLINDHOPRIORITY={i.BLINDHOPRIORITY},LOCALCELLNAME=' \
                                f'"{i.Source_full_name}" ,NEIGHBOURCELLNAME="{i.Target_full_name}";'
                self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                            command_lte2g])

    def create_ho_2glte(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == '2G>LTE':
                if f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}' not in self.ext_2glte:
                    command_ext_2glte = f'ADD GEXTLTECELL:EXTLTECELLNAME="{i.Target_full_name}",MCC="255",MNC="01",' \
                                        f'ENODEBTYPE=MACRO,CI={(int(i.Target_ENB)*256)+int(i.Target_ENB_CI)},TAC=' \
                                        f'{i.Target_LAC},FREQ={i.Target_BCCH},PCID={i.Target_BSIC},' \
                                        f'EUTRANTYPE=FDD,OPNAME="MTS Ukraine";'
                    self.ext_2glte.append(f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}')
                    self.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC, [i.Type_ho,
                                                                                         command_ext_2glte])
                command_2glte = f'ADD GLTENCELL:IDTYPE=BYNAME,SRCLTENCELLNAME="{i.Source_full_name}",' \
                                f'NBRLTENCELLNAME="{i.Target_full_name}",SPTRESEL=SUPPORT,SPTRAPIDSEL=SUPPORT;'
                self.check_append_dict(self.__class__.Huawei_from_2G, i.Source_BSC, [i.Type_ho, command_2glte])

    def create_ho_lte3g(self):
        for i in self.__class__.lst_huawei:
            if i.Type_ho == 'LTE>3G' and i.Target_BCCH == 10737:
                if f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}' not in self.ext_lte3g_lst:
                    command_ext_lte3g = f'ADD UTRANEXTERNALCELL:MCC="255",MNC="01",RNCID={i.Target_BSC},CELLID=' \
                                        f'{i.Target_Cell_ID},UTRANDLARFCN={i.Target_BCCH},UTRANULARFCNCFGIND=NOT_CFG' \
                                        f',UTRANFDDTDDTYPE=UTRAN_FDD,RACCFGIND=CFG,RAC={i.Target_RAC},PSCRAMBCODE=' \
                                        f'{i.Target_BSIC},LAC={i.Target_LAC},CELLNAME="{i.Target_full_name}";'
                    self.ext_lte3g_lst.append(f'{i.Source_Site_Name}_{i.Target_Cell_ID}_{i.Target_LAC}')
                    self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                                command_ext_lte3g])
                blindhopriority_part = 'LOCALCELLNAME='
                if i.Source_full_name[:15] == i.Target_full_name[:15]:
                    blindhopriority_part = 'BLINDHOPRIORITY=32,OVERLAPIND=YES,NCELLMEASPRIORITY=128, LOCALCELLNAME='

                command_lte3g = f'ADD UTRANNCELL:LOCALCELLID={i.Source_ENB_CI},MCC="255",MNC="01",RNCID=' \
                                f'{i.Target_BSC},CELLID={i.Target_Cell_ID},{blindhopriority_part}"' \
                                f'{i.Source_full_name}",NEIGHBOURCELLNAME="{i.Target_full_name}";'
                self.check_append_dict(self.__class__.Huawei_from_LTE, i.Source_Site_Name, [i.Type_ho,
                                                                                            command_lte3g])

    def sorting_for_xlsx(self):
        self.__class__.Huawei_from_LTE = self.command_sort(self.__class__.Huawei_from_LTE, [
            'ADD EUTRANEXTERNALCELL', 'ADD EUTRANINTRAFREQNCELL', 'ADD EUTRANINTERFREQNCELL', 'ADD GERANEXTERNALCELL',
            'ADD GERANNFREQGROUPARFCN', 'ADD GERANNCELL', 'ADD UTRANEXTERNALCELL', 'ADD UTRANNCELL'])

        self.__class__.Huawei_from_2G = self.command_sort(self.Huawei_from_2G, [
            'ADD GEXT2GCELL', 'ADD G2GNCELL', 'ADD GEXT3GCELL', 'ADD G3GNCELL', 'ADD GEXTLTECELL', 'ADD GLTENCEL'])

        self.__class__.Huawei_from_3G = self.command_sort(self.Huawei_from_3G, [
            'ADD UEXT3GCELL', 'ADD UINTRAFREQNCELL', 'ADD UINTERFREQNCELL', 'ADD UEXT2GCELL', 'ADD U2GNCELL'])

    def create_xlsx_file(self):
        wb = openpyxl.Workbook()
        xlsx_path = f'{self.path_folder}/___HUAWEI___{self.name_bs}.xlsx'

        wb.save(xlsx_path)
        with pd.ExcelWriter(xlsx_path, engine='openpyxl', mode='w') as writer:
            if len(self.__class__.Huawei_from_2G) > 0:
                df_2g = pd.DataFrame(self.__class__.Huawei_from_2G)
                df_2g.to_excel(writer, sheet_name='2G')
            if len(self.__class__.Huawei_from_3G) > 0:
                df_3g = pd.DataFrame(self.__class__.Huawei_from_3G)
                df_3g.to_excel(writer, sheet_name='3G')

            if len(self.__class__.Huawei_from_LTE) > 0:
                df_lte = pd.DataFrame(self.__class__.Huawei_from_LTE)
                df_lte.to_excel(writer, sheet_name='LTE')

