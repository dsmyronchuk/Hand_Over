from readrows import ReadRows
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import openpyxl


class NSN:
    lst_nsn = []
    NSN_2G2G = []
    NSN_2G3G = []
    NSN_3G2G = []
    NSN_3G3G_adji = []
    NSN_3G3G_adjs = []

    def __init__(self, main_bs, path_folder):
        self.main_bs = main_bs
        self.path_folder = path_folder
        self.search_nsn()                    # Из общего списка HandOver ищу Source ZTE обьекты

        # Генерация команд
        self.create_ho_2g2g()
        self.create_ho_2g3g()
        self.create_ho_3g2g()
        self.create_ho_3g3g()

        # Создание итоговых файлов xml; csv для СУ
        if (len(self.__class__.NSN_3G3G_adji) + len(self.__class__.NSN_3G3G_adjs) + len(self.__class__.NSN_3G2G)) > 0:
            self.create_xml_3g()
        if len(self.__class__.NSN_2G2G) > 0:
            self.create_csv_2g2g()
        if len(self.__class__.NSN_2G3G) > 0:
            self.create_csv_2g3g()

    def search_nsn(self):
        for i in ReadRows.lst_row:
            if i.Source_vendor == 'NSN':
                self.__class__.lst_nsn.append(i)

    def create_ho_2g2g(self):
        for i in self.__class__.lst_nsn:
            csv_row = []
            if i.Type_ho == '2G>2G':
                csv_row.append('Create')
                csv_row.append(str(int(i.Source_Cell_ID)))
                csv_row.append(str(int(i.Source_LAC)))
                csv_row.append('255')
                csv_row.append('01')
                csv_row.append(str(int(i.Target_Cell_ID)))
                csv_row.append(str(int(i.Target_LAC)))
                csv_row.append('255')
                csv_row.append('01')
                csv_row.append(f'{i.Source_Site_Name[-1]}->{i.Target_Site_Name[-1:]}')
                if i.Target_BCCH > 123:
                    csv_row.append('GSM 1800')
                else:
                    csv_row.append('GSM 900')
                csv_row.append(str(int(i.Target_BCCH)))
                csv_row.append(i.Target_bcc)
                csv_row.append(i.Target_ncc)

                self.__class__.NSN_2G2G.append(csv_row)

    def create_ho_2g3g(self):
        for i in self.__class__.lst_nsn:
            csv_row = []
            if i.Type_ho == '2G>3G':
                csv_row.append('Create')
                csv_row.append(str(int(i.Source_Cell_ID)))
                csv_row.append(str(int(i.Source_LAC)))
                csv_row.append('255')
                csv_row.append('01')
                csv_row.append(str(int(i.Target_Cell_ID)))
                csv_row.append(str(int(i.Target_BSC)))
                csv_row.append('255')
                csv_row.append('01')
                csv_row.append('MTS_ADJW')

                self.__class__.NSN_2G3G.append(csv_row)

    def create_ho_3g2g(self):
        for i in self.__class__.lst_nsn:
            if i.Type_ho == '3G>2G':
                row_xml = [str(int(i.Source_Cell_ID)), str(int(i.Source_BSC)), str(int(i.Target_Cell_ID)),
                           str(int(i.Target_LAC)), str(i.Target_bcc), str(i.Target_ncc), str(int(i.Target_BCCH))]
                self.__class__.NSN_3G2G.append(row_xml)

    def create_ho_3g3g(self):
        for i in self.__class__.lst_nsn:
            if i.Type_ho == '3G>3G':
                if i.Source_BCCH == i.Target_BCCH:
                    row_xml = [str(int(i.Source_Cell_ID)), str(int(i.Source_BSC)), str(int(i.Target_Cell_ID)),
                               str(int(i.Target_LAC)), str(int(i.Target_RAC)), str(int(i.Target_BSC)),
                               str(int(i.Target_BSIC))]
                    self.__class__.NSN_3G3G_adjs.append(row_xml)
                else:
                    row_xml = [str(int(i.Source_Cell_ID)), str(int(i.Source_BSC)), str(int(i.Target_Cell_ID)),
                               str(int(i.Target_LAC)), str(int(i.Target_RAC)), str(int(i.Target_BSC)),
                               str(int(i.Target_BSIC)), str(int(i.Target_BCCH))]
                    self.__class__.NSN_3G3G_adji.append(row_xml)

    def create_xml_3g(self):
        # словари для managedObject
        umt_sclass_adjs = {'class': 'com.nsn.mcrnc:ADJS'}
        umt_sclass_adji = {'class': 'com.nsn.mcrnc:ADJI'}
        umt_sclass_adjg = {'class': 'com.nsn.mcrnc:ADJG'}

        # создание xml
        new = ET.Element('raml', version='2.1', xmlns='raml21.xsd')
        cm_data = ET.SubElement(new, 'cmData', xmlns="", type='plan', scope='changes', name='ADJx_KIE_2_WBTS_INDOORS')
        header = ET.SubElement(cm_data, 'header')
        log = ET.SubElement(header, 'log', dateTime='29.09.2021', action="created", appInfo="NSN NetAct Plan Editor")
        log.text = 'No description'

        for i in self.__class__.NSN_3G3G_adjs:
            managed_object = ET.SubElement(cm_data, 'managedObject', umt_sclass_adjs, operation="create",
                                           version="mcRNC18")
            p1 = ET.SubElement(managed_object, 'p', name="SourceCI")
            p1.text = i[0]
            p1 = ET.SubElement(managed_object, 'p', name="SourceRncId")
            p1.text = i[1]
            p1 = ET.SubElement(managed_object, 'p', name="SourceMCC")
            p1.text = '255'
            p1 = ET.SubElement(managed_object, 'p', name="SourceMNC")
            p1.text = '01'
            p1 = ET.SubElement(managed_object, 'p', name="AdjsCI")
            p1.text = i[2]
            p1 = ET.SubElement(managed_object, 'p', name="AdjsCPICHTxPwr")
            p1.text = '330'
            p1 = ET.SubElement(managed_object, 'p', name="AdjsLAC")
            p1.text = i[3]
            p1 = ET.SubElement(managed_object, 'p', name="AdjsMCC")
            p1.text = '255'
            p1 = ET.SubElement(managed_object, 'p', name="AdjsMNC")
            p1.text = '01'
            p1 = ET.SubElement(managed_object, 'p', name="AdjsRAC")
            p1.text = i[4]
            p1 = ET.SubElement(managed_object, 'p', name="AdjsRNCid")
            p1.text = i[5]
            p1 = ET.SubElement(managed_object, 'p', name="AdjsScrCode")
            p1.text = i[6]
            p1 = ET.SubElement(managed_object, 'p', name="AdjsSIB")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="NrtHopsIdentifier")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="RtHopsIdentifier")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="AdjsEcNoOffset")
            p1.text = '0'
            p1 = ET.SubElement(managed_object, 'p', name="HSDPAHopsIdentifier")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="RTWithHSDPAHopsIdentifier")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="SRBHopsIdentifier")
            p1.text = '0'

        for i in self.__class__.NSN_3G3G_adji:
            managed_object = ET.SubElement(cm_data, 'managedObject', umt_sclass_adji, operation="create",
                                           version="mcRNC18")
            p1 = ET.SubElement(managed_object, 'p', name="SourceCI")
            p1.text = i[0]
            p1 = ET.SubElement(managed_object, 'p', name="SourceRncId")
            p1.text = i[1]
            p1 = ET.SubElement(managed_object, 'p', name="SourceMCC")
            p1.text = '255'
            p1 = ET.SubElement(managed_object, 'p', name="SourceMNC")
            p1.text = '01'
            p1 = ET.SubElement(managed_object, 'p', name="AdjiCI")
            p1.text = i[2]
            p1 = ET.SubElement(managed_object, 'p', name="AdjiCPICHTxPwr")
            p1.text = '330'
            p1 = ET.SubElement(managed_object, 'p', name="AdjiLAC")
            p1.text = i[3]
            p1 = ET.SubElement(managed_object, 'p', name="AdjiMCC")
            p1.text = '255'
            p1 = ET.SubElement(managed_object, 'p', name="AdjiMNC")
            p1.text = '01'
            p1 = ET.SubElement(managed_object, 'p', name="AdjiRAC")
            p1.text = i[4]
            p1 = ET.SubElement(managed_object, 'p', name="AdjiRNCid")
            p1.text = i[5]
            p1 = ET.SubElement(managed_object, 'p', name="AdjiScrCode")
            p1.text = i[6]
            p1 = ET.SubElement(managed_object, 'p', name="AdjiSIB")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="NrtHopiIdentifier")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="RtHopiIdentifier")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="AdjiEcNoOffsetNCHO")
            p1.text = '12'
            p1 = ET.SubElement(managed_object, 'p', name="BlindHOTargetCell")
            p1.text = '0'
            p1 = ET.SubElement(managed_object, 'p', name="AdjiHandlingBlockedCellSLHO")
            p1.text = '0'
            p1 = ET.SubElement(managed_object, 'p', name="AdjiUARFCN")
            p1.text = i[7]

        for i in self.__class__.NSN_3G2G:
            managed_object = ET.SubElement(cm_data, 'managedObject', umt_sclass_adjg, operation="create",
                                           version="mcRNC18")
            p1 = ET.SubElement(managed_object, 'p', name="SourceCI")
            p1.text = i[0]
            p1 = ET.SubElement(managed_object, 'p', name="SourceRncId")
            p1.text = i[1]
            p1 = ET.SubElement(managed_object, 'p', name="SourceMCC")
            p1.text = '255'
            p1 = ET.SubElement(managed_object, 'p', name="SourceMNC")
            p1.text = '01'
            p1 = ET.SubElement(managed_object, 'p', name="AdjgCI")
            p1.text = i[2]
            p1 = ET.SubElement(managed_object, 'p', name="AdjgTxPwrMaxRACH")
            p1.text = '30'
            p1 = ET.SubElement(managed_object, 'p', name="AdjgLAC")
            p1.text = i[3]
            p1 = ET.SubElement(managed_object, 'p', name="AdjgMCC")
            p1.text = '255'
            p1 = ET.SubElement(managed_object, 'p', name="AdjgMNC")
            p1.text = '01'
            p1 = ET.SubElement(managed_object, 'p', name="AdjgBandIndicator")
            p1.text = '0'
            p1 = ET.SubElement(managed_object, 'p', name="AdjgBCC")
            p1.text = i[4]
            p1 = ET.SubElement(managed_object, 'p', name="AdjgBCCH")
            p1.text = i[6]
            p1 = ET.SubElement(managed_object, 'p', name="AdjgSIB")
            p1.text = '1'
            p1 = ET.SubElement(managed_object, 'p', name="NrtHopgIdentifier")
            p1.text = '2'
            p1 = ET.SubElement(managed_object, 'p', name="RtHopgIdentifier")
            p1.text = '2'
            p1 = ET.SubElement(managed_object, 'p', name="AdjgTxPwrMaxTCH")
            p1.text = '30'
            p1 = ET.SubElement(managed_object, 'p', name="AdjgNCC")
            p1.text = i[5]
            p1 = ET.SubElement(managed_object, 'p', name="ADJGType")
            p1.text = '0'
            p1 = ET.SubElement(managed_object, 'p', name="ADJGChangeOrigin")
            p1.text = '2'

        xml_string = ET.tostring(new).decode(errors='ignore')
        xml_prettyxml = minidom.parseString(xml_string).toprettyxml()
        with open(f'{self.path_folder}/___NOKIA___{self.main_bs}_3G.xml', 'w') as xml_file:
            xml_file.write(xml_prettyxml)

    def create_csv_2g2g(self):
        df_2g2g_csv = pd.DataFrame(self.__class__.NSN_2G2G, columns=['$operation', '$sourceCI', '$sourceLAC',
                                                                     '$sourceMCC', '$sourceMNC', '$targetCI',
                                                                     '$targetLAC', '$targetMCC', '$targetMNC',
                                                                     '$templateName', 'frequencyBandInUse',
                                                                     'bcchFrequency', 'adjCellBsicBcc',
                                                                     'adjCellBsicNcc'])

        path_2g2g_csv = f'{self.path_folder}/___NOKIA___{self.main_bs}_2G2G.csv'
        wb = openpyxl.Workbook()
        wb.save(path_2g2g_csv)
        df_2g2g_csv.to_csv(path_2g2g_csv, index=False)

    def create_csv_2g3g(self):
        df_2g3g_csv = pd.DataFrame(self.__class__.NSN_2G3G, columns=['$operation', '$sourceCI', '$sourceLAC',
                                                                     '$sourceMCC', '$sourceMNC', '$targetCI',
                                                                     '$targetRNCId', '$targetMCC', '$targetMNC',
                                                                     '$templateName'])

        path_2g3g_csv = f'{self.path_folder}/___NOKIA___{self.main_bs}_2G3G.csv'
        wb = openpyxl.Workbook()
        wb.save(path_2g3g_csv)
        df_2g3g_csv.to_csv(path_2g3g_csv, index=False)


