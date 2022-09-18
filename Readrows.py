import Secret_info


class ReadRows:
    lst_row = []
    duplicate_check = []
    path_directory = ''

    def __init__(self, row):
        self.Source_BSC = int(row[0])
        self.Source_Cell_ID = row[1]
        self.Source_SAC = row[2]
        self.Source_LAC = row[3]
        if row[7] not in (1700, 2900, 3676):
            self.Source_RAC = int(row[4])
        self.Source_Site_Name = row[5]
        self.Source_BSIC = int(row[6])
        self.Source_BCCH = row[7]
        self.Source_Azimuth = row[8]
        self.Target_BSC = int(row[9])
        self.Target_Cell_ID = row[10]
        self.Target_SAC = row[11]
        self.Target_LAC = row[12]
        if row[16] not in (1700, 2900, 3676):
            self.Target_RAC = int(row[13])
        self.Target_Site_Name = row[14]
        self.Target_BSIC = int(row[15])
        self.Target_BCCH = row[16]
        self.Target_Azimuth = row[17]
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

    @staticmethod
    def check_vendor(bsc):
        if bsc in Secret_info.ZTE_Controller:
            return 'ZTE'

        elif bsc in Secret_info.Huawei_Controller:
            return 'Huawei'

        elif bsc in Secret_info.NSN_Controller:
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
    def ncc(bsic, bcch):
        if bcch < 950:
            if len(str(bsic)) == 1:
                return 0
            if len(str(bsic)) == 2:
                return str(bsic)[0]
