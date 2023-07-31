"""
@File : request_model.py
@Date : 2023/7/12 16:23
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from typing import Optional

from pydantic import BaseModel

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
    ServiceSectID: Optional[list] = []
    ResultStatusCode: list = ['3080', '4030']
    DelayMin: Optional[str] = ''
    ExamLocation: Optional[str] = ''
    SearchType: int = 0
    ExamDeptIDs: Optional[str] = ''
    LockTime: int = 0


"""Token"""


class RequestToken(BaseModel):
    ProductName: str
    HospitalCode: str
    RequestIP: str


# 产品注册
class ProductRegister(BaseModel):
    HospitalCode: str
    ProductName: str


"""DEP"""


class RequestElectronic(BaseModel):
    PlacerOrderNO: Optional[str]
    SystemCode: str = 'RIS'
    OrganizationHISCode: str = 'QWYHZYFZX'
    OrganizationName: str = '全网云杭州研发中心'
    ServiceSectID: Optional[str] = 'CR|MG|MR|DR|CT|XA|TJ|RF|XB'
    PatientClass: Optional[str] = '0'
    MedrecNo: Optional[str]
    StartTime: Optional[str]
    EndTime: Optional[str]
    Ward: Optional[str]
    ObservationLocation: Optional[str]
    ChargeFlag: int = 0
    FilterRegistered: bool = False
    PatientName: Optional[str]
    SearchType: Optional[str]  # 1-门诊  2-住院  4-体检 7-全部


if __name__ == "__main__":
    pass
