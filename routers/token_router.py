"""
@File : app_router.py
@Date : 2023/7/12 16:24
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import jwt

import requests

from fastapi import APIRouter

from config import CONFIG
from request_model import RequestToken, RequestOld
from response_model import Token, ValidateToken, CheckStatus, RegisterInfo

"""token服务模拟"""
"""
注意：
1此授权服务仅作为公司内测试使用
2不得私自向外部署
3出现违规行为，自负法律责任
"""

# Token系统
token_route = APIRouter(prefix="/Token", tags=['Token'])

product_route = APIRouter(tags=['Token'])

SECRET = "eWordTomTaw@HZ"

# 获取参数
config = CONFIG


def jwt_token(token_dict, secret=SECRET, algorithms="HS256"):
    """
    :param token_dict: payload
    :param secret: 密钥
    :param algorithms: 签名算法
    :return: token的字符串
    """
    token_value = "Bearer " + jwt.encode(token_dict, secret, algorithms)
    return token_value


# 尝试获取真实的token，若返回401错误，则返回{}，否则返回真实信息
def get_real_token(fetch_api: str, request_params: dict):
    real_token_host = config['proxy']['token_host']
    real_token_url = f"{real_token_host}{fetch_api}"
    try:
        response = requests.post(real_token_url, json=request_params)
        if response:
            if response.json()['status'] == 0:
                print(f"INFO：产品信息{request_params}已注册，返回真实的token信息")
                return response.json()
        print(f"WARNING:{response.text}")
        return {}
    except Exception as e:
        print(f"ERROR:{e}")
        return {}


# 校验是否注册
@product_route.get('/Product/CheckProductRegisterStateByHospital', name="校验产品注册情况", response_model=CheckStatus)
def check_product_register(hospitalCode: str, productName: str):
    register_info = dict(count=500, productName=productName, version="V1.0",
                         hospitalName=hospitalCode)
    check_result = dict(registerInfo=RegisterInfo(**register_info), desc="success", status=0)
    return CheckStatus(**check_result)


@token_route.post('/RetriveInternal', name="获取令牌", response_model=Token,
                  description="优先返回真实token信息，若未注册则返回mock的token")
def retrieve_internal_token(request_token: RequestToken):
    # 先尝试获取真实的token
    real_token = get_real_token("/Token/RetriveInternal", request_token.model_dump())
    if real_token:
        return Token(**real_token)
    token_body = dict(token=jwt_token(request_token.model_dump()), desc="success", status=0)
    return Token(**token_body)


@token_route.post('/ValidateInternal', name="验证令牌", response_model=ValidateToken)
def validate_internal_token(request_token: RequestToken):
    validate_result = dict(desc="成功", status=0)
    return ValidateToken(**validate_result)


# 兼容老版本token接口
@token_route.post('/Retrive', name="获取令牌（老版本）", response_model=Token,
                  description="优先返回真实token信息，若未注册则返回mock的token")
def retrieve_token(request_token: RequestOld):
    real_token = get_real_token("/Token/Retrive", request_token.model_dump())
    if real_token:
        return Token(**real_token)
    token_body = dict(token=jwt_token(request_token.model_dump()), desc="success", status=0)
    return Token(**token_body)


@token_route.post('/Validate', name="验证令牌(老版本)", response_model=ValidateToken,
                  description="优先返回真实token信息，若未注册则返回mock的token")
def validate_token():
    validate_result = dict(desc="成功", status=0)
    return ValidateToken(**validate_result)


# 产品之间验证
@token_route.post('/RetriveInteractive', name="产品间获取令牌", response_model=Token)
def retrieve_interactive_token(request_token: RequestToken):
    real_token = get_real_token("/Token/RetriveInteractive", request_token.model_dump())
    if real_token:
        return Token(**real_token)
    token_body = dict(token=jwt_token(request_token.model_dump()), desc="success", status=0)
    return Token(**token_body)


@token_route.post('/ValidateInteractive', name="产品间验证令牌", response_model=ValidateToken)
def validate_interactive_token(request_token: RequestToken):
    validate_result = dict(desc="成功", status=0)
    return ValidateToken(**validate_result)


if __name__ == "__main__":
    pass
    print(jwt_token({
        "ProductName": "eWordIMCIS",
        "HospitalCode": "QWYHZYFZX",
        "RequestIP": "192.168.1.56"
    }))
