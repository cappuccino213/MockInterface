"""
@File : request_model.py
@Date : 2023/7/12 16:23
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from typing import Optional, List

from pydantic import BaseModel, Field

"""使用Pydantic来构造请求体模型"""

"""随访系统"""


class FollowUpInfo(BaseModel):
    id_card: str
    name: str
    is_follow: str
    testing_facility: Optional[str]


"""IMCIS"""


class RequestReport(BaseModel):
    RePrint: Optional[bool] = False
    ExamDate: Optional[str] = ''
    ExamEndDate: Optional[str] = ''
    BussinessTime: Optional[str] = ''
    BussinessEndTime: Optional[str] = ''
    OrganizationID: str = 'QWYHZYFZX'
    CardType: Optional[str] = ''
    CardNo: str
    TypeCode: str = 'ExamResult'
    ClassCode: Optional[str] = ''
    BusinessType: Optional[str] = ''
    ServiceSectID: Optional[list] = Field(default_factory=list)
    ResultStatusCode: list = Field(['3080', '4030'])
    DelayMin: Optional[str] = ''
    ExamLocation: Optional[str] = ''
    SearchType: int = 0
    ExamDeptIDs: Optional[str] = ''
    LockTime: int = 0


"""Token"""


class RequestToken(BaseModel):
    ProductName: str
    HospitalCode: Optional[str]
    RequestIP: Optional[str] = None  # None表示可以不提供该参数

    class Config:
        json_schema_extra = {
            "example": {
                "ProductName": "eWordRIS",
                "HospitalCode": "QWYHZYFZX",
                "RequestIP": "127.0.0.1"
            }
        }


class RequestOld(BaseModel):
    RequestIP: str
    audience: Optional[str]
    CustomData: Optional[str]
    Expire: Optional[int]

    class Config:
        json_schema_extra = {
            "example": {
                "RequestIP": "127.0.0.1",
                "audience": "eWordRIS",
                "CustomData": "",
                "Expire": 2}
        }


# 产品注册
class ProductRegister(BaseModel):
    HospitalCode: str
    ProductName: str


"""DEP"""


class RequestElectronic(BaseModel):
    PlacerOrderNO: Optional[str] = None  # 申请单号
    SystemCode: str = 'RIS'
    OrganizationHISCode: str = 'QWYHZYFZX'
    OrganizationName: str = '全网云杭州研发中心'
    ServiceSectID: str = 'CR|MG|MR|DR|CT|XA|TJ|RF|XB'
    PatientClass: Optional[str] = None  # 申请单列表获取，就诊类别：1000-门诊 2000-住院 3000-急诊 4000-体检 5000-VIP
    MedrecNo: Optional[str] = None  # 病历号
    StartTime: Optional[str] = None
    EndTime: Optional[str] = None
    Ward: Optional[str]
    ObservationLocation: Optional[str]
    ChargeFlag: int = 0
    FilterRegistered: bool = False
    PatientName: Optional[str]
    SearchType: Optional[str] = None  # 输入号码获取，在RIS的输入框切换对应查询库，其中1-门诊  2-住院  4-体检 7-全部
    CardSelfNO: Optional[str] = None  # 就诊卡号


class NotifyToHISJsonRequest(BaseModel):
    PlacerOrderNO: str


"""Archive"""


class RequestImportOrders(BaseModel):
    AccessionNumber: str
    PatientID: str
    PatientName: str
    PatientSex: str
    PatientBirthDate: str
    PatientType: int
    OrganizationCode: str
    FormType: int
    FileData: List[str]


class RequestGetStudyApplyImage(BaseModel):
    AccessionNumber: str
    PatientID: str
    OrganizationCode: str
    FormType: int


"""HttpProxy"""


class APIRequestProxy(BaseModel):
    api_path: str
    method: str
    body: dict = Field(default={})
    headers: dict = Field(default={'Content-Type': 'application/json'})
    params: dict = Field(default={})


if __name__ == "__main__":
    pass
