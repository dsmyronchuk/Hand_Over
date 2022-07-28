from readrows import ReadRows
from Static_Cls import StaticCls
from jinja2 import Template
import sql_request
import pandas as pd
import openpyxl


class ZTE(StaticCls):
    lst_zte = []
    ZTE_from_2G = dict()    # Словарь с 2же командами
    ZTE_from_3G = dict()    # Словарь с 3же командами
    ZTE_from_LTE = dict()   # Словарь с LTE командами

    def __init__(self,):
        self.name_bs = StaticCls.name_bs
        self.path_folder = StaticCls.path_folder

        self.search_zte()                   # Из общего списка HandOver ищу Source ZTE обьекты
        self.add_relation_parametr()        # добавляю локальные параметрі для relation
        self.add_2g_parametr_btsid()        # BTS ID, BTS Cell ID для 2G
        self.add_lte_parametr()             # добавляю параметры SubNetwork, MEID, Target MHz Spectre (LTE)
        self.table_functions_relation()     # работа с таблицами Relation
        self.table_functions_external()     # работа с таблицами Externall Cell

        # Генерация команд
        self.create_ho_2g2g()
        self.create_ho_2g3g()
        self.create_ho_3g3g()
        self.create_ho_3g2g()
        self.create_ho_4g4g()
        self.create_ho_4g2g()
        self.create_ho_4g3g()

        self.sorting_for_xlsx()             # Сортировка комманд в нужном формате для записи в xlsx
        self.create_xlsx_file()             # Создание итогового xlsx файла и запись в него команд

    def search_zte(self):
        for i in ReadRows.lst_row:
            if i.Source_vendor == 'ZTE':
                self.__class__.lst_zte.append(i)
                i.info_column = f'{i.Source_full_name}({i.Source_Cell_ID}) >>> {i.Target_full_name}({i.Target_Cell_ID})'

    def add_relation_parametr(self):
        for i in self.__class__.lst_zte:
            if i.Type_ho == '2G>2G':
                if i.Source_BCCH < 125 and i.Target_BCCH < 125:  # G>G
                    i.RxLevMin = '15'
                    i.HoMarginPbgt = '32'
                    i.NCellLayer = '1'
                    i.MacroMicroHoThs = '20'
                    i.HoPriority = '3'

                if i.Source_BCCH < 125 and i.Target_BCCH > 125:  # G>D
                    i.RxLevMin = '16'
                    i.HoMarginPbgt = '20'
                    i.NCellLayer = '3'
                    i.MacroMicroHoThs = '20'
                    i.HoPriority = '7'

                if i.Source_BCCH > 125 and i.Target_BCCH > 125:  # D>D
                    i.RxLevMin = '15'
                    i.HoMarginPbgt = '32'
                    i.NCellLayer = '1'
                    i.MacroMicroHoThs = '18'
                    i.HoPriority = '7'

                if i.Source_BCCH > 125 and i.Target_BCCH < 125:  # D>G
                    i.RxLevMin = '15'
                    i.HoMarginPbgt = '32'
                    i.NCellLayer = '2'
                    i.MacroMicroHoThs = '18'
                    i.HoPriority = '3'

                if i.Target_BCCH > 125:
                    i.MsTxPwrMax = '0'
                    i.MsTxPwrMaxCch = '0'
                    i.freqBand = '2'
                if i.Target_BCCH < 125:
                    i.MsTxPwrMax = '5'
                    i.MsTxPwrMaxCch = '5'
                    i.freqBand = '0'

            if i.Type_ho == 'LTE>LTE':
                if i.Target_BCCH == 3676:
                    i.freqBandInd = '8'
                    i.earfcnUl = '902.6'
                    i.earfcnDl = '947.6'
                if i.Target_BCCH == 1700:
                    i.freqBandInd = '3'
                    i.earfcnUl = '1760'
                    i.earfcnDl = '1855'

            if i.Type_ho =='LTE>2G':
                if i.Target_BCCH in range(1, 124):
                    i.freqBand = 6
                if i.Target_BCCH in range(512, 885):
                    i.freqBand = 9

            if i.Type_ho == 'LTE>3G':
                if i.Target_BCCH == 10712:
                    i.uarfcnUl = 1952.4
                    i.uarfcnDl = 2142.4
                if i.Target_BCCH == 10737:
                    i.uarfcnUl = 1957.4
                    i.uarfcnDl = 2147.4
                if i.Target_BCCH == 10762:
                    i.uarfcnUl = 1962.4
                    i.uarfcnDl = 2152.4

    def add_2g_parametr_btsid(self):
        # выкачиваю и обрабатываю таблицу GGsmCell
        path_gsm_cell = sql_request.ZTE_gsm_cell
        self.gsm_cell_dict = self.get_dct_4column(path_gsm_cell, 'MEID', 'cellIdentity',
                                                     'GBtsSiteManager', 'GGsmCell', '2key_2value')

        # Если сота создана сегодня, её не будет в БД, по этому данные нужно ввести вручную
        for i in self.__class__.lst_zte:
            if i.Source_BCCH < 950 and f'{i.Source_BSC}_{i.Source_Cell_ID}' not in self.gsm_cell_dict:
                inp = input(f'Введите 2G ID, 2GCell ID для соты {i.Source_Site_Name}({i.Source_Cell_ID}): ').split(',')
                inp[1] = inp[1].strip()     # убираю пробел, если пользователь ввёл данные с пробелом
                self.gsm_cell_dict[f'{i.Source_BSC}_{i.Source_Cell_ID}'] = inp

        # добавляю данные BTS ID, BTS Cell ID в аттрибуты обьекта
        for i in self.__class__.lst_zte:
            key_source = f'{i.Source_BSC}_{i.Source_Cell_ID}'
            key_target = f'{i.Target_BSC}_{i.Target_Cell_ID}'
            if i.Source_BCCH < 950 and key_source in self.gsm_cell_dict:
                i.Source_BTS_ID = self.gsm_cell_dict[key_source][0]
                i.Source_BTS_Cell = self.gsm_cell_dict[key_source][1]
            if i.Target_BCCH < 950 and i.Target_vendor == 'ZTE' and key_target in self.gsm_cell_dict:
                i.Target_BTS_ID = self.gsm_cell_dict[key_target][0]
                i.Target_BTS_Cell = self.gsm_cell_dict[key_target][1]

    def add_lte_parametr(self):
        # SubNetwork; MEID
        path_ne = sql_request.ZTE_ne_sdr
        sql_table = pd.read_sql(path_ne, self.connect_sql())
        dct = {row['Name']: [row['SubNetwork'], row['MEID']] for index, row in sql_table.iterrows()}

        for i in self.__class__.lst_zte:
            if i.Source_BCCH in (1700, 2900, 3676) and i.Source_Site_Name[:11] in dct:
                i.SubNetwork = dct[i.Source_Site_Name[:11]][0]
                i.MEID = dct[i.Source_Site_Name[:11]][1]
            # Если БС создана сегодня, то её не будет в БД, данные нужно ввести вручную
            elif i.Source_BCCH in (1700, 2900, 3676) and i.Source_Site_Name[:11] not in sql_table:
                user_SubNetwork = input(f'Введите SubNetwork для соты {i.Source_full_name}: ')
                user_MEID = input(f'Введите MEID для соты {i.Source_full_name}: ')

                i.SubNetwork = user_SubNetwork
                i.MEID = user_MEID

                # добавляю в словарь для будущих строк с этой БС
                dct[i.Source_Site_Name[:11]] = [user_SubNetwork, user_MEID]

        # Target LTE Spectr (MHz)
        path_lte_cell = sql_request.ZTE_lte_cell
        dct_lte_cell = self.get_dct_4column(path_lte_cell, 'ENBFunctionFDD', 'cellLocalId', 'Name',
                                               'bandWidthDl', '3key_1value')
        for i in self.__class__.lst_zte:
            if i.Type_ho == 'LTE>LTE':
                key = f'{i.Target_ENB}_{i.Target_ENB_CI}_{i.Target_Site_Name[:11]}'
                if key in dct_lte_cell:
                    i.Target_MHz = dct_lte_cell[key]
                else:  # Если БС создана сегодня, то её не будет в БД, данные нужно ввести вручную
                    print(f'Введите спектр полосы (MHz) для LTE соты {i.Target_full_name}')
                    user_mhz = input('(3, 5, 15, 20): ')
                    i.Target_MHz = user_mhz
                    dct_lte_cell[key] = user_mhz        # добавляю в словарь для будущих строк с этой БС

    def table_functions_relation(self):
        # Обработка таблицы 2G2G_relation ( для GGsmRelationSeq )
        path_2g2g_relation = sql_request.ZTE_relation_index_2g2g
        self.index_2g2g = self.get_dct_4column(path_2g2g_relation, 'MEID', 'GBtsSiteManager', 'GGsmCell',
                                                  'GGsmRelationSeq', '3key_1value')
        for k, v in self.index_2g2g.items():  # передываю цельную строку в список строк
            self.index_2g2g[k] = v.split(',')

        # Обработка таблицы 2G3G_relation ( для GGsmRelationSeq )
        path_2g3g_relation = sql_request.ZTE_relation_index_2g3g
        self.index_2g3g = self.get_dct_4column(path_2g3g_relation, 'MEID', 'GBtsSiteManager', 'GGsmCell',
                                                  'GUtranRelationSeq', '3key_1value')
        for k, v in self.index_2g3g.items():  # передываю цельную строку в список строк
            self.index_2g3g[k] = v.split(',')

        # обработка таблицы LTELTE_relation
        path_4g4g_relation = sql_request.ZTE_relation_index_4g4g
        self.index_4g4g = self.get_dct_4column(path_4g4g_relation, 'SubNetwork', 'MEID', 'EUtranCellFDD',
                                                  'EUtranRelation_index', '3key_1value')
        for k, v in self.index_4g4g.items():  # передываю цельную строку в список строк
            self.index_4g4g[k] = v.split(',')

        # обработка таблицы LTE2G_relation
        path_4g2g_relation = sql_request.ZTE_relation_index_4g2g
        self.index_4g2g = self.get_dct_4column(path_4g2g_relation, 'SubNetwork', 'MEID', 'EUtranCellFDD',
                                                  'GsmRelation_index', '3key_1value')
        for k, v in self.index_4g2g.items():  # передываю цельную строку в список строк
            self.index_4g2g[k] = v.split(',')

        # обработка таблицы LTE3G_relation
        path_4g3g_relation = sql_request.ZTE_relation_index_4g3g
        self.index_4g3g = self.get_dct_4column(path_4g3g_relation, 'SubNetwork', 'MEID', 'EUtranCellFDD',
                                                  'UtranRelation_index', '3key_1value')
        for k, v in self.index_4g3g.items():  # передываю цельную строку в список строк
            self.index_4g3g[k] = v.split(',')

    def table_functions_external(self):
        # обработка таблиц EXT 2G2G
        path_ext2g2g = sql_request.ZTE_ext_2g2g
        self.ext2g2g = self.get_dct_4column(path_ext2g2g, 'MEID', 'cellIdentity', 'lac',
                                               'GExternalGsmCell', '3key_1value')

        # обработка таблиц EXT 2G3G
        path_ext2g3g = sql_request.ZTE_ext_2g3g
        self.ext2g3g = self.get_dct_4column(path_ext2g3g, 'MEID', 'ci', 'lac',
                                               'GExternalUtranCellFDD', '3key_1value')

        # обработка таблиц EXT 3G3G
        path_ext3g3g = sql_request.ZTE_ext_3g3g
        self.ext3g3g = self.get_dct_4column(path_ext3g3g, 'MEID', 'cId', 'lac',
                                               'UExternalUtranCellFDD', '3key_1value')

        # Обработка таблиц EXT 3G2G
        path_ext3g2g = sql_request.ZTE_ext_3g2g
        self.ext3g2g = self.get_dct_4column(path_ext3g2g, 'MEID', 'cellIdentity', 'lac',
                                               'UExternalGsmCell', '3key_1value')

        # Обработка таблиц EXT LTELTE
        path_ext4g4g = sql_request.ZTE_ext_4g4g
        self.ext4g4g = self.get_dct_4column(path_ext4g4g, 'SubNetwork', 'ENBFunctionFDD', 'Target_CI',
                                               'ExternalEUtranCellFDD', '3key_1value')
        # Обработка таблиц EXT LTE2G
        path_ext4g2g = sql_request.ZTE_ext_4g2g
        self.ext4g2g = self.get_dct_4column(path_ext4g2g, 'SubNetwork', 'ENBFunctionFDD', 'cellIdentity',
                                               'ExternalGsmCell', '3key_1value')
        # Обработка таблиц EXT LTE3G
        path_ext4g3g = sql_request.ZTE_ext_4g3g
        self.ext4g3g = self.get_dct_4column(path_ext4g3g, 'SubNetwork', 'ENBFunctionFDD', 'cId',
                                               'ExternalUtranCellFDD', '3key_1value')

    def free_slot(self, obj_i):    # возврщатает свободный слот 129-192/0-31, и добавляет это значение в словарь
        key = ''
        dct = {}
        start = 0
        finish = 0
        if obj_i.Type_ho == '2G>2G':
            dct = self.index_2g2g
            key = f'{obj_i.Source_BSC}_{obj_i.Source_BTS_ID}_{obj_i.Source_BTS_Cell}'
            start, finish = 129, 192
        if obj_i.Type_ho == '2G>3G':
            dct = self.index_2g3g
            key = f'{obj_i.Source_BSC}_{obj_i.Source_BTS_ID}_{obj_i.Source_BTS_Cell}'
            start, finish = 129, 192
        if obj_i.Type_ho == 'LTE>2G':
            dct = self.index_4g2g
            key = f'{obj_i.SubNetwork}_{obj_i.MEID}_{obj_i.Source_CI_256}'
            start, finish = 0, 31
        if obj_i.Type_ho == 'LTE>3G':
            dct = self.index_4g3g
            key = f'{obj_i.SubNetwork}_{obj_i.MEID}_{obj_i.Source_CI_256}'
            start, finish = 0, 31
        if obj_i.Type_ho == 'LTE>LTE':
            dct = self.index_4g4g
            key = f'{obj_i.SubNetwork}_{obj_i.MEID}_{obj_i.Source_CI_256}'
            start, finish = 0, 31

        if key in dct:
            lst = dct[key]
            for i in range(start, finish):
                if str(i) not in lst:
                    lst.append(str(i))
                    dct[key] = lst
                    return str(i)

        else:
            dct[key] = [f'{start}']
            return f'{start}'

    def create_new_ext_index(self, obj_i):
        new_value = f'{obj_i.Target_BSC}{obj_i.Target_Cell_ID}'
        key = f'{obj_i.Source_BSC}_{obj_i.Target_Cell_ID}_{obj_i.Target_LAC}'
        if obj_i.Type_ho == '2G>2G':
            self.ext2g2g[key] = new_value
        elif obj_i.Type_ho == '2G>3G':
            self.ext2g3g[key] = new_value
        elif obj_i.Type_ho == '3G>3G':
            self.ext3g3g[key] = new_value
        elif obj_i.Type_ho == '3G>2G':
            self.ext3g2g[key] = new_value

        elif obj_i.Type_ho == 'LTE>2G':
            key = f'{obj_i.SubNetwork}_{obj_i.Source_ENB}_{obj_i.Target_Cell_ID}'
            self.ext4g2g[key] = new_value
        elif obj_i.Type_ho == 'LTE>3G':
            key = f'{obj_i.SubNetwork}_{obj_i.Source_ENB}_{obj_i.Target_Cell_ID}'
            self.ext4g3g[key] = new_value

        if obj_i.Type_ho == 'LTE>LTE':
            key = f'{obj_i.SubNetwork}_{obj_i.Source_ENB}_{obj_i.Target_Cell_ID}'
            new_value = f'{obj_i.Target_Cell_ID}'
            self.ext4g4g[key] = new_value

        return new_value

    def create_ho_2g2g(self):
        temp_self_ho = Template(open('zte_template/2g2g_temp__BSC=BSC.txt').read())
        temp_another_ho = Template(open('zte_template/2g2g_temp__BSC!=BSC.txt').read())
        temp_external = Template(open('zte_template/2g2g_temp_ext.txt').read())

        for i in self.__class__.lst_zte:
            key__bsc_ci_lac = f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}'

            if i.Type_ho == '2G>2G' and i.Source_BSC == i.Target_BSC:
                command_self_ho = temp_self_ho.render(Source_BSC=i.Source_BSC,
                                                      Source_BTS_ID=i.Source_BTS_ID,
                                                      Source_BTS_Cell=i.Source_BTS_Cell,
                                                      GGsmRelationSeq=self.free_slot(i),
                                                      Source_Cell_Id=i.Source_Cell_ID,
                                                      Target_Cell_Id=i.Target_Cell_ID,
                                                      Target_BTS_ID=i.Target_BTS_ID,
                                                      Target_BTS_Cell=i.Target_BTS_Cell,
                                                      RxLevMin=i.RxLevMin,
                                                      HoMarginPbgt=i.HoMarginPbgt,
                                                      NCellLayer=i.NCellLayer,
                                                      MacroMicroHoThs=i.MacroMicroHoThs,
                                                      HoPriority=i.HoPriority)
                self.check_append_dict(self.__class__.ZTE_from_2G, i.Source_BSC, [i.Type_ho, command_self_ho,
                                                                                      i.info_column])

            if i.Type_ho == '2G>2G' and i.Source_BSC != i.Target_BSC and key__bsc_ci_lac not in self.ext2g2g:
                command_external_2g2g = temp_external.render(Source_BSC=i.Source_BSC,
                                                             Ext_BTS_index=self.create_new_ext_index(i),
                                                             Target_Cell_ID=i.Target_Cell_ID,
                                                             Target_bcc=i.Target_bcc,
                                                             Target_ncc=i.Target_ncc,
                                                             Target_LAC=i.Target_LAC,
                                                             Target_RAC=i.Target_RAC,
                                                             frequency_Band=i.freqBand,
                                                             Target_BCCH=i.Target_BCCH,
                                                             MsTxPwrMax=i.MsTxPwrMax,
                                                             MsTxPwrMaxCch=i.MsTxPwrMaxCch)
                self.check_append_dict(self.__class__.ZTE_from_2G, i.Source_BSC, [i.Type_ho, command_external_2g2g,
                                                                                      i.info_column])

            if i.Type_ho == '2G>2G' and i.Source_BSC != i.Target_BSC and key__bsc_ci_lac in self.ext2g2g:
                command_another_ho = temp_another_ho.render(Source_BSC=i.Source_BSC,
                                                            Ext_BTS_index=self.ext2g2g[key__bsc_ci_lac],
                                                            Source_BTS_ID=i.Source_BTS_ID,
                                                            Source_BTS_Cell=i.Source_BTS_Cell,
                                                            GGsmRelationSeq=self.free_slot(i),
                                                            Source_Cell_Id=i.Source_Cell_ID,
                                                            Target_Cell_Id=i.Target_Cell_ID,
                                                            RxLevMin=i.RxLevMin,
                                                            HoMarginPbgt=i.HoMarginPbgt,
                                                            NCellLayer=i.NCellLayer,
                                                            MacroMicroHoThs=i.MacroMicroHoThs,
                                                            HoPriority=i.HoPriority)
                self.check_append_dict(self.__class__.ZTE_from_2G, i.Source_BSC, [i.Type_ho, command_another_ho,
                                                                                      i.info_column])

    def create_ho_2g3g(self):
        temp_ho = Template(open('zte_template/2g3g_temp_ho.txt').read())
        temp_external = Template(open('zte_template/2g3g_temp_ext.txt').read())

        for i in self.__class__.lst_zte:
            key__bsc_ci_lac = f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}'

            if i.Type_ho == '2G>3G' and key__bsc_ci_lac not in self.ext2g3g:
                comand_extrnal = temp_external.render(Source_BSC=i.Source_BSC,
                                                      Ext_BTS_index=self.create_new_ext_index(i),
                                                      Target_BSC=i.Target_BSC,
                                                      Target_LAC=i.Target_LAC,
                                                      Target_RAC=i.Target_RAC,
                                                      Target_BCCH=i.Target_BCCH,
                                                      Target_Name=i.Target_full_name,
                                                      Target_Cell_ID=i.Target_Cell_ID,
                                                      Target_BSIC=i.Target_BSIC)
                self.check_append_dict(self.__class__.ZTE_from_2G, i.Source_BSC, [i.Type_ho, comand_extrnal,
                                                                                      i.info_column])

            if i.Type_ho == '2G>3G':
                command_ho = temp_ho.render(Source_BSC=i.Source_BSC,
                                            Ext_BTS_index=self.ext2g3g[key__bsc_ci_lac],
                                            Source_BTS_ID=i.Source_BTS_ID,
                                            Source_BTS_Cell=i.Source_BTS_Cell,
                                            GUtranRelation=self.free_slot(i),
                                            Source_Cell_ID=i.Source_Cell_ID,
                                            Target_Cell_ID=i.Target_Cell_ID)
                self.check_append_dict(self.__class__.ZTE_from_2G, i.Source_BSC, [i.Type_ho, command_ho,
                                                                                      i.info_column])

    def create_ho_3g3g(self):
        temp_self_ho = Template(open('zte_template/3g3g_temp__RNC=RNC.txt').read())
        temp_another_ho = Template(open('zte_template/3g3g_temp__RNC!=RNC.txt').read())
        temp_external = Template(open('zte_template/3g3g_temp_ext.txt').read())

        for i in self.__class__.lst_zte:
            key__bsc_ci_lac = f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}'

            if i.Type_ho == '3G>3G' and i.Source_BSC != i.Target_BSC and key__bsc_ci_lac not in self.ext3g3g:
                command_external = temp_external.render(Source_BSC=i.Source_BSC,
                                                        Ext_BTS_index=self.create_new_ext_index(i),
                                                        Target_LAC=i.Target_LAC,
                                                        Target_RAC=i.Target_RAC,
                                                        Target_UARFCN=i.Target_BCCH - 950,
                                                        Target_UARFCN_Dl=i.Target_BCCH,
                                                        Target_Name=i.Target_full_name,
                                                        Target_Cell_ID=i.Target_Cell_ID,
                                                        Target_BSIC=i.Target_BSIC)
                self.check_append_dict(self.__class__.ZTE_from_3G, i.Source_BSC, [i.Type_ho, command_external,
                                                                                      i.info_column])

            if i.Type_ho == '3G>3G' and i.Source_BSC != i.Target_BSC:
                command_another_ho = temp_another_ho.render(Source_BSC=i.Source_BSC,
                                                            Source_Cell_ID=i.Source_Cell_ID,
                                                            Target_Name=i.Target_full_name,
                                                            UUtranRelation=f'{i.Target_BSC}{i.Target_Cell_ID}',
                                                            Ext_BTS_index=self.ext3g3g[key__bsc_ci_lac])
                self.check_append_dict(self.__class__.ZTE_from_3G, i.Source_BSC, [i.Type_ho, command_another_ho,
                                                                                      i.info_column])

            if i.Type_ho == '3G>3G' and i.Source_BSC == i.Target_BSC:
                command_self_ho = temp_self_ho.render(Source_BSC=i.Source_BSC,
                                                      Source_Cell_ID=i.Source_Cell_ID,
                                                      UUtranRelation=f'{i.Target_BSC}{i.Target_Cell_ID}',
                                                      Target_Name=i.Target_full_name,
                                                      Target_Cell_ID=i.Target_Cell_ID)
                self.check_append_dict(self.__class__.ZTE_from_3G, i.Source_BSC, [i.Type_ho, command_self_ho,
                                                                                      i.info_column])

    def create_ho_3g2g(self):
        temp_ho = Template(open('zte_template/3g2g_temp_ho.txt').read())
        temp_external = Template(open('zte_template/3g2g_temp_ext.txt').read())

        for i in self.__class__.lst_zte:
            key__bsc_ci_lac = f'{i.Source_BSC}_{i.Target_Cell_ID}_{i.Target_LAC}'

            if i.Type_ho == '3G>2G' and key__bsc_ci_lac not in self.ext3g2g:
                command_external = temp_external.render(Source_BSC=i.Source_BSC,
                                                        Ext_BTS_index=self.create_new_ext_index(i),
                                                        Target_Name=i.Target_full_name,
                                                        Target_bcc=i.Target_ncc,
                                                        Target_ncc=i.Target_bcc,
                                                        Target_Cell_ID=i.Target_Cell_ID,
                                                        Target_LAC=i.Target_LAC,
                                                        Target_RAC=i.Target_RAC)
                self.check_append_dict(self.__class__.ZTE_from_3G, i.Source_BSC, [i.Type_ho, command_external,
                                                                                      i.info_column])

            if i.Type_ho == '3G>2G':
                command_ho = temp_ho.render(Source_BSC=i.Source_BSC,
                                            Source_Cell_ID=i.Source_Cell_ID,
                                            UGsmRelation=f'{i.Target_BSC}{i.Target_Cell_ID}',
                                            Target_Name=i.Target_full_name,
                                            Ext_BTS_index=self.ext3g2g[key__bsc_ci_lac])
                self.check_append_dict(self.__class__.ZTE_from_3G, i.Source_BSC, [i.Type_ho, command_ho,
                                                                                      i.info_column])

    def create_ho_4g4g(self):
        temp_self_ho = Template(open('zte_template/4g4g_temp_self_bs.txt').read())
        temp_another_ho = Template(open('zte_template/4g4g_temp_another_bs.txt').read())
        temp_external = Template(open('zte_template/4g4g_temp_ext.txt').read())

        for i in self.__class__.lst_zte:
            key = ''
            if i.Type_ho == 'LTE>LTE':
                key = f'{i.SubNetwork}_{i.Source_ENB}_{i.Target_Cell_ID}'
            if i.Type_ho == 'LTE>LTE' and i.Source_Site_Name != i.Target_Site_Name and key not in self.ext4g4g:
                command_external = temp_external.render(SAA=i.SubNetwork,
                                                        MEID=i.MEID,
                                                        Source_ENB=i.Source_ENB,
                                                        External_index=self.create_new_ext_index(i),
                                                        Target_Name=i.Target_full_name,
                                                        Freq_Band=i.freqBandInd,
                                                        Target_ENB_CI=i.Target_ENB_CI,
                                                        Target_PCI=i.Target_BSIC,
                                                        Target_TAC=i.Target_LAC,
                                                        Target_MHZ=i.Target_MHz,
                                                        Target_ENB=i.Target_ENB)
                self.check_append_dict(self.__class__.ZTE_from_LTE, i.SubNetwork, [i.Type_ho, command_external,
                                                                                       i.info_column])

            if i.Type_ho == 'LTE>LTE' and i.Source_Site_Name != i.Target_Site_Name:
                command_another_ho = temp_another_ho.render(SAA=i.SubNetwork,
                                                            MEID=i.MEID,
                                                            Source_ENB=i.Source_ENB,
                                                            Source_CI_256=i.Source_CI_256,
                                                            EUtranRelation=self.free_slot(i),
                                                            Target_Name=i.Target_full_name,
                                                            Ext_index=self.ext4g4g[key])
                self.check_append_dict(self.__class__.ZTE_from_LTE, i.SubNetwork, [i.Type_ho, command_another_ho,
                                                                                       i.info_column])

            if i.Type_ho == 'LTE>LTE' and i.Source_Site_Name == i.Target_Site_Name:
                command_self_ho = temp_self_ho.render(SAA=i.SubNetwork,
                                                      MEID=i.MEID,
                                                      Source_ENB=i.Source_ENB,
                                                      Source_CI_256=i.Source_CI_256,
                                                      Target_CI_256=i.Target_CI_256,
                                                      EUtranRelation=self.free_slot(i),
                                                      Target_Name=i.Target_full_name)
                self.check_append_dict(self.__class__.ZTE_from_LTE, i.SubNetwork, [i.Type_ho, command_self_ho,
                                                                                       i.info_column])

    def create_ho_4g2g(self):
        temp_ho = Template(open('zte_template/4g2g_temp_ho.txt').read())
        temp_external = Template(open('zte_template/4g2g_temp_ext.txt').read())

        for i in self.__class__.lst_zte:
            key = ''
            if i.Type_ho == 'LTE>2G':
                key = f'{i.SubNetwork}_{i.Source_ENB}_{i.Target_Cell_ID}'
            if i.Type_ho == 'LTE>2G' and key not in self.ext4g2g:
                command_external = temp_external.render(SAA=i.SubNetwork,
                                                        MEID=i.MEID,
                                                        Source_ENB=i.Source_ENB,
                                                        External_index=self.create_new_ext_index(i),
                                                        Target_Name=i.Target_full_name,
                                                        Target_Cell_ID=i.Target_Cell_ID,
                                                        Target_LAC=i.Target_LAC,
                                                        freqBand=i.freqBand,
                                                        Target_BCCH=i.Target_BCCH,
                                                        Target_ncc=i.Target_ncc,
                                                        Target_bcc=i.Target_bcc,
                                                        Target_RAC=i.Target_RAC)
                self.check_append_dict(self.__class__.ZTE_from_LTE, i.SubNetwork, [i.Type_ho, command_external,
                                                                                       i.info_column])

            if i.Type_ho == 'LTE>2G':
                command_ho = temp_ho.render(SAA=i.SubNetwork,
                                            MEID=i.MEID,
                                            Source_ENB=i.Source_ENB,
                                            Source_CI_256=i.Source_CI_256,
                                            GsmRelation=self.free_slot(i),
                                            Target_Name=i.Target_full_name,
                                            External_index=self.ext4g2g[key])
                self.check_append_dict(self.__class__.ZTE_from_LTE, i.SubNetwork, [i.Type_ho, command_ho,
                                                                                       i.info_column])

    def create_ho_4g3g(self):
        temp_ho = Template(open('zte_template/4g3g_temp_ho.txt').read())
        temp_external = Template(open('zte_template/4g3g_temp_ext.txt').read())

        for i in self.__class__.lst_zte:
            key = ''
            if i.Type_ho == 'LTE>3G':
                key = f'{i.SubNetwork}_{i.Source_ENB}_{i.Target_Cell_ID}'
            if i.Type_ho == 'LTE>3G' and key not in self.ext4g3g:
                command_external = temp_external.render(SAA=i.SubNetwork,
                                                        MEID=i.MEID,
                                                        Source_ENB=i.Source_ENB,
                                                        External_index=self.create_new_ext_index(i),
                                                        Target_Name=i.Target_full_name,
                                                        uarfcnDl=i.uarfcnDl,
                                                        uarfcnUl=i.uarfcnUl,
                                                        Target_LAC=i.Target_LAC,
                                                        Target_BSIC=i.Target_BSIC,
                                                        Target_BSC=i.Target_BSC,
                                                        Target_Cell_ID=i.Target_Cell_ID,
                                                        Target_RAC=i.Target_RAC)
                self.check_append_dict(self.__class__.ZTE_from_LTE, i.SubNetwork, [i.Type_ho, command_external,
                                                                                       i.info_column])

            if i.Type_ho == 'LTE>3G':
                command_ho = temp_ho.render(SAA=i.SubNetwork,
                                            MEID=i.MEID,
                                            Source_ENB=i.Source_ENB,
                                            Source_CI_256=i.Source_CI_256,
                                            UtranRelation=self.free_slot(i),
                                            ExternalUtranCellFDD=self.ext4g3g[key],
                                            Target_Name=i.Target_full_name)
                self.check_append_dict(self.__class__.ZTE_from_LTE, i.SubNetwork, [i.Type_ho, command_ho,
                                                                                       i.info_column])

    def sorting_for_xlsx(self):
        self.__class__.ZTE_from_2G = self.command_sort(self.__class__.ZTE_from_2G, [
            'MOC="GExternalGsmCell"', 'MOC="GGsmRelation"', 'MOC="GExternalUtranCellFDD"', 'MOC="GUtranRelation"'])
        self.__class__.ZTE_from_3G = self.command_sort(self.__class__.ZTE_from_3G, [
            'CREATE:MOC="UExternalUtranCellFDD"', 'CREATE:MOC="UUtranRelation"',
            'CREATE:MOC="UExternalGsmCell"', 'CREATE:MOC="UGsmRelation"'])
        self.__class__.ZTE_from_LTE = self.command_sort(self.__class__.ZTE_from_LTE, [
            'CREATE:MOC="ExternalEUtranCellFDD"', 'CREATE:MOC="EUtranRelation"', 'CREATE:MOC="ExternalGsmCell"',
            'CREATE:MOC="GsmRelation"', 'CREATE:MOC="ExternalUtranCellFDD"', 'CREATE:MOC="UtranRelation"'])

    def create_xlsx_file(self):
        wb = openpyxl.Workbook()
        xlsx_path = f'{self.path_folder}/___ZTE___{self.name_bs}.xlsx'

        wb.save(xlsx_path)
        with pd.ExcelWriter(xlsx_path, engine='openpyxl', mode='w') as writer:
            if len(self.__class__.ZTE_from_2G) > 0:
                df_2g = pd.DataFrame(self.__class__.ZTE_from_2G)
                df_2g.to_excel(writer, sheet_name='2G')
            if len(self.__class__.ZTE_from_3G) > 0:
                df_3g = pd.DataFrame(self.__class__.ZTE_from_3G)
                df_3g.to_excel(writer, sheet_name='3G')
            if len(self.__class__.ZTE_from_LTE) > 0:
                df_lte = pd.DataFrame(self.__class__.ZTE_from_LTE)
                df_lte.to_excel(writer, sheet_name='LTE')



