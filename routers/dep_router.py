"""
@File : dep_router.py
@Date : 2023/7/27 16:17
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import datetime

from fastapi import APIRouter

from request_model import RequestElectronic, NotifyToHISJsonRequest
from response_model import ElectronicList, ElectronicInfo, NotifyToHIS
from utility import fake_data
from config import CONFIG

"""数据交换平台mock"""
dep_route = APIRouter(tags=['DEP'])


@dep_route.post('/api/Electronic/ElectronicList', name="获取电子申请单", response_model=ElectronicList)
def get_electronic_list(request_electronic: RequestElectronic):
    def get_elec_info():
        result_dict = dict(
            medrecNo=fake_data.medical_info()['medrecNo'],
            invoceNO=fake_data.medical_info()['invoiceNO'],
            cardSelfNO=fake_data.medical_info()['cardSelfNO'],
            patientID=fake_data.medical_info()['patientID'],
            name=fake_data.person_info()['name'],
            birthDate=fake_data.person_info()['birth'],
            sex='M' if fake_data.person_info()['sex'] == '男性' else 'F',
            # 'Male' if fake_data.person_info()['sex'] == '男性' else 'Female'
            age=fake_data.person_info()['age'],
            ageUnit=fake_data.person_info()['ageUnit'],
            idCard=fake_data.person_info()['ID'],
            nation=fake_data.person_info()['nation'],
            nationality=fake_data.person_info()['nationality'],
            maritalStatus=fake_data.person_info()['maritalStatus'],
            # isPregnant = fake_data.person_info()['isPregnant'],
            insuranceType=fake_data.medical_info()['insuranceType'],
            insuranceID=fake_data.medical_info()['insuranceID'],
            clinicDiagnosis=fake_data.medical_info()['clinicDiagnosis'],
            symptom=fake_data.medical_info()['symptom'],
            charges=fake_data.medical_info()['charges'],
            requestDeptName=fake_data.medical_info()['requestDeptName'],
            providerName=fake_data.person_info()['name'],
            patientClass=fake_data.medical_info()['patientClass'],
            serviceSectID=fake_data.medical_info()['serviceSectID'],
            procedureCode=fake_data.medical_info()['procedureCode'],
            procedureName=fake_data.medical_info()['procedureName'],
            placerOrderNO=fake_data.medical_info()['placerOrderNO'],
            placerOrderDetailNO=fake_data.medical_info()['placerOrderDetailNO'],
            requestDate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S"')
        )
        return result_dict

    # 取电子单信息，根据申请单号生成
    if request_electronic.PlacerOrderNO:
        result_dict = get_elec_info()
        result_dict['placerOrderNO'] = request_electronic.PlacerOrderNO
        result_dict['placerOrderDetailNO'] = request_electronic.PlacerOrderNO + '-1'
        return ElectronicList(
            **dict(resultJson=[ElectronicInfo(**result_dict)], currentPage=1, pageSize=1, totalRecords=1))
    # 电子申请单列表，根据日期生成
    elif request_electronic.StartTime and request_electronic.EndTime:
        ele_list = []
        for _ in range(CONFIG['mockup']['response']['count']):
            result_dict = get_elec_info()
            result_dict['requestDate'] = fake_data.random_time(request_electronic.StartTime,
                                                               request_electronic.EndTime).strftime(
                "%Y-%m-%d %H:%M:%S")  # 根据申请时间生成对应区间的数据
            ele_list.append(ElectronicInfo(**result_dict))
        # ele_list = [ElectronicInfo(**result_dict) for _ in range(CONFIG['mockup']['response']['count'])]
        return ElectronicList(**dict(resultJson=ele_list), currentPage=1, pageSize=1, totalRecords=1)
    else:
        return ElectronicList(
            **dict(resultDesc="未查询到数据", currentPage=0, pageSize=0, totalRecords=0))


@dep_route.post('/api/Notify/NotifyHIS', name="通知HIS接口", response_model=NotifyToHIS)
def notify_to_his(request_notify_his: NotifyToHISJsonRequest):
    if request_notify_his.PlacerOrderNO:
        return NotifyToHIS(**dict(isSuccess=True, ResultDesc="通知HIS成功"))
    return NotifyToHIS(**dict(isSuccess=False, ResultDesc="通知HIS失败,申请单号未空"))


if __name__ == "__main__":
    pass
