import json

import service_layer.exceptions
from presentation import show_questions, show_not_all_answered_questions_response, show_user_results
from service_layer import services
from wsgi_application.application import Request, SimpleResponse, ResponseABC
from wsgi_application.authentication import authentication_required
from wsgi_application.routing import Router

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
def login(request: Request) -> ResponseABC:
    if not (username := request.body.get('username')):
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
def get_questions(request: Request) -> ResponseABC:
    with open('questions.json', 'r') as questions_file:
        questions = json.load(questions_file)
    response = RESPONSE_TEMPLATE.format(show_questions(questions, request.query_params))
    return SimpleResponse(200, response)


@router.route('/process_answers', methods=['POST'])
@authentication_required
def process_answers(request: Request) -> ResponseABC:
    try:
        correct_answers_percentage = services.process_answers(request.session['username'], request.body)
        content = (
            f'<h2>Відсоток правильних відповідей: {correct_answers_percentage}%</h2><br>'
            '<a href="http://uni_site.com">На головну</a>'
        )
    except service_layer.exceptions.NotAllQuestionsAnsweredException:
        content = show_not_all_answered_questions_response(request.body)
    except service_layer.exceptions.InvalidUsernameException:
        content = '<a href="http://uni_site.com">Ввести валідні імʼя та прізвище</a>'
    return SimpleResponse(200,  RESPONSE_TEMPLATE.format(content))


@router.route('/my_results', methods=['GET'])
@authentication_required
def get_user_results(request: Request) -> ResponseABC:
    username = request.session['username']
    with open('user_results.json', 'r') as f:
        try:
            user_results = json.load(f).get(username, [])
        except json.JSONDecodeError:
            user_results = []
    response = RESPONSE_TEMPLATE.format(show_user_results(username, user_results))
    return SimpleResponse(200, response)
