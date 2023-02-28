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
@provide_uow
def login(request: Request, uow: AbstractUnitOfWork) -> ResponseABC:
    if not (username := request.body.get('username')):
        return SimpleResponse(400, 'Введіть імʼя та прізвище')
    user_login_service = UserLoginService(uow)
    user_login_service(username)
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
@provide_uow
def get_questions(request: Request, uow: AbstractUnitOfWork) -> ResponseABC:
    get_user_test_answers_service = GetUserTestAnswers(uow)
    user_answers = get_user_test_answers_service(request.session.get('username'))
    response = RESPONSE_TEMPLATE.format(show_questions(user_answers))
    return SimpleResponse(200, response)


@router.route('/process_answers', methods=['POST'])
@authentication_required
@provide_uow
def process_answers(request: Request, uow: AbstractUnitOfWork) -> ResponseABC:
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
    return SimpleResponse(200,  RESPONSE_TEMPLATE.format(content))


@router.route('/my_results', methods=['GET'])
@authentication_required
@provide_uow
def get_user_results(request: Request, uow: AbstractUnitOfWork) -> ResponseABC:
    username = request.session['username']
    get_user_tests_service = GetUserTestsService(uow)
    user_tests = get_user_tests_service(username)
    response = RESPONSE_TEMPLATE.format(show_user_results(username, user_tests))
    return SimpleResponse(200, response)
