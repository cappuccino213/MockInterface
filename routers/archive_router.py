"""
@File : archive_router.py
@Date : 2023/7/14 13:55
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""

from fastapi import APIRouter, Header, Depends, HTTPException, Body,Request

from request_model import RequestImportOrders, RequestGetStudyApplyImage, RequestFailedStudy, RequestDoManualMatch
from response_model import CompareFailList, StudyData, QASuccessResponse, QAFailResponse
from utility import *

from typing import Optional

"""接口定义"""
archive_route = APIRouter(tags=['Archive'])

real_archive_host = CONFIG['proxy']['archive_host']

archive_config = CONFIG['archive']

ris_config = CONFIG['ris']


# 定义一个依赖项来从Authorization请求头中提取token
async def get_token_from_header(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return authorization


def fake_compare_failed_list(request_body: RequestFailedStudy) -> StudyData:
    """根据请求参数构造一个模拟的 StudyData 对象"""

    def get_modality():
        if request_body.ExamType:
            types = request_body.ExamType.split('|')
            return random.choice(types) if len(types) > 1 else types[0]
        else:
            return fake_data.random_string(['CR', 'DR', 'CT', 'RF', 'XA', 'MR', 'MG'])

    # 基础字段映射规则：如果存在则取用户输入，否则 mock
    base_fields = {
        'organizationCode': lambda: request_body.OrganizationCode or archive_config.get("auth_product_info").get("HospitalCode"),
        'accessionNumber': lambda: request_body.AccessionNumber or fake_data.multi_type_number('custom', mask='#######'),
        'patientId': lambda: request_body.PatientID or fake_data.multi_type_number('custom', mask='FS#####'),
        'patientName': lambda: request_body.PatientName or fake_data.person_info()['name'],
        'modality': get_modality,
        'studyDateTime': lambda: (
            fake_data.random_date_in_range(request_body.StudyBeginDate, request_body.StudyEndDate)
            if request_body.StudyBeginDate and request_body.StudyEndDate
            else fake_data.random_date()
        ),
    }

    # 构建基础字段字典
    special_field_dict = {key: func() for key, func in base_fields.items()}

    # 固定其他字段（mock 数据）
    other_field_dict = {
        "patientAge": f"{fake_data.person_info()['age']}y",
        "patientBirthday": fake_data.person_info()['birth'],
        "patientSex": "Male" if fake_data.person_info()['sex'] == '男性' else 'Female',
        "workQueueGuid": fake_data.multi_type_number('uuid'),
        "studyInstanceUID": str(fake_data.multi_type_number('dicom')),
        "studyDescription": "",
        "errorDescription": "获取0条待比对检查信息",
        "otherName": ""
    }

    # 合并所有字段
    res_dict = {**special_field_dict, **other_field_dict}

    return StudyData(**res_dict)


# 获取archive的token
def get_internal_token():
    auth_info = CONFIG['ris']['auth_product_info'] # 这里需要用被调用方的产品信息
    result = TokenHandle().get_token_value(auth_info)
    print(f"INFO:     获取{CONFIG['ris']['auth_product_info']}的token信息：{result}")
    # return result.get('token').split(" ")[1]
    # 需要完整的token，所以不截取
    return result.get('token')

# 定义一个通知RIS归档完成的方法
def notify_ris_archive_complete(ris_url:str, request_body: dict):
    """
    :param ris_url:
    :param request_body:
    {
  "StudyInstanceUID": "1.2.194.0.108707908.20240730075934.1413.16898.2492438",
  "AccessionNumber": "28",
  "PatientID": "0000003",
  "MedrecNo": null,
  "OrganizationCode": "QWYHZYFZX",
  "AETitle": "mock_dicom",
  "OrganizationGuid": "3a0e58e2-da00-4a7a-bbdc-58a4bb3aaa81",
  "ObservationDate": "2024/7/30 8:43:43"
}
    :return:
    {
    "isSuccess": true,
    "resultDesc": "",
    "data": null}
    """
    api_path = "/api/Archive/Finish"
    token_value = get_internal_token()
    full_url = f"{ris_url}{api_path}"
    res = requests.post(url=full_url, json=request_body, headers={"Content-Type": "application/json", "Authorization": token_value})
    if res.status_code != 200:
        print(f"WARNING:     RIS归档完成通知失败，返回信息:{res.text}")
    print(f"INFO:     RIS归档完成通知结果:{res.json()}")
    return res.json()


@archive_route.post("/Exchange/DoManualMatch", name="手工比对", response_model=QASuccessResponse)
def do_manual_match(request:Request,request_body: RequestDoManualMatch = Body(...)):
    """
    接收手工比对数据,增加自动通知QA完成逻辑
    这里的请求方必须是真实的RIS服务，不能用接口工具测试，因为以下回通过请求获取地址，如果不在请求方的机器上使用接口测试，
    会导致获取的client_host，造成通知QA错误
    """
    client_host = ris_config.get('ris_url')
    # 配置从获取RIS服务端口信息
    client_port = ris_config.get('ris_port')
    # 拼接完整地址
    client_url = f"{client_host}:{client_port}"
    print(f"INFO:     手工匹配的请求方地址为:{client_url}")
    # 模拟的study_uid,若未获取到使用默认值
    mock_study_uid = CONFIG.get('archive').get('mock_studyinstanceuid',"1.2.194.0.108707908.20240730075934.1413.16898.1234567")

    # 构建通知参数
    notify_request_params = {
        "StudyInstanceUID": mock_study_uid, # 模拟固定uid值，无实际影像
        "AccessionNumber": request_body.MatchedData.AccessionNumber,
        "PatientID": request_body.MatchedData.PatientId,
        "MedrecNo": "",
        "OrganizationCode": archive_config.get("auth_product_info").get("HospitalCode"),
        "AETitle": "mock_ae",
        # "OrganizationGuid": "3a0e58e2-da00-4a7a-bbdc-58a4bb3aaa81",
        "ObservationDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    }
    # 先通知RIS归档完成
    notify_result = notify_ris_archive_complete(client_url,notify_request_params)
    # 然后返回手工比对成功结果
    if not notify_result.get('isSuccess'):
        return QAFailResponse(**dict(code=1, message=notify_result.get("message")))
    return QASuccessResponse(**dict(code=0, message="Success"))



@archive_route.post('/Exchange/GetCompareFailedStudy', name="获取QA阻塞列表", response_model=CompareFailList)
async def get_compare_failed_study(request_body: RequestFailedStudy = Body(...)):
    """增加根据入参返回数据的逻辑"""
    result_count = archive_config.get("response_count",20) # 从配置文件中获取返回结果数量，默认20
    study_list = [fake_compare_failed_list(request_body) for _ in range(result_count)]
    return CompareFailList(code=1, data=study_list, message="Success")



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
    print(f"TEST 存档配置信息:{archive_config}")
    print(f"TEST:{CONFIG['ris']['auth_product_info']}")
