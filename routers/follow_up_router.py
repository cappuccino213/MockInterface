"""
@File : follow_up_router.py
@Date : 2023/7/18 14:44
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""

from fastapi import APIRouter
from request_model import FollowUpInfo
from response_model import NoticeResult

follow_up_route = APIRouter(prefix="/mock/follow-up", tags=['Follow-up'])


# 测试时需要将DEP中的随访接口改成此接口（只有绍兴项目中有此设置），RIS设置通知随访
@follow_up_route.post("/notify/follow", name="通知随访", response_model=NoticeResult)
def notify_follow(notify_info: FollowUpInfo):
    if notify_info.is_follow == '0':
        result = NoticeResult(**dict(msg="取消随访成功"))
    elif notify_info.is_follow == '1':
        result = NoticeResult(**dict(msg="随访通知成功"))
    else:
        result = NoticeResult(**dict(msg="参数is_follow值有误"))
    return result


if __name__ == "__main__":
    pass
