class NotAllQuestionsAnsweredException(Exception):
    def __init__(self):
        super().__init__('Not all questions were answered')


class NoUnfinishedUserTestException(Exception):
    def __init__(self):
        super().__init__('No unfinished user\'s test found')
