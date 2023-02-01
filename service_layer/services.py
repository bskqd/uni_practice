import json
from datetime import datetime
from typing import Union

from service_layer.exceptions import NotAllQuestionsAnsweredException, InvalidUsernameException


def process_answers(username: str, answers: dict[str, Union[str, list[str, ...]]]) -> int:
    if not username:
        raise InvalidUsernameException
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
    result = round((correct_answers / len(questions)) * 100)
    update_user_results(username, result)
    return result


def update_user_results(username: str, result: int):
    with open('user_results.json', 'r') as f:
        try:
            user_results = json.load(f)
        except json.JSONDecodeError:
            user_results = {}
    user_results.setdefault(username, []).append({'result': result, 'datetime': str(datetime.now())})
    with open('user_results.json', 'w') as f:
        json.dump(user_results, f)
