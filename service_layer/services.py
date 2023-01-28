import json
from typing import Union

from service_layer.exceptions import NotAllQuestionsAnsweredException


def process_answers(answers: dict[str, Union[str, list[str, ...]]]) -> int:
    with open('questions.json', 'r') as questions_file:
        questions = json.load(questions_file)
    correct_answers = 0
    for question_id, question_data in questions.items():
        try:
            given_answer = answers[question_id]
        except KeyError:
            raise NotAllQuestionsAnsweredException
        if given_answer == question_data['right_answer_id']:
            correct_answers += 1
    return round((correct_answers / len(questions)) * 100)
