"""
@File : utility.py
@Date : 2023/7/12 16:27
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime
import base64
import random

import imgkit

from typing import Union

from dateutil.relativedelta import relativedelta
from mimesis import Person
from mimesis.random import Random
from mimesis import Cryptographic
from mimesis.locales import Locale
from mimesis import Datetime


from config import CONFIG

"""工具模块"""


# mock数据
class FakeData:
    def __init__(self):
        self.person = Person(Locale.ZH)
        self.dt = Datetime(Locale.ZH)
        self.m_random = Random()  # 随机对象
        self.tel_phone_header = ['182', '138', '139', '159', '189', '158']
        self.dicom_uid_prefix = "1.2.410.200010.1073359.3636.68918.69638.141818."

    # dicomuid生成
    def dicom_uid(self, length=5) -> str:
        random_int = random.randint(10 ** (length - 1), 10 ** length - 1)  # 生成一个指定长度的随机整数
        random_string = str(random_int).zfill(length)
        return self.dicom_uid_prefix + random_string

    # 号码生成

    def multi_type_number(self, num_type, **params) -> str:
        if num_type == 'uuid':
            return Cryptographic().uuid()
        if num_type == 'custom':  # 自定义号码
            return self.m_random.custom_code(**params)
        if num_type == 'dicom':
            # return generate_uid()
            return self.dicom_uid()

    # 随机生成字符串

    def random_string(self, enum_str: list[str]):
        return self.m_random.choice_enum_item(enum_str)

    # 根据时间范围随机生成时间
    @staticmethod
    def random_time(start_time: Union[str, datetime.datetime], end_time: Union[str, datetime.datetime]):
        """
        :param start_time: 2023-07-01 00：00：30
        :param end_time:2023-07-31 12：01：30
        :return:介于start和end之间的时间 datetime类型
        """
        if type(start_time) == str:
            # 把字符串时间转化成时间格式
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        # 计算出时间范围
        time_range = (end_time - start_time).days
        # 随机天数
        random_day = random.randint(1, time_range)
        random_time = start_time + datetime.timedelta(days=random_day)
        # print(random_time.strftime("%Y-%m-%d %H:%M:%S"))
        # return random_time.strftime("%Y-%m-%d %H:%M:%S")
        return random_time
        # 参考https://blog.csdn.net/weixin_44679038/article/details/128067554

    # 随机生成日期

    def random_date(self, start: int = CONFIG['mockup']['year']['start'],
                    end: int = CONFIG['mockup']['year']['end']):
        # start = CONFIG['mockup']['year']['start']
        # end = CONFIG['mockup']['year']['end']
        return self.dt.date(start=start, end=end).strftime("%Y-%m-%d")
        # if date_type == 'date':
        #     return self.dt.date(start=start, end=end).strftime("%Y-%m-%d")
        # if date_type == 'time':
        #     return self.dt.datetime(start=start, end=end).strftime("%Y-%m-%d %H:%M:%S")  # 用法有误

    def identify_code(self, birth):
        """
        :param birth: 出生日期8位,格式为20000214
        :return: 18位身份证号
        """
        areacode = self.random_string(CONFIG['mockup']['areacode'])
        # 3位顺序码
        sequence_code = self.random_string([str(code) for code in (100, 300)])
        # 校验码，实际校验码需要根据前17位进行加权计算的，这里我们建议枚举处理
        check_code = self.random_string([str(i) for i in range(9)] + ['X'])
        return areacode + birth + sequence_code + check_code

    # 具体业务数据
    def person_info(self):
        person_dict = dict(name=self.person.full_name(reverse=True).replace(' ', ''),
                           sex=self.person.sex(),
                           age=self.person.age(CONFIG['mockup']['age']['start'], CONFIG['mockup']['age']['end']),
                           ageUnit='岁',
                           phone=self.m_random.choice_enum_item(self.tel_phone_header) + self.person.phone_number(
                               '########'),
                           occupation=self.person.occupation(),
                           nation='中华人民共和国',
                           nationality='汉族',
                           maritalStatus=self.random_string(['已婚', '未婚']))
        person_dict['birth'] = (datetime.datetime.now().date() - relativedelta(years=person_dict['age'])).strftime(
            "%Y-%m-%d")
        person_dict['ID'] = self.identify_code(person_dict['birth'].replace('-', ''))

        return person_dict

    # 医疗信息相关
    def medical_info(self):
        medical_dict = dict(
            medrecNo=self.multi_type_number('custom', **dict(mask='######')),  # 病历号
            outPatientNO='',  # 门诊号
            inPatientNO='',  # 住院号
            patientID=self.multi_type_number('custom', **dict(mask='########')),  # 患者编号
            # accessionNumber='',  # 检查编号
            invoiceNO='',  # 发票号
            cardSelfNO='',  # 卡号
            placerOrderNO=self.multi_type_number('custom', **dict(mask='plo######')),  # 申请单号
            insuranceID=self.multi_type_number('custom', **dict(mask='YB########')),  # 医保号
            insuranceType=self.random_string(['医保', '农保']),  # 医保类型
            clinicDiagnosis='临床诊断的测试文本内容',  # 临床诊断,
            symptom='患者症状的描述',  # 症状
            charges=88.0,  # 费用
            requestDeptName='申请科室名称',  # 申请科室
            # providerName='',  # 申请医生名
            patientClass=self.random_string(['1000', '2000', '3000', '4000']),
            serviceSectID=self.random_string(['CR', 'DR', 'CT', 'RF', 'XA', 'MR', 'MG']),
            procedureCode='0' + self.random_string([str(i) for i in range(1001, 2000)]),
            procedureName=self.random_string(
                ['颅脑平扫', '胸部平扫', '肺部增强', '颈部增强', '上腹部平扫', '双手平扫', '膝关节平扫']),
            # requestDate=self.random_date_time('time'),
            organizationCode='QWYHZYFZX',
            organizationName='全网云杭州研发中心'
        )
        medical_dict['accessionNumber'] = medical_dict['serviceSectID'] + self.multi_type_number('custom', **dict(
            mask='########'))
        medical_dict['placerOrderDetailNO'] = medical_dict['placerOrderNO'] + '-1'
        return medical_dict


fake_data = FakeData()


# 工具处理类
class ToolKit:

    @staticmethod
    def fill_html(fill_data: dict, html_file='./static/report/report_template.htm') -> str:
        """
        :param html_file: 含参数值的html文件
        :param fill_data: 填充的参数dict
        :return: 返回html的字符串
        """
        with open(html_file, 'r', encoding='utf-8') as file:
            html_string = file.read()
        return html_string.format(
            organizationID=fill_data.get('organizationID'),
            serviceSectID=fill_data.get('serviceSectID'),
            examDate=fill_data.get('examDate'),
            patientID=fill_data.get('patientID'),
            accessionNumber=fill_data.get('accessionNumber'),
            name=fill_data.get('name'),
            sex=fill_data.get('sex'),
            age=fill_data.get('age'),
            requestDept=fill_data.get('requestDept'),
            serviceSect=fill_data.get('serviceSect'),
            auditDate=fill_data.get('auditDate')
        )
        # return html_string

    # 读取图片转化成直接流
    @staticmethod
    def read_image(image_path=r'./static/ECG1.jpg'):
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        # bytes转base64
        image_str = base64.b64encode(image_bytes)
        return image_str

    # 将html转成图片
    @staticmethod
    def html2img(html_str, output='out.jpg'):
        imgkit.from_string(html_str, output)


tk = ToolKit()

if __name__ == "__main__":
    pass
    test_dict = dict(organizationID="全网云研发中心",
                     serviceSectID="CT",
                     serviceSect="腹部平扫",
                     sex="男性",
                     patientID="88888",
                     accessionNumber="666666",
                     name="患者甲",
                     age=28,
                     requestDept="骨科",
                     auditDate="2023-7-8 12:45:12")
    # ht = tk.fill_html(test_dict)
    #
    # tk.html2img(ht, r'./static/report/out.jpg')

    # print(fake_data.person_info())
    # print(fake_data.medical_info()['placerOrderNO'])
    # print(fake_data.identify_code('19990214'))
    # fake_data.random_time('2023-07-21 14:00:00', '2023-07-31 13:22:54')
    # fd = fake_data.person_info()
    #
    # for _ in range(10):
    #     print(fd)

    print(FakeData().dicom_uid())
