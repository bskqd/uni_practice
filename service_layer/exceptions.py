class NotAllQuestionsAnsweredException(Exception):
    def __init__(self):
        super().__init__('Not all questions were answered')


class InvalidUsernameException(Exception):
    def __init__(self):
        super().__init__('Invalid username provided')
