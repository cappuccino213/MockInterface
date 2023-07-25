"""
@File : utility.py
@Date : 2023/7/12 16:27
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime
import base64
import imgkit

from dateutil.relativedelta import relativedelta
from mimesis import Person
from mimesis.random import Random
from mimesis import Cryptographic
from mimesis.locales import Locale
from mimesis import Datetime

from pydicom.uid import generate_uid

"""工具模块"""


# mock数据
class FakeData:
    def __init__(self):
        self.person = Person(Locale.ZH)
        self.dt = Datetime(Locale.ZH)
        self.m_random = Random()  # 随机对象
        self.tel_phone_header = ['182', '138', '139', '159', '189', '158']

    def person_info(self):
        person_dict = dict(name=self.person.full_name(reverse=True).replace(' ', ''),
                           sex=self.person.sex(),
                           age=self.person.age(0, 100),
                           phone=self.m_random.choice_enum_item(self.tel_phone_header) + self.person.phone_number(
                               '########'),
                           occupation=self.person.occupation())
        person_dict['birth'] = (datetime.datetime.now().date() - relativedelta(years=person_dict['age'])).strftime(
            "%Y-%m-%d")

        return person_dict

    # 号码生成
    def multi_type_number(self, num_type, **params):
        if num_type == 'uuid':
            return Cryptographic().uuid()
        if num_type == 'custom':  # 自定义号码
            return self.m_random.custom_code(**params)
        if num_type == 'dicom':
            return generate_uid()

    # 随机生成字符串
    def random_string(self, enum_str: list[str]):
        return self.m_random.choice_enum_item(enum_str)

    # 随机生成时间
    def random_date_time(self, date_type):
        if date_type == 'date':
            return self.dt.date(start=2022, end=2023).strftime("%Y-%m-%d")
        if date_type == 'time':
            return self.dt.datetime(start=2022, end=2023).strftime("%Y-%m-%d %H:%M:%S.%f")


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

    print(fake_data.person_info())
