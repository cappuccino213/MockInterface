"""
@File : archive_router.py
@Date : 2023/7/14 13:55
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""

from fastapi import APIRouter, Header, Depends, HTTPException, Body

from request_model import RequestImportOrders, RequestGetStudyApplyImage
from response_model import CompareFailList, StudyData
from utility import *

from typing import Optional

"""接口定义"""
archive_route = APIRouter(tags=['Archive'])

real_archive_host = CONFIG['proxy']['archive_host']


# 定义一个依赖项来从Authorization请求头中提取token
async def get_token_from_header(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return authorization


@archive_route.post('/Exchange/GetCompareFailedStudy', name="获取QA阻塞列表", response_model=CompareFailList)
async def get_compare_failed_study():
    # 未加入参校验和接口逻辑
    # 返回结果生成
    study_list = []
    for _ in range(20):  # 返回的条目
        study_list.append(StudyData(**dict(workQueueGuid=fake_data.multi_type_number('uuid'),
                                           patientId=fake_data.multi_type_number('custom', **dict(mask='FS#####')),
                                           otherName='',
                                           patientName=fake_data.person_info()['name'],
                                           patientAge=str(fake_data.person_info()['age']) + 'y',
                                           patientBirthday=fake_data.person_info()['birth'],
                                           patientSex='Male' if fake_data.person_info()['sex'] == '男性' else 'Female',
                                           modality=fake_data.random_string(['CR', 'DR', 'CT', 'RF', 'XA', 'MR', 'MG']),
                                           studyDateTime=fake_data.random_date(),
                                           accessionNumber=fake_data.multi_type_number('custom',
                                                                                       **dict(mask='#######')),
                                           studyInstanceUID=str(fake_data.multi_type_number('dicom')),
                                           studyDescription='',
                                           organizationCode='QWYHZYFZX',
                                           errorDescription='获取0条待比对检查信息'
                                           )))
    compare_failed_list = CompareFailList(
        **dict(code=1, data=study_list, message="Success"))
    return compare_failed_list


"""以下是转接真实存档路由"""


@archive_route.post('/Exchange/ImportOrders', name="上传检查申请单", description=f"实际访问地址 {real_archive_host}")
async def import_orders(request_body: RequestImportOrders = Body(...), token=Depends(get_token_from_header)):
    """
    :param request_body: Body表示请求体
    :param token: Header表示请求头
    :return:
    """
    real_api = f"{real_archive_host}/Exchange/ImportOrders"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    response = requests.post(real_api, json=request_body.model_dump(), headers=headers)
    if response.status_code == 200:
        return response.json()
    print(f"warning:{response.status_code, response.text}")


@archive_route.post('/Exchange/GetStudyApplyImage', name="获取检查申请单",
                    description=f"实际访问地址 {real_archive_host}")
async def get_study_apply_image(request_body: RequestGetStudyApplyImage = Body(...),
                                token=Depends(get_token_from_header)):
    real_api = f"{real_archive_host}/Exchange/GetStudyApplyImage"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    response = requests.post(real_api, json=request_body.model_dump(), headers=headers)
    if response.status_code == 200:
        return response.json()
    print(f"warning:{response.status_code, response.text}")


if __name__ == "__main__":
    pass
