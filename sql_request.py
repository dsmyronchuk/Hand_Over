# ZTE

ZTE_gsm_cell = '''SELECT MEID, cellIdentity, GBtsSiteManager, GGsmCell 
               FROM `parse_zte_general`.`GSM_Controller_GGsmCell`'''

ZTE_ne_sdr = '''SELECT USERLABEL as Name, SubNetwork, MEID 
            FROM parse_zte_general.UNIGROUND_SDR_NEManagedElement
            WHERE LENGTH(SubNetwork) = 5;'''

ZTE_lte_cell = '''SELECT ENBFunctionFDD, cellLocalId, substring(userLabel, 1, 11) as Name, bandWidthDl 
              FROM parse_zte_general.FDD_SDR_EUtranCellFDD;'''


ZTE_relation_index_2g2g = '''SELECT MEID, GBtsSiteManager, GGsmCell, GROUP_CONCAT(DISTINCT GGsmRelationSeq
                ORDER BY GGsmRelationSeq) AS GGsmRelationSeq
                FROM `parse_zte_general`.`GSM_Controller_GGsmRelation`
                GROUP BY MEID, GBtsSiteManager, GGsmCell;'''

ZTE_relation_index_2g3g = '''SELECT MEID, GBtsSiteManager, GGsmCell, GROUP_CONCAT(DISTINCT GUtranRelationSeq
                ORDER BY GUtranRelationSeq) as GUtranRelationSeq
                FROM `parse_zte_general`.`GSM_Controller_GUtranRelation`
                GROUP BY MEID, GBtsSiteManager, GGsmCell;'''

ZTE_relation_index_4g4g = '''SELECT SubNetwork, MEID, EUtranCellFDD, GROUP_CONCAT(DISTINCT EUtranRelation
                         ORDER BY EUtranRelation) as EUtranRelation_index
                         FROM `parse_zte_general`.`FDD_SDR_EUtranRelation`
                         GROUP BY MEID;'''

ZTE_relation_index_4g2g = '''SELECT SubNetwork, MEID, EUtranCellFDD, GROUP_CONCAT(DISTINCT GsmRelation
                         ORDER BY GsmRelation) as GsmRelation_index
                         FROM `parse_zte_general`.`FDD_SDR_GsmRelation`
                         GROUP BY MEID;'''

ZTE_relation_index_4g3g = '''SELECT SubNetwork, MEID, EUtranCellFDD, GROUP_CONCAT(DISTINCT UtranRelation
                         ORDER BY UtranRelation) as UtranRelation_index
                         FROM `parse_zte_general`.`FDD_SDR_UtranRelation`
                         GROUP BY MEID;'''

ZTE_ext_2g2g = '''SELECT MEID, cellIdentity, lac, GExternalGsmCell 
              FROM `parse_zte_general`.`GSM_Controller_GExternalGsmCell`'''

ZTE_ext_2g3g = '''SELECT MEID, ci, lac, GExternalUtranCellFDD  
              FROM parse_zte_general.GSM_Controller_GExternalUtranCellFDD'''

ZTE_ext_3g3g = '''SELECT MEID, cId, lac, UExternalUtranCellFDD 
              FROM `parse_zte_general`.`UMTS_Controller_UExternalUtranCellFDD`'''

ZTE_ext_3g2g = '''SELECT MEID, cellIdentity, lac, UExternalGsmCell 
              FROM `parse_zte_general`.`UMTS_Controller_UExternalGsmCell`'''

ZTE_ext_4g4g = '''SELECT SubNetwork, ENBFunctionFDD, concat(eNBId, 0, cellLocalId) as Target_CI, ExternalEUtranCellFDD 
              FROM `parse_zte_general`.`FDD_SDR_ExternalEUtranCellFDD`'''

ZTE_ext_4g2g = '''SELECT SubNetwork, ENBFunctionFDD, cellIdentity, ExternalGsmCell FROM 
              `parse_zte_general`.`FDD_SDR_ExternalGsmCell`'''

ZTE_ext_4g3g = '''SELECT SubNetwork, ENBFunctionFDD, cId, ExternalUtranCellFDD FROM 
              `parse_zte_general`.`FDD_SDR_ExternalUtranCellFDD`'''

ZTE_index_ext_2g2g = '''SELECT MEID, GROUP_CONCAT(DISTINCT GExternalGsmCell
                    ORDER BY MEID) as GExternalGsmCell
                    FROM `parse_zte_general`.`GSM_Controller_GExternalGsmCell`
                    GROUP BY MEID'''

ZTE_index_ext_2g3g = '''SELECT MEID, GROUP_CONCAT(DISTINCT GExternalUtranCellFDD
                    ORDER BY MEID) as GExternalUtranCellFDD
                    FROM `parse_zte_general`.GSM_Controller_GExternalUtranCellFDD
                    GROUP BY MEID'''

# Huawei
Huawei_2g2g_ext = 'SELECT fdn, CI, LAC FROM `parse_huawei`.`GSM_BSC6910GSMGEXT2GCELL`'

Huawei_2g3g_ext = 'SELECT fdn, CI, LAC, EXT3GCELLNAME FROM `parse_huawei`.`GSM_BSC6910GSMGEXT3GCELL`'

Huawei_3g2g_ext = 'SELECT LOGICRNCID, CID, LAC, GSMCELLINDEX FROM `parse_huawei`.`UMTS_BSC6910UMTSGSMCELL`'

Huawei_3g3g_ext = 'SELECT LOGICRNCID, CELLID, LAC FROM `parse_huawei`.`UMTS_BSC6910UMTSNRNCCELL`'

Huawei_4g4g_ext = 'SELECT ENODEBFUNCTIONNAME, ENODEBID, CELLID FROM `parse_huawei`.`BBU_BTS3900EUTRANEXTERNALCELL`'

Huawei_4g3g_ext = 'SELECT ENODEBFUNCTIONNAME, CELLID, LAC FROM `parse_huawei`.`BBU_BTS3900UTRANEXTERNALCELL`'

Huawei_2g_oss_name = 'SELECT fdn, CI, LAC, CELLNAME FROM `parse_huawei`.`GSM_BSC6910GSMGCELL`'

Huawei_3g_oss_name = 'SELECT LOGICRNCID, CELLID, LAC, CELLNAME FROM`parse_huawei`.`UMTS_BSC6910UMTSUCELL`'

Huawei_lte_oss_name = 'SELECT ENODEBFUNCTIONNAME, CELLID, DLEARFCN, CELLNAME FROM`parse_huawei`.`BBU_BTS3900CELL`'

Huawei_ne_oss_name = 'SELECT NAME FROM`parse_huawei`.`BBU_BTS3900NE`'

#MS_rpdb = f"""
#SELECT TOP 1000 [BSC]
#,[CI]
#,[SAC]
#,[LAC]
#,[RAC]
#,[Site Name]
#,[Azimuth]
#,[N]
#,[E]
#,[Tilt]
#,[BSIC]
#,[Channel]
#,[PCI]
#,[RSI]
#,CASE WHEN [BCCH] =1
#THEN 'ИСТИНА'
#ELSE 'ЛОЖЬ'
#END [BCCH]
#,[Id_Site]
#FROM [rpdb].[dbo].[vExpSiemensFP]
#where [Site Name] like '{input('Введите имя БС: ').replace(' ', '_')}_%' and BCCH = 1
#ORDER BY [SAC] ASC, [CI] ASC, [BCCH] ASC
#"""


