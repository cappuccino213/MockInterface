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


"""DEP"""


# 电子申请单列表
class ElectronicInfo(BaseModel):
    medrecNo: str
    patientID: Optional[str]
    outPatientNO: Optional[str]  # 门诊类型有
    invoceNO: str
    cardSelfNO: str
    healthCardNO: Optional[str]
    name: str
    birthDate: str
    sex: str  # M 、F
    addressDetail: Optional[str]
    contactPhoneNO: Optional[str]
    age: int
    ageUnit: str
    idCard: str
    nation: str
    nationality: str
    maritalStatus: str
    isPregnant: int = 0  # 0 1
    adverseReaction: Optional[str] # 不良反映
    insuranceType: str
    insuranceID: str
    medicalRecord: Optional[str]
    clinicDiagnosis: str
    symptom: str
    requestAttention: Optional[str]
    reasonforStudy: Optional[str]
    requestMemo: str=''
    charges: float  # 50~165.0
    chargeFlag: str = "1"
    requestDeptName: str
    providerName: str
    patientClass: str  # 1000 2000
    serviceSectID: str
    procedureCode: str  # 13866
    procedureName: str
    requestDate: str  # 最近一个月
    providerPhone: Optional[str]
    filmPrint: Optional[str]
    filmCount: int = 0
    placerOrderNO: str
    placerOrderDetailNO: str
    orderPatientID: str=''
    orderUID: str=''
    invisitTimes: int = 0
    visitUID: Optional[str]
    filmChargedCount: int = 0
    privacyLevel: int = 0
    patientType: Optional[str]
    hospitalStaffFlag: Optional[str]
    multiDrugFastFlag: Optional[str]
    isolationLevel: Optional[str]
    fallScore: Optional[str]
    painScore: Optional[str]
    transportationMode: Optional[str]
    emergencygrading: Optional[str]
    inPatientNO: Optional[str]
    ward: Optional[str]
    sickRoom: Optional[str]
    bedNO: Optional[str]
    inHospitalFlag: Optional[str]
    physicalNO: Optional[str]
    diseaseDiagnosisCode: Optional[str]
    diseaseDiagnosisName: Optional[str]


class ElectronicList(BaseModel):
    isSuccess: bool = True
    resultDesc: str = "获得成功"
    resultJson: list[ElectronicInfo]
    currentPage: int
    pageSize: int
    totalRecords: int
    token: str = None


if __name__ == "__main__":
    # st = StudyData(**dict(workQueueGuid='1' patientId='32156' patientName='张颜值'))
    # print(st.model_dump())
    # print(st.model_dump_json())
    pass
