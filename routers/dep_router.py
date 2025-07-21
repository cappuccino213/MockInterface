"""
@File : dep_router.py
@Date : 2023/7/27 16:17
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime
import random

from fastapi import APIRouter

from request_model import RequestElectronic, NotifyToHISJsonRequest
from response_model import ElectronicList, ElectronicInfo, NotifyToHIS
from utility import fake_data
from config import CONFIG

"""数据交换平台mock"""
dep_route = APIRouter(tags=['DEP'])


@dep_route.post('/api/Electronic/ElectronicList', name="获取电子申请单", response_model=ElectronicList)
def get_electronic_list(request_electronic: RequestElectronic):
    def get_electronic_info():
        medical_info = fake_data.medical_info()
        person_info = fake_data.person_info()
        date_format = '%Y-%m-%d %H:%M:%S'
        return {
            'medrecNo': medical_info['medrecNo'],
            'invoceNO': medical_info['invoiceNO'],
            'cardSelfNO': medical_info['cardSelfNO'],
            'patientID': medical_info['patientID'],
            'name': person_info['name'],
            'birthDate': person_info['birth'],
            # 'birthDate': "",
            'sex': 'M' if person_info['sex'] == '男性' else 'F',
            'age': person_info['age'],
            'ageUnit': person_info['ageUnit'],
            'idCard': person_info['ID'],
            'nation': person_info['nation'],
            'nationality': person_info['nationality'],
            'maritalStatus': person_info['maritalStatus'],
            'insuranceType': medical_info['insuranceType'],
            'insuranceID': medical_info['insuranceID'],
            'clinicDiagnosis': medical_info['clinicDiagnosis'],
            'symptom': medical_info['symptom'],
            'charges': medical_info['charges'],
            'requestDeptName': medical_info['requestDeptName'],
            # 'providerName': person_info['name'],
            'providerName': "申请医生",
            'patientClass': medical_info['patientClass'],
            'serviceSectID': medical_info['serviceSectID'],
            'procedureCode': medical_info['procedureCode'],
            'procedureName': medical_info['procedureName'],
            'placerOrderNO': medical_info['placerOrderNO'],
            'placerOrderDetailNO': medical_info['placerOrderDetailNO'],
            'requestDate': datetime.datetime.now().strftime(date_format)
        }

    # --根据入参修改生成数据--
    # -输入号码获取数据
    # 定义根据查询类型指定就诊类别数据
    def get_patient_class(search_type: str) -> str:
        if search_type == '1':
            return '1000'
        elif search_type == '2':
            return '2000'
        elif search_type == '4':
            return '4000'
        else:
            return random.Random().choice(['1000', '2000', '3000', '4000'])

    # 根据申请单号生成
    if request_electronic.PlacerOrderNO:
        result_dict = get_electronic_info()
        result_dict['placerOrderNO'] = request_electronic.PlacerOrderNO
        result_dict['placerOrderDetailNO'] = request_electronic.PlacerOrderNO + '-1'
        result_dict['patientClass'] = get_patient_class(request_electronic.SearchType)
        return ElectronicList(
            **dict(resultJson=[ElectronicInfo(**result_dict)], currentPage=1, pageSize=1, totalRecords=1))
    # 根据病历号生成
    if request_electronic.MedrecNo:
        result_dict = get_electronic_info()
        result_dict['medrecNo'] = request_electronic.MedrecNo
        result_dict['patientClass'] = get_patient_class(request_electronic.SearchType)
        return ElectronicList(
            **dict(resultJson=[ElectronicInfo(**result_dict)], currentPage=1, pageSize=1, totalRecords=1))
    # 根据就诊卡号生成
    if request_electronic.CardSelfNO:
        result_dict = get_electronic_info()
        result_dict['cardSelfNO'] = request_electronic.CardSelfNO
        result_dict['patientClass'] = get_patient_class(request_electronic.SearchType)
        return ElectronicList(
            **dict(resultJson=[ElectronicInfo(**result_dict)], currentPage=1, pageSize=1, totalRecords=1))

    # -电子申请单列表获取-
    # 电子申请单列表，根据日期生成
    if request_electronic.StartTime and request_electronic.EndTime:
        ele_list = []
        for _ in range(CONFIG['mockup']['response']['count']):
            result_dict = get_electronic_info()
            # 判断是否有就诊类别要求(入参0表示无要求，随机返回)
            if request_electronic.PatientClass != '0':
                result_dict['patientClass'] = request_electronic.PatientClass

            # 判断是否有检查类型要求（空字符表示无要求）
            if request_electronic.ServiceSectID:
                result_dict['serviceSectID'] = request_electronic.ServiceSectID

            result_dict['requestDate'] = fake_data.random_time(request_electronic.StartTime,
                                                               request_electronic.EndTime).strftime(
                "%Y-%m-%d %H:%M:%S")  # 根据申请时间生成对应区间的数据
            ele_list.append(ElectronicInfo(**result_dict))
        # ele_list = [ElectronicInfo(**result_dict) for _ in range(CONFIG['mockup']['response']['count'])]
        return ElectronicList(**dict(resultJson=ele_list), currentPage=1, pageSize=1, totalRecords=1)

    return ElectronicList(
        **dict(resultDesc="未查询到数据", currentPage=0, pageSize=0, totalRecords=0))


@dep_route.post('/api/Notify/NotifyHIS', name="通知HIS接口", response_model=NotifyToHIS)
def notify_to_his(request_notify_his: NotifyToHISJsonRequest):
    if request_notify_his.PlacerOrderNO:
        return NotifyToHIS(**dict(isSuccess=True, ResultDesc="通知HIS成功"))
    return NotifyToHIS(**dict(isSuccess=False, ResultDesc="通知HIS失败,申请单号未空"))


if __name__ == "__main__":
    pass
