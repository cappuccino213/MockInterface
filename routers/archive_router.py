"""
@File : archive_router.py
@Date : 2023/7/14 13:55
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from fastapi import APIRouter
from response_model import CompareFailList, StudyData
from utility import *

"""接口定义"""
# Archive
# archive_route = APIRouter(prefix="/mock/archive", tags=['archive'])
archive_route = APIRouter(tags=['Archive'])
# fake_data = FakeData()


@archive_route.post('/Exchange/GetCompareFailedStudy', name="获取QA阻塞列表", response_model=CompareFailList)
def get_compare_failed_study():
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
                                           studyDateTime=fake_data.random_date_time('time'),
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


if __name__ == "__main__":
    pass
