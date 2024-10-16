class BaseException(Exception):
    def __init__(self, type: str, msg: str):
        self.type = type
        self.msg = msg
        super().__init__(msg)

    def getResult(self):
        data = {}
        result = {
            "result": False,
            "data": data
        }
        if self.type is not None:
            data["type"] = self.type
        if self.msg is not None:
            data["msg"] = self.msg
        
        return result

# 파라미터 유효성 Exception
class InvalidParamException(BaseException):
    def __init__(self, type: str = "invalid_data", msg: str = "invalid data"):
        super().__init__(type, msg)
        self.type = type
        self.msg = msg

# ai 사용량 초과 Exception
class ExceedAiReqException(BaseException):
    def __init__(self, type: str = "exceed_count", msg: str = "usage exceed"):
        super().__init__(type, msg)
        self.type = type
        self.msg = msg

# 답변 불가 Exception
class UnanswerableAiException(BaseException):
    def __init__(self, type: str = None, msg: str = None):
        super().__init__(type, msg)
        self.type = type
        self.msg = msg