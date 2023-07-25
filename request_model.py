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


if __name__ == "__main__":
    pass
