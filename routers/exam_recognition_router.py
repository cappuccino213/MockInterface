"""
@File : exam_recognition_router.py
@Date : 2024/11/26 11:09
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
from fastapi import APIRouter, Header, Depends, Body, HTTPException
from pydantic import ValidationError

from request_model import RequestGetRelativeReports, RequestGetDetails, RequestGetDenyReasons, \
    RequestUploadRecognizedResult
from config import CONFIG

recognition_route = APIRouter(tags=["检查互认"], prefix="/api/report")

rec_config = CONFIG.get("business").get("recognition")


# 定义一个依赖项来获取请求头
def validate_request_header(
        clientId: str = Header(..., title="clientId", regex=r"^\S+$"),  # 使用正则表达式确保是非空字符串
        orgCode: str = Header(..., title="orgCode", regex=r"^\S+$"),
        timestamp: str = Header(..., title="timestamp", regex=r"^\d+$"),  # 假设时间戳是数字字符串
        sign: str = Header(..., title="sign", regex=r"^\S+$")):
    try:
        # 验证签名和机构
        if sign == rec_config["sign"] and orgCode == rec_config["org_code"]:
            headers = {
                "clientId": clientId,
                "orgCode": orgCode,
                "timestamp": timestamp,
                "sign": sign
            }
            return headers
        raise HTTPException(status_code=401, detail="机构或签名信息验证失败")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 请求体验证逻辑方法
def validate_get_relative_reports(params: dict):
    if params.get("patientName") != rec_config["patient_name"]:
        return False
    if params.get("idCardNo") != rec_config["id_card"]:
        return False
    if params.get("organizationCode") != rec_config["org_code"]:
        return False
    if params.get("doctorName") != rec_config["doctor_name"]:
        return False
    if params.get("doctorCode") != rec_config["doctor_code"]:
        return False
    return True


# 获取患者相关检查列表
@recognition_route.post("/getRelativeReports", name="获取患者相关检查列表")
async def get_relative_reports(request_body: RequestGetRelativeReports = Body(...),
                               headers=Depends(validate_request_header)):
    request_dict = request_body.model_dump()
    print(f"请求接口参数: {request_dict}")
    if validate_get_relative_reports(request_dict):
        return {"code": "0",
                "message": "success",
                "data": [
                    {
                        "patientName": request_body.patientName,
                        "idCardNo": request_body.idCardNo,
                        "organizationCode": request_body.organizationCode,
                        "organizationName": "全网云杭州研发中心",
                        "gender": "男",
                        "age": "30",
                        "examUid": "202411261111",
                        "examDate": "2024-11-26 12:00:00",
                        "examItemName": "头颅平扫",
                        "resultAssistantName": "报告医生",
                        "preliminaryDate": "2024-11-26 14:00:00",
                        "modality": "CT",
                        "area": "杭州"
                    }
                ]}
    return {"code": "1", "message": "未查询到患者信息", "data": []}


def validate_get_detail(params: dict):
    if params.get("patientName") != rec_config["patient_name"]:
        return False
    if params.get("idCardNo") != rec_config["id_card"]:
        return False
    if params.get("organizationCode") != rec_config["org_code"]:
        return False
    if params.get("doctorName") != rec_config["doctor_name"]:
        return False
    if params.get("examUid") != rec_config["exam_uid"]:
        return False
    if params.get("area") != rec_config["area"]:
        return False
    return True


# 获取检查报告详情
@recognition_route.post("/getDetail", name="获取检查报告详情")
async def get_details(request_body: RequestGetDetails = Body(...), headers=Depends(validate_request_header)):
    request_dict = request_body.model_dump()
    print(f"请求接口参数: {request_dict}")
    if validate_get_detail(request_dict):
        return {
            "code": "0",
            "message": "success",
            "data": [
                {
                    "patientName": request_body.patientName,
                    "idCardNo": request_body.idCardNo,
                    "organizationCode": request_body.organizationCode,
                    "organizationName": "全网云杭州研发中心",
                    "gender": "男",
                    "age": "30",
                    "examUid": "202411261111",
                    "providerName": "王栋",
                    "requestDeptName": "脑科",
                    "requestOrgName": "申请者机构名称",
                    "requestDate": "2024-11-26 11:00:00",
                    "examDate": "2024-11-26 12:00:00",
                    "examItemName": "头颅平扫",
                    "examItemCode": "ct-tlps",
                    "modality": "CT",
                    "technicianName": "技师名称",
                    "resultAssistantName": "报告医生",
                    "preliminaryDate": "审核医生",
                    "resultPrincipalName": "2024-11-26 14:00:00",
                    "auditDate": "2024-11-26 16:00:00",
                    "imagingFinding": "两侧大脑半球对称，脑实质内未见异常密度影，脑沟脑室系统未见增宽扩大，中线结构居中。颅骨未见明显异常。",
                    "imagingDiagnosis": "颅脑CT平扫颅内未见异常。",
                    "imageUrl": "http://192.168.1.18:8221/imageView?strPatientID=CT-00036610&strAccessionNumber=6074024&strModality=CT&strStudyInstanceUID=1.2.86.76547135.7.6083352.20230330110000",
                    "area": "杭州"
                }
            ]}
    return {"code": "1", "message": "未查询到患者信息", "data": []}


def validate_get_deny_reasons(params: dict):
    if params.get("organizationCode") != rec_config["organization_code"]:
        return False
    return True


# 获取不互认原因
@recognition_route.post("/getDenyReasons", name="获取不互认原因")
async def get_deny_reasons(request_body: RequestGetDenyReasons, headers=Depends(validate_request_header)):
    request_dict = request_body.model_dump()
    print(f"请求接口参数: {request_dict}")
    if validate_get_deny_reasons(request_dict):
        data_list = [
            {"reasonCode": "1", "reasonDescription": "因病情变化，已有的检查结果无法反映患者目前病情"},
            {"reasonCode": "2", "reasonDescription": "因时效问题，已有的检查结果难以提供参考价值的项目"},
            {"reasonCode": "3", "reasonDescription": "检查结果与疾病发展关联程度高、变化幅度大的项目"}
        ]
        return {"code": "0",
                "message": "不互认原因",
                "data": data_list}
    return {"code": "1", "message": "不互认原因", "data": [{"reasonCode": "9", "reasonDescription": "未找到对应机构信息"}]}


def validate_upload_recognized_result(params: dict):
    if params.get("organizationCode") != rec_config["organization_code"]:
        return False, "organizationCode有误"
    elif params.get("doctorName") != rec_config["doctor_name"]:
        return False, "doctorName有误"
    elif params.get("isRecognized"):
        if params.get("examUid") == rec_config["exam_uid"] and params.get("area") == rec_config["area"]:
            message = "互认结果，上传成功"
            print(message)
            return True, message
        return False, "examUid或area有误"

    else:
        if params.get("reasonCode") and params.get("reasonMark"):
            message = "不互认结果，上传成功"
            print(message)
            return True, message
        else:
            return False, "reasonCode或reasonMark不能为空"


# 上传互认原因结果
@recognition_route.post("/uploadRecognizedResult", name="上传互认结果")
async def upload_recognized_result(request_body: RequestUploadRecognizedResult,
                                   headers=Depends(validate_request_header)):
    request_dict = request_body.model_dump()
    print(f"请求接口参数：{request_dict}")
    result, msg = validate_upload_recognized_result(request_dict)
    if result:
        return {"code": "0", "message": msg}
    return {"code": "1", "message": msg}
