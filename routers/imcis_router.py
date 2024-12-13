"""
@File : imcis_router.py
@Date : 2023/7/18 17:04
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from typing import List

from fastapi import APIRouter

from response_model import ReportInfo

from request_model import RequestReport

from utility import *

imcis_route = APIRouter(tags=["IMCIS"])


def fake_report_info():
    now = datetime.datetime.today()
    business_time = fake_data.random_time(now - datetime.timedelta(days=30), now)  # 取近一个月的时间
    pi = fake_data.person_info()
    report_info_dict = dict(patientID=fake_data.multi_type_number('custom', **dict(mask='pid######')),
                            name=pi['name'],
                            sex=pi['sex'][0],
                            birthDate=pi['birth'],
                            age=pi['age'],
                            serviceSect=fake_data.random_string(
                                ['颅脑平扫', '胸部平扫', '肺部增强', '颈部增强', '上腹部平扫', '双手平扫',
                                 '膝关节平扫']),
                            serviceSectID=fake_data.random_string(['CR', 'DR', 'CT', 'RF', 'XA', 'MR', 'MG']),
                            organizationID='全网云',
                            phoneNumber=pi['phone'],
                            examDate=business_time.strftime("%Y-%m-%d %H:%M:%S"),
                            examUID=fake_data.multi_type_number('uuid'),
                            auditDate=(business_time + datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),  # 检查后2小时审核
                            preliminaryDate=(business_time + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),  # 检查后1小时报告
                            medRecNO=fake_data.multi_type_number('custom', **dict(mask='mec######')),
                            inPatientNO=fake_data.multi_type_number('custom', **dict(mask='IN######')))
    return report_info_dict


@imcis_route.post("/api/Doc/GetDocList", name="获取报告列表", response_model=List[ReportInfo])
async def get_report_doc(request_body: RequestReport):
    report_info_dict = fake_report_info()
    report_info_dict['accessionNumber'] = request_body.CardNo
    report_info = ReportInfo(**report_info_dict)
    report_list = [report_info]
    return report_list


@imcis_route.post("/api/Doc/GetDoc", name="获取报告", response_model=List[ReportInfo])
async def get_report_doc(request_body: RequestReport):
    report_info_dict = fake_report_info()
    report_info_dict['accessionNumber'] = request_body.CardNo
    # 根据生成的数据，生成报告jpg
    tk.html2img(tk.fill_html(report_info_dict), r'./static/report/out.jpg')
    doc_info_list = [tk.read_image(r'./static/report/out.jpg')]

    report_info_dict['docInfoList'] = doc_info_list
    report_info = ReportInfo(**report_info_dict)
    return [report_info]


if __name__ == "__main__":
    pass
