import json
from typing import Callable

import service_layer.exceptions
from application import Request
from presentation import show_questions, show_not_all_answered_questions_response, show_user_results
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
    if not request.cookies.get('username'):
        start_response('200 OK', [('Content-Type', 'text/html')])
        response = RESPONSE_TEMPLATE.format('<a href="http://uni_site.com">Ввести імʼя та прізвище</a>')
        return [response.encode()]
    with open('questions.json', 'r') as questions_file:
        questions = json.load(questions_file)
    response = RESPONSE_TEMPLATE.format(show_questions(questions, request.params))
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode()]


@router.route('/process_answers', methods=['POST'])
def process_answers(request: Request, start_response: Callable):
    try:
        correct_answers_percentage = services.process_answers(request.cookies.get('username'), request.params)
    except service_layer.exceptions.NotAllQuestionsAnsweredException:
        start_response('200 OK', [('Content-Type', 'text/html')])
        response = RESPONSE_TEMPLATE.format(show_not_all_answered_questions_response(request.params))
        return [response.encode()]
    except service_layer.exceptions.InvalidUsernameException:
        start_response('200 OK', [('Content-Type', 'text/html')])
        response = RESPONSE_TEMPLATE.format('<a href="http://uni_site.com">Ввести валідні імʼя та прізвище</a>')
        return [response.encode()]
    response = RESPONSE_TEMPLATE.format(
        f'<h2>Відсоток правильних відповідей: {correct_answers_percentage}%</h2><br>'
        '<a href="http://uni_site.com">На головну</a>'
    )
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode()]


@router.route('/my_results', methods=['GET'])
def get_user_results(request: Request, start_response: Callable):
    if not (username := request.cookies.get('username')):
        start_response('200 OK', [('Content-Type', 'text/html')])
        response = RESPONSE_TEMPLATE.format('<a href="http://uni_site.com">Ввести імʼя та прізвище</a>')
        return [response.encode()]
    with open('user_results.json', 'r') as f:
        try:
            user_results = json.load(f).get(username, [])
        except json.JSONDecodeError:
            user_results = []
    response = RESPONSE_TEMPLATE.format(show_user_results(username, user_results))
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode()]
