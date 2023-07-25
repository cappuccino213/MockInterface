"""
@File : app_router.py
@Date : 2023/7/12 16:24
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import jwt
from fastapi import APIRouter

from request_model import RequestToken
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


def jwt_token(token_dict, secret=SECRET, algorithms="HS256"):
    """
    :param token_dict: payload
    :param secret: 密钥
    :param algorithms: 签名算法
    :return: token的字符串
    """
    token_value = "Bearer " + jwt.encode(token_dict, secret, algorithms)
    return token_value


# 校验是否注册
@product_route.get('/Product/CheckProductRegisterStateByHospital', name="校验产品注册情况", response_model=CheckStatus)
def check_product_register(hospitalCode: str, productName: str):
    register_info = dict(count=500, productName=productName, version="V1.0",
                         hospitalName=hospitalCode)
    check_result = dict(registerInfo=RegisterInfo(**register_info), desc="success", status=0)
    return CheckStatus(**check_result)


@token_route.post('/RetriveInternal', name="获取令牌", response_model=Token)
def retrieve_token(request_token: RequestToken):
    token_body = dict(token=jwt_token(request_token.model_dump()), desc="success", status=0)
    return Token(**token_body)


@token_route.post('/ValidateInternal', name="验证令牌", response_model=ValidateToken)
def validate_token(request_token: RequestToken):
    validate_result = dict(desc="成功", status=0)
    return ValidateToken(**validate_result)


# 产品之间验证
@token_route.post('/RetriveInteractive', name="产品间获取令牌", response_model=Token)
def retrieve_interactive_token(request_token: RequestToken):
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
