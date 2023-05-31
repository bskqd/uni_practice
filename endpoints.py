from jinja2 import Environment

import service_layer.exceptions
from authentication import authentication_required
from presentation import show_questions, show_user_results
from providers import provide_uow
from service_layer.testing import GetUserTestAnswers, FinishUserTest
from service_layer.unit_of_work import AbstractUnitOfWork
from service_layer.users import UserLoginService, GetUserTestsService
from wsgi_application.application import Request, SimpleResponse, ResponseABC
from wsgi_application.routing import Router

router = Router()


@router.route('/login', methods=['POST'])
@provide_uow
def login(request: Request, uow: AbstractUnitOfWork, environment: Environment) -> ResponseABC:
    if not (username := request.body.get('username')):
        return SimpleResponse(request, 400, 'Введіть імʼя та прізвище')
    user_login_service = UserLoginService(uow)
    user_login_service(username)
    response = SimpleResponse(
        request,
        200,
        environment.get_template('base.html').render(
            body=(
                'Успішно. <a href="http://uni_site.com/questions">Пройти тест</a> '
                '<a href="http://uni_site.com">На головну</a>'
            )
        ),
    )
    response.set_session({'username': username})
    return response


@router.route('/questions', methods=['GET'])
@authentication_required
@provide_uow
def get_questions(request: Request, uow: AbstractUnitOfWork, environment: Environment) -> ResponseABC:
    get_user_test_answers_service = GetUserTestAnswers(uow)
    user_answers = get_user_test_answers_service(request.session.get('username'))
    response = environment.get_template('base.html').render(body=show_questions(user_answers))
    return SimpleResponse(request, 200, response)


@router.route('/process_answers', methods=['POST'])
@authentication_required
@provide_uow
def process_answers(request: Request, uow: AbstractUnitOfWork, environment: Environment) -> ResponseABC:
    finish_user_test_service = FinishUserTest(uow)
    try:
        correct_answers_percentage = finish_user_test_service(request.session['username'], request.body)
        content = (
            f'<h2>Відсоток правильних відповідей: {correct_answers_percentage}%</h2><br>'
            '<a href="http://uni_site.com">На головну</a>'
        )
    except service_layer.exceptions.NotAllQuestionsAnsweredException:
        content = (
            '<h1>Ви відповіли не на всі запитання, <a href="http://uni_site.com/questions">допройти тест</a></h1>'
        )
    except service_layer.exceptions.NoUnfinishedUserTestException:
        content = '<a href="http://uni_site.com">Не знайдено тесту від такого користувача</a>'
    return SimpleResponse(request, 200,environment.get_template('base.html').render(body=content))


@router.route('/my_results', methods=['GET'])
@authentication_required
@provide_uow
def get_user_results(request: Request, uow: AbstractUnitOfWork, environment: Environment) -> ResponseABC:
    username = request.session['username']
    get_user_tests_service = GetUserTestsService(uow)
    user_tests = get_user_tests_service(username)
    response = environment.get_template('base.html').render(body=show_user_results(username, user_tests))
    return SimpleResponse(request, 200, response)
