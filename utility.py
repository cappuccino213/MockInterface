"""
@File : utility.py
@Date : 2023/7/12 16:27
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime
import base64

import imgkit

import requests

import string

from typing import Union

from datetime import datetime, timedelta
import random

from dateutil.parser.isoparser import isoparse
from dateutil.relativedelta import relativedelta
from mimesis import Person,Numeric, Text
from mimesis.random import Random
from mimesis import Cryptographic
from mimesis.locales import Locale
from mimesis import Datetime

from config import CONFIG
from request_model import APIRequestProxy

"""工具模块"""


# mock数据
class FakeData:
    def __init__(self):
        # 从配置读取地域设置
        locale_str = CONFIG.get('mockup').get('locale','ZH') # 默认中文
        locale = Locale[locale_str]
        self.person = Person(locale)
        self.dt = Datetime(Locale.ZH) # 时间对象暂时不变，看后续需求
        self.m_random = Random()  # 随机对象
        self.numeric = Numeric()
        self.tel_phone_header = ['182', '138', '139', '159', '189', '158']
        self.dicom_uid_prefix = "1.2.410.200010.1073359.3636.68918.69638.141818."

    # dicomuid生成
    def dicom_uid(self, length=5) -> str:
        random_int = random.randint(10 ** (length - 1), 10 ** length - 1)  # 生成一个指定长度的随机整数
        random_string = str(random_int).zfill(length)
        return self.dicom_uid_prefix + random_string



    # 自定义号码
    @staticmethod
    def custom_code(mask: str = '######') -> str:
        """
        根据掩码规则生成字符串，支持 '#' 表示数字，其他字符保留
        :param mask: 掩码规则，例如 'FS#####', '#######'
        :return: 根据掩码生成的字符串
        """
        result = ''
        numeric = Numeric()
        text = Text()

        for ch in mask:
            if ch == '#':
                result += str(numeric.integer_number(1, 9))  # 生成一位随机数字
            elif ch == '*':
                result += random.choices(string.ascii_letters + string.digits, k=1)[0]   # 生成一位字母或数字
            else:
                result += ch
        return result

    def multi_type_number(self, num_type, **params):
        if num_type == 'uuid':
            return Cryptographic().uuid()
        elif num_type == 'custom':  # 自定义号码
            mask = params.get('mask', '######')
            return self.custom_code(mask)
        elif num_type == 'dicom':
            return self.dicom_uid()
        else:
            raise ValueError(f"Unsupported number type: {num_type}")

    # 随机生成字符串

    def random_string(self, enum_str: list[str]):
        return self.m_random.choice_enum_item(enum_str)

    # 根据时间范围随机生成时间
    @staticmethod
    def random_time(start_time: Union[str, datetime], end_time: Union[str, datetime]):
        """
        :param start_time: 2023-07-01 00：00：30
        :param end_time:2023-07-31 12：01：30
        :return:介于start和end之间的时间 datetime类型
        """
        if type(start_time) == str:
            # 把字符串时间转化成时间格式
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        # 计算出时间范围
        time_range = (end_time - start_time).days
        # 随机天数
        random_day = random.randint(1, time_range)
        random_time = start_time + timedelta(days=random_day)
        # print(random_time.strftime("%Y-%m-%d %H:%M:%S"))
        # return random_time.strftime("%Y-%m-%d %H:%M:%S")
        return random_time
        # 参考https://blog.csdn.net/weixin_44679038/article/details/128067554

    # 随机生成日期

    def random_date(self, start: int = CONFIG['mockup']['year']['start'],
                    end: int = CONFIG['mockup']['year']['end']):
        """
        :param start: 开始年份
        :param end: 结束年份
        :return: 随机生成指定年份的日期
        """
        return self.dt.date(start=start, end=end).strftime("%Y-%m-%d")

    # 日期区间生成日期

    @staticmethod
    def random_date_in_range(start_date_str: Union[str, datetime],
                             end_date_str: Union[str, datetime],
                             date_format: str = "%Y-%m-%d") -> str:
        """
        在指定日期范围内生成一个随机日期字符串
        :param start_date_str: 起始日期（字符串或 datetime）
        :param end_date_str: 结束日期（字符串或 datetime）
        :param date_format: 输出格式
        :return: 格式化后的日期字符串
        """
        def parse_date(date_val: Union[str, datetime]) -> datetime.date:
            if isinstance(date_val, datetime):
                return date_val.date()
            try:
                # 尝试按格式解析
                return datetime.strptime(date_val, date_format).date()
            except ValueError:
                # 尝试自动识别 ISO 等格式
                return isoparse(date_val).date()

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # 计算两个日期之间的总天数
        delta_days = (end_date - start_date).days

        if delta_days < 0:
            raise ValueError("结束日期不能早于起始日期")

        # 随机选择一天
        random_days = random.randint(0, delta_days)
        random_date = start_date + timedelta(days=random_days)

        return random_date.strftime(date_format)

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
                           age=self.numeric.integer_number(CONFIG['mockup']['age']['start'], CONFIG['mockup']['age']['end']),
                           ageUnit='岁',
                           phone=self.m_random.choice_enum_item(self.tel_phone_header) + self.person.phone_number(
                               '########'),
                           occupation=self.person.occupation(),
                           nation='汉族',
                           nationality='中华人民共和国',
                           maritalStatus=self.random_string(['已婚', '未婚']))
        person_dict['birth'] = (datetime.now().date() - relativedelta(years=person_dict['age'])).strftime(
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
            # clinicDiagnosis='临床诊断的测试文本内容',  # 临床诊断,
            clinicDiagnosis='',  # 临床诊断,
            symptom='',  # 症状
            # symptom='患者症状的描述',  # 症状
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

    # 读取图片转化成Base64流
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


# 代理请求
class HttpProxy:
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url

    def get_proxy(self, proxy_params: APIRequestProxy):
        # 拼接完整接口地址
        api_url = self.proxy_url + proxy_params.api_path

        # 根据请求方法，选择对应的请求方法
        http_method = proxy_params.method.lower()
        if http_method == 'get':
            response = requests.get(api_url, params=proxy_params.params)
        elif http_method == 'post':
            p_headers = proxy_params.headers
            response = requests.post(api_url, headers=p_headers, json=proxy_params.body)
        else:
            raise ValueError("不支持的请求方法")
        return response.json()




# 令牌处理类
class TokenHandle:
    TOKEN_HOST = CONFIG['token_server']['token_host']

    # AUTH_INFO = CONFIG['archive']['auth_product_info']
    # 获取令牌
    def get_token_value(self, auth_info):
       request_body = auth_info
       header = {"content-type": "application/json"}
       api_path = "/Token/RetriveInternal"
       res_result = requests.post(url=self.TOKEN_HOST+api_path, json=request_body, headers=header)
       if res_result.status_code != 200:
           raise Exception(res_result.status_code)
       return res_result.json()


if __name__ == "__main__":
    # test_dict = dict(organizationID="全网云研发中心",
    #                  serviceSectID="CT",
    #                  serviceSect="腹部平扫",
    #                  sex="男性",
    #                  patientID="88888",
    #                  accessionNumber="666666",
    #                  name="患者甲",
    #                  age=28,
    #                  requestDept="骨科",
    #                  auditDate="2023-7-8 12:45:12")
    # print(FakeData().medical_info())

    # test_auth = CONFIG['archive']['auth_product_info']
    # print(TokenHandle().get_token_value(test_auth))
    print(Locale['EN'])