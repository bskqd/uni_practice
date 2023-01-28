class NotAllQuestionsAnsweredException(Exception):
    def __init__(self):
        super().__init__('Not all questions were answered')

