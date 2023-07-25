"""
@File : response_model.py
@Date : 2023/7/14 15:24
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import random
import time
from typing import List, Optional, Union

from pydantic import BaseModel

"""返回结果的数据模型"""

"""Archive"""


class StudyData(BaseModel):
    workQueueGuid: str
    patientId: str
    patientName: str
    otherName: str
    patientAge: str
    patientBirthday: str
    patientSex: str
    modality: str
    studyDateTime: str
    accessionNumber: str
    studyInstanceUID: str
    studyDescription: str
    organizationCode: str
    errorDescription: str


class CompareFailList(BaseModel):
    code: int
    data: List[StudyData]
    message: str


"""FollowUp"""


# 可以设置默认返回值
class NoticeResult(BaseModel):
    code: int = 200
    msg: str
    time: str = str(time.time())


"""IMCIS"""


class ReportInfo(BaseModel):
    patientID: str
    name: str
    sex: str
    birthDate: str
    age: Optional[int]
    phoneNumber: str
    accessionNumber: str
    patientClass: Optional[str] = random.choice(['门诊', '住院', '急诊', '体检'])
    serviceSect: Optional[str] = random.choice(
        ['颅脑平扫', '胸部平扫', '肺部增强', '颈部增强', '上腹部平扫', '双手平扫', '膝关节平扫'])
    examDate: str
    resultStauts: Optional[str] = '审核完成'
    printTimes: Optional[int] = 0
    examUID: str
    # docInfoList: Optional[list] = []
    docInfoList: Optional[Union[list, str]] = None
    patientType: Optional[str] = None
    examDeptName: Optional[str] = None
    auditDate: str
    reviseDate: Optional[str] = None
    preliminaryDate: str
    resultStatusCode: Optional[str] = '3080'
    serviceSectID: Optional[str] = random.choice(['CR', 'DR', 'CT', 'RF', 'XA', 'MR', 'MG'])
    organizationID: Optional[str] = 'QWYHZYFZX'
    orderStatus: Optional[bool] = False
    pathType: Optional[str] = None
    medRecNO: str
    insuranceID: Optional[str] = None
    inPatientNO: str
    idCardNO: Optional[str] = None
    examLocation: Optional[str] = random.choice(['机房#1', '机房#2', '机房#3'])
    hasReport: Optional[bool] = True
    placerOrderNO: Optional[str] = None


"""token"""


# 注册信息
class RegisterInfo(BaseModel):
    count: int
    productName: str
    version: str
    hospitalName: str


# 校验产品注册
class CheckStatus(BaseModel):
    registerInfo: RegisterInfo
    desc: str
    status: int = 1


class Token(BaseModel):
    token: str
    desc: str = None
    status: int = 1


class ValidateToken(BaseModel):
    desc: str = None
    status: int = 1


if __name__ == "__main__":
    # st = StudyData(**dict(workQueueGuid='1' patientId='32156' patientName='张颜值'))
    # print(st.model_dump())
    # print(st.model_dump_json())
    pass
