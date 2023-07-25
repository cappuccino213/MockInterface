# 项目结构简介
- 开发背景是公司内经常会有产品间的api集成测试、或者与第三方的api对接测试，为了方便api的集成测试、保证业务场景数据流测试的完整性
## MockInterFace 项目目录
### routers 路由目录
- 根据mock的api分模块写路由
### static 静态文件目录
- report 自动生成报告文件
### main
- 注册路由
- 运行项目
### request_model api请求参数数据模型
- 基本是以router中的模块一一对应
### response_model api返回体数据模型
- 基本是以router中的模块一一对应
### utility 工具模块
- 所有代码中用到的工具均已class定义
- 如包括基于mimesis模块数据生成FakeData
- 各种数据处理方法集合Toolkit
### 配置文件
- config.toml配置文件
- config.py配置文件读取

# 技术栈简介
- PyVersion 此项目时在python3.9上开发的，理论上支持3.9+
- fastapi api接口的框架（自带swagger文档）
- uvicorn web服务运行
- pydantic 数据模型定义
	- 数据结构、类型定义
	- 数据结构、类型校验
- logoru 日志框架（待完善）
- toml 配置文件
- 其他
	- html转文件工具 wkhtmltopdf