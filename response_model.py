"""
@File : response_model.py
@Date : 2023/7/14 15:24
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime
import random
import time
from typing import List, Optional, Union, Any

from pydantic import BaseModel, Field

"""返回结果的数据模型"""

"""Archive"""
class QASuccessResponse(BaseModel):
    code: int = 0
    message: str = "Success"


class QAFailResponse(BaseModel):
    code: int
    message: str = "Fail"

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


class ImportOrderResponse(BaseModel):
    code: int
    message: str


class ImageData(BaseModel):
    imageData: str
    imageName: str


class ImageInfo(BaseModel):
    formType: int
    imageResult: list[ImageData]


class GetStudyApplyImageResponse(BaseModel):
    Data: list[ImageInfo]
    Code: int
    Message: str


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
    hospitalName: Optional[str] = Field(default='全网云杭州研发中心', description='医院名称')


# 校验产品注册
class CheckStatus(BaseModel):
    registerInfo: RegisterInfo
    desc: str
    status: int = 1


class Token(BaseModel):
    token: str
    desc: Union[str, Any] = None
    status: int = 1


class ValidateToken(BaseModel):
    desc: Union[str, Any] = None
    status: int = 1


"""DEP"""


# 电子申请单列表
class ElectronicInfo(BaseModel):
    medrecNo: str
    patientID: Optional[str]
    outPatientNO: Optional[str] = None  # 门诊类型有
    invoceNO: str
    cardSelfNO: str
    healthCardNO: Optional[str] = None
    name: str
    birthDate: str
    sex: str  # M 、F
    addressDetail: Optional[str] = None
    contactPhoneNO: Optional[str] = None
    age: int
    ageUnit: str
    idCard: str
    nation: str
    nationality: str
    maritalStatus: str
    isPregnant: int = 0  # 0 1
    adverseReaction: Optional[str] = None  # 不良反映
    insuranceType: str
    insuranceID: str
    inHospitalFlag: str
    medicalRecord: Optional[str] = None
    clinicDiagnosis: str
    symptom: str
    requestAttention: Optional[str] = None
    reasonforStudy: Optional[str] = None
    requestMemo: str = ''
    charges: float  # 50~165.0
    chargeFlag: str = "1"
    requestDeptName: str
    providerName: str
    patientClass: str  # 1000 2000
    serviceSectID: str
    procedureCode: str  # 13866
    procedureName: str
    requestDate: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 默认当天
    providerPhone: Optional[str] = None
    filmPrint: Optional[str] = None
    filmCount: int = 0
    placerOrderNO: Optional[str]
    placerOrderDetailNO: Optional[str]
    orderPatientID: str = ''
    orderUID: str = ''
    invisitTimes: int = 0
    visitUID: Optional[str] = None
    filmChargedCount: int = 0
    privacyLevel: int = 0
    patientType: Optional[str] = None
    hospitalStaffFlag: Optional[str] = None
    multiDrugFastFlag: Optional[str] = None
    isolationLevel: Optional[str] = None
    fallScore: Optional[str] = None
    painScore: Optional[str] = None
    transportationMode: Optional[str] = None
    emergencygrading: Optional[str] = None
    inPatientNO: Optional[str] = None
    ward: Optional[str] = None
    sickRoom: Optional[str] = None
    bedNO: Optional[str] = None
    inHospitalFlag: Optional[str] = None
    physicalNO: Optional[str] = None
    diseaseDiagnosisCode: Optional[str] = None
    diseaseDiagnosisName: Optional[str] = None


class ElectronicList(BaseModel):
    isSuccess: bool = True
    resultDesc: str = "获得成功"
    resultJson: Optional[list[ElectronicInfo]] = None
    currentPage: int
    pageSize: int
    totalRecords: int
    token: str = None


class NotifyToHIS(BaseModel):
    isSuccess: bool = True
    ResultDesc: str = "通知成功"
    ResultJson: dict = None


if __name__ == "__main__":
    # st = StudyData(**dict(workQueueGuid='1' patientId='32156' patientName='张颜值'))
    # print(st.model_dump())
    # print(st.model_dump_json())
    pass
