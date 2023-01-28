import json
from typing import Callable

import service_layer.exceptions
from application import Request
from presentation import show_question, show_not_all_answered_questions_response
from routing import Router
from service_layer import services

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
        response += show_question(question_id, question_data, request.query_params.get(question_id))
    response += '<input type="submit" value="Надіслати відповіді"></form>'
    response = RESPONSE_TEMPLATE.format(response)
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode()]


@router.route('/process_answers', methods=['POST'])
def process_answers(request: Request, start_response: Callable):
    try:
        correct_answers_percentage = services.process_answers(request.body)
    except service_layer.exceptions.NotAllQuestionsAnsweredException:
        start_response('200 OK', [('Content-Type', 'text/html')])
        response = RESPONSE_TEMPLATE.format(show_not_all_answered_questions_response(request.body))
        return [response.encode()]
    response = RESPONSE_TEMPLATE.format(
        f'<h2>Відсоток правильних відповідей: {correct_answers_percentage}%</h2><br>'
        '<a href="http://uni_site.com">На головну</a>'
    )
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode()]
