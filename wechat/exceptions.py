class WechatRequestError(RuntimeError):
    def __init__(self, message, errCode):
        message = '(errCode={}) '.format(errCode) + message
        super().__init__(message)
        self.errCode = errCode

