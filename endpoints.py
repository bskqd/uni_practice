import json
from typing import Callable

from application import Request
from routing import Router

router = Router()

RESPONSE_TEMPLATE = (
    '<!DOCTYPE html>'
    '<html lang="en">'
    '<head>'
    '<meta charset="UTF-8">'
    '<title>Тестування</title>'
    '</head>'
    '<body>'
    '{}'
    '</body>'
    '</html>'
)


@router.route('/questions', methods=['GET'])
def get_questions(request: Request, start_response: Callable):
    with open('questions.json', 'r') as questions_file:
        questions = json.load(questions_file)
    response = '<form action="/process_answers" method="post">'
    for question_id, question_data in questions.items():
        response += f'<h3>{question_data["text"]}</h3>'
        for answer_index, answer in enumerate(question_data['answers']):
            response += (
                f'<input type="radio" id="{answer["id"]}" name="{question_id}" value="{answer["id"]}">'
                f'<label for="{answer["id"]}">{answer["label"]}</label><br>'
            )
            if answer_index == len(question_data['answers']) - 1:
                response += '<br>'
    response += '<input type="submit" value="Надіслати відповіді"></form>'
    response = RESPONSE_TEMPLATE.format(response)
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode()]


@router.route('/process_answers', methods=['POST'])
def process_answers(request: Request, start_response: Callable):
    with open('questions.json', 'r') as questions_file:
        questions = json.load(questions_file)
    correct_answers = 0
    for question_id, question_data in questions.items():
        try:
            given_answer = request.body[question_id]
        except KeyError:
            start_response('200 OK', [('Content-Type', 'text/html')])
            response = RESPONSE_TEMPLATE.format(
                '<h1>Ви відповіли не на всі запитання, '
                '<a href="http://uni_site.com/questions">пройти тест ще раз</a></h1>'
            )
            return [response.encode()]
        if given_answer == question_data['right_answer_id']:
            correct_answers += 1
    correct_answers_percentage = round((correct_answers / len(questions)) * 100)
    response = RESPONSE_TEMPLATE.format(
        f'<h2>Відсоток правильних відповідей: {correct_answers_percentage}%</h2><br>'
        '<a href="http://uni_site.com">На головну</a>'
    )
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode()]
