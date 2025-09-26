"""
@File    : dep_router_test.py
@Date    : 2025/9/26 14:38
@Author  : 九层风（Yeah Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime
import random
import logging

from fastapi import APIRouter

from request_model import RequestElectronic, NotifyToHISJsonRequest
from response_model import ElectronicList, ElectronicInfo, NotifyToHIS
from utility import fake_data
from config import CONFIG

"""数据交换平台mock"""
dep_route = APIRouter(tags=['DEP'])

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_electronic_info_with_prepared_data(medical_info, person_info):
    """使用预生成数据的get_electronic_info函数"""
    date_format = '%Y-%m-%d %H:%M:%S'
    result = {
        'medrecNo': medical_info['medrecNo'],
        'invoceNO': medical_info['invoiceNO'],
        'cardSelfNO': medical_info['cardSelfNO'],
        'patientID': medical_info['patientID'],
        'name': person_info['name'],
        'birthDate': person_info['birth'],
        'sex': 'M' if person_info['sex'] == '男性' else 'F',
        'age': person_info['age'],
        'ageUnit': "",
        'idCard': person_info['ID'],
        'nation': person_info['nation'],
        'nationality': person_info['nationality'],
        'maritalStatus': person_info['maritalStatus'],
        'insuranceType': medical_info['insuranceType'],
        'insuranceID': medical_info['insuranceID'],
        'inHospitalFlag': '1',
        'clinicDiagnosis': medical_info['clinicDiagnosis'],
        'symptom': medical_info['symptom'],
        'charges': medical_info['charges'],
        'requestDeptName': medical_info['requestDeptName'],
        'providerName': "申请医生",
        'patientClass': medical_info['patientClass'],
        'serviceSectID': medical_info['serviceSectID'],
        'procedureCode': medical_info['procedureCode'],
        'procedureName': medical_info['procedureName'],
        'placerOrderNO': medical_info['placerOrderNO'],
        'placerOrderDetailNO': medical_info['placerOrderDetailNO'],
        'requestDate': datetime.datetime.now().strftime(date_format)
    }
    return result

def get_patient_class(search_type: str) -> str:
    """获取患者类别"""
    if search_type == '1':
        return '1000'
    elif search_type == '2':
        return '2000'
    elif search_type == '4':
        return '4000'
    else:
        return random.Random().choice(['1000', '2000', '3000', '4000'])

@dep_route.post('/api/Electronic/ElectronicList', name="获取电子申请单", response_model=ElectronicList)
async def get_electronic_list(request_electronic: RequestElectronic):
    # 根据申请单号生成
    if request_electronic.PlacerOrderNO:
        medical_info = fake_data.medical_info()
        person_info = fake_data.person_info()
        result_dict = get_electronic_info_with_prepared_data(medical_info, person_info)
        result_dict['placerOrderNO'] = request_electronic.PlacerOrderNO
        result_dict['placerOrderDetailNO'] = request_electronic.PlacerOrderNO + '-1'
        result_dict['patientClass'] = get_patient_class(request_electronic.SearchType)
        return ElectronicList(
            **dict(resultJson=[ElectronicInfo(**result_dict)], currentPage=1, pageSize=1, totalRecords=1))

    # 根据病历号生成
    if request_electronic.MedrecNo:
        medical_info = fake_data.medical_info()
        person_info = fake_data.person_info()
        result_dict = get_electronic_info_with_prepared_data(medical_info, person_info)
        result_dict['medrecNo'] = request_electronic.MedrecNo
        result_dict['patientClass'] = get_patient_class(request_electronic.SearchType)
        return ElectronicList(
            **dict(resultJson=[ElectronicInfo(**result_dict)], currentPage=1, pageSize=1, totalRecords=1))

    # 根据就诊卡号生成
    if request_electronic.CardSelfNO:
        medical_info = fake_data.medical_info()
        person_info = fake_data.person_info()
        result_dict = get_electronic_info_with_prepared_data(medical_info, person_info)
        result_dict['cardSelfNO'] = request_electronic.CardSelfNO
        result_dict['patientClass'] = get_patient_class(request_electronic.SearchType)
        return ElectronicList(
            **dict(resultJson=[ElectronicInfo(**result_dict)], currentPage=1, pageSize=1, totalRecords=1))

    # 电子申请单列表获取，根据日期生成
    if request_electronic.StartTime and request_electronic.EndTime:
        # 获取DEP配置
        dep_config = CONFIG['dep']

        # 判断是否需要返回相同病人不同检查项目的数据
        has_multi_examitem = dep_config['ele_apply_list']['has_multi_examitem']

        if not has_multi_examitem:
            # 不需要多检查项目，正常生成指定数量的数据
            count = dep_config['ele_apply_list']['response_count']

            ele_list = []
            for i in range(count):
                medical_info = fake_data.medical_info()
                person_info = fake_data.person_info()
                result_dict = get_electronic_info_with_prepared_data(medical_info, person_info)

                # 应用筛选条件
                if request_electronic.PatientClass != '0':
                    result_dict['patientClass'] = request_electronic.PatientClass
                if request_electronic.ServiceSectID:
                    result_dict['serviceSectID'] = request_electronic.ServiceSectID

                result_dict['requestDate'] = fake_data.random_time(
                    request_electronic.StartTime,
                    request_electronic.EndTime
                ).strftime("%Y-%m-%d %H:%M:%S")
                ele_list.append(ElectronicInfo(**result_dict))

            return ElectronicList(**dict(resultJson=ele_list), currentPage=1, pageSize=len(ele_list),
                                  totalRecords=len(ele_list))
        else:
            # 需要多检查项目，按索引分段生成
            total_count = dep_config['ele_apply_list']['response_count']
            multi_examitem_num = dep_config['ele_apply_list']['multi_examitem_num']

            # 确保多检查项目数量不超过总数
            multi_examitem_num = min(multi_examitem_num, total_count)

            ele_list = []

            # 预先生成基础数据（用于多检查项目部分）
            if multi_examitem_num > 0:
                base_medical_info = fake_data.medical_info()
                base_person_info = fake_data.person_info()

                # 生成第一条基础数据
                date_format = '%Y-%m-%d %H:%M:%S'
                base_result_dict = {
                    'medrecNo': base_medical_info['medrecNo'],
                    'invoceNO': base_medical_info['invoiceNO'],
                    'cardSelfNO': base_medical_info['cardSelfNO'],
                    'patientID': base_medical_info['patientID'],
                    'name': base_person_info['name'],
                    'birthDate': base_person_info['birth'],
                    'sex': 'M' if base_person_info['sex'] == '男性' else 'F',
                    'age': base_person_info['age'],
                    'ageUnit': "",
                    'idCard': base_person_info['ID'],
                    'nation': base_person_info['nation'],
                    'nationality': base_person_info['nationality'],
                    'maritalStatus': base_person_info['maritalStatus'],
                    'insuranceType': base_medical_info['insuranceType'],
                    'insuranceID': base_medical_info['insuranceID'],
                    'inHospitalFlag': '1',
                    'clinicDiagnosis': base_medical_info['clinicDiagnosis'],
                    'symptom': base_medical_info['symptom'],
                    'charges': base_medical_info['charges'],
                    'requestDeptName': base_medical_info['requestDeptName'],
                    'providerName': "申请医生",
                    'patientClass': base_medical_info['patientClass'],
                    'serviceSectID': base_medical_info['serviceSectID'],
                    'procedureCode': base_medical_info['procedureCode'],
                    'procedureName': base_medical_info['procedureName'],
                    'placerOrderNO': base_medical_info['placerOrderNO'],
                    'placerOrderDetailNO': base_medical_info['placerOrderDetailNO'],
                    'requestDate': fake_data.random_time(
                        request_electronic.StartTime,
                        request_electronic.EndTime
                    ).strftime(date_format)
                }

                # 应用筛选条件到基础数据
                if request_electronic.PatientClass != '0':
                    base_result_dict['patientClass'] = request_electronic.PatientClass
                if request_electronic.ServiceSectID:
                    base_result_dict['serviceSectID'] = request_electronic.ServiceSectID

                ele_list.append(ElectronicInfo(**base_result_dict))

                # 生成其余的多检查项目数据（相同病人，不同检查项目）
                for i in range(1, multi_examitem_num):
                    new_medical_info = fake_data.medical_info()

                    # 创建基于基础数据的新记录，仅更改检查项目相关字段
                    multi_result_dict = base_result_dict.copy()
                    multi_result_dict.update({
                        'procedureCode': new_medical_info['procedureCode'],
                        'procedureName': new_medical_info['procedureName'],
                        'placerOrderNO': new_medical_info['placerOrderNO'],
                        'placerOrderDetailNO': new_medical_info['placerOrderNO'] + '-1',
                        'serviceSectID': new_medical_info['serviceSectID'],
                        'clinicDiagnosis': new_medical_info['clinicDiagnosis'],
                        'symptom': new_medical_info['symptom'],
                        'charges': new_medical_info['charges'],
                        'requestDeptName': new_medical_info['requestDeptName']
                    })

                    # 更新请求日期
                    multi_result_dict['requestDate'] = fake_data.random_time(
                        request_electronic.StartTime,
                        request_electronic.EndTime
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    ele_list.append(ElectronicInfo(**multi_result_dict))

            # 生成剩余的普通数据
            remaining_count = total_count - multi_examitem_num
            if remaining_count > 0:
                for i in range(remaining_count):
                    medical_info = fake_data.medical_info()
                    person_info = fake_data.person_info()
                    result_dict = get_electronic_info_with_prepared_data(medical_info, person_info)

                    # 应用筛选条件
                    if request_electronic.PatientClass != '0':
                        result_dict['patientClass'] = request_electronic.PatientClass
                    if request_electronic.ServiceSectID:
                        result_dict['serviceSectID'] = request_electronic.ServiceSectID

                    result_dict['requestDate'] = fake_data.random_time(
                        request_electronic.StartTime,
                        request_electronic.EndTime
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    ele_list.append(ElectronicInfo(**result_dict))

            return ElectronicList(**dict(resultJson=ele_list), currentPage=1, pageSize=len(ele_list),
                                  totalRecords=len(ele_list))

    # 无结果时返回
    return ElectronicList(
        **dict(resultDesc="未查询到数据", currentPage=0, pageSize=0, totalRecords=0))

# 消息通知接口
@dep_route.post('/api/Notify/NotifyHIS', name="通知HIS接口", response_model=NotifyToHIS)
def notify_to_his(request_notify_his: NotifyToHISJsonRequest):
    if request_notify_his.PlacerOrderNO:
        return NotifyToHIS(**dict(isSuccess=True, ResultDesc="通知HIS成功"))
    return NotifyToHIS(**dict(isSuccess=False, ResultDesc="通知HIS失败,申请单号未空"))
