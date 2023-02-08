import json

import service_layer.exceptions
from application import RequestABC, SimpleResponse, ResponseABC
from authentication import authentication_required
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


@router.route('/login', methods=['POST'])
def login(request: RequestABC) -> ResponseABC:
    if not (username := request.params.get('username')):
        return SimpleResponse(400, 'Введіть імʼя та прізвище')
    response = SimpleResponse(
        200,
        RESPONSE_TEMPLATE.format(
            'Успішно. '
            '<a href="http://uni_site.com/questions">Пройти тест</a>'
            '<a href="http://uni_site.com">На головну</a>'
        ),
    )
    response.set_session({'username': username})
    return response


@router.route('/questions', methods=['GET'])
@authentication_required
def get_questions(request: RequestABC) -> ResponseABC:
    with open('questions.json', 'r') as questions_file:
        questions = json.load(questions_file)
    response = RESPONSE_TEMPLATE.format(show_questions(questions, request.params))
    return SimpleResponse(200, response)


@router.route('/process_answers', methods=['POST'])
@authentication_required
def process_answers(request: RequestABC) -> ResponseABC:
    try:
        correct_answers_percentage = services.process_answers(request.session['username'], request.params)
    except service_layer.exceptions.NotAllQuestionsAnsweredException:
        response = RESPONSE_TEMPLATE.format(show_not_all_answered_questions_response(request.params))
        return SimpleResponse(200, response)
    except service_layer.exceptions.InvalidUsernameException:
        response = RESPONSE_TEMPLATE.format('<a href="http://uni_site.com">Ввести валідні імʼя та прізвище</a>')
        return SimpleResponse(200, response)
    response = RESPONSE_TEMPLATE.format(
        f'<h2>Відсоток правильних відповідей: {correct_answers_percentage}%</h2><br>'
        '<a href="http://uni_site.com">На головну</a>'
    )
    return SimpleResponse(200, response)


@router.route('/my_results', methods=['GET'])
@authentication_required
def get_user_results(request: RequestABC) -> ResponseABC:
    username = request.session['username']
    with open('user_results.json', 'r') as f:
        try:
            user_results = json.load(f).get(username, [])
        except json.JSONDecodeError:
            user_results = []
    response = RESPONSE_TEMPLATE.format(show_user_results(username, user_results))
    return SimpleResponse(200, response)
