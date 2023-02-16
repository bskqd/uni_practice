import service_layer.exceptions
from adapters.repository import SQLAlchemyRepository
from authentication import authentication_required
from database.base import sessionmaker
from models import User, Question, UserTest, UserAnswer, Answer
from presentation import show_questions, show_user_results
from service_layer.testing import GetUserAnswersService, FinishUserTest
from service_layer.unit_of_work import SqlAlchemyUnitOfWork
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
def login(request: Request) -> ResponseABC:
    if not (username := request.body.get('username')):
        return SimpleResponse(400, 'Введіть імʼя та прізвище')
    uow = SqlAlchemyUnitOfWork(sessionmaker, users_repo=SQLAlchemyRepository(User))
    user_login_service = UserLoginService(uow)
    with uow:
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
def get_questions(request: Request) -> ResponseABC:
    uow = SqlAlchemyUnitOfWork(
        sessionmaker,
        users_repo=SQLAlchemyRepository(User),
        questions_repo=SQLAlchemyRepository(Question),
        user_tests_repo=SQLAlchemyRepository(UserTest),
        user_answers_repo=SQLAlchemyRepository(UserAnswer),
    )
    get_questions_service = GetUserAnswersService(uow)
    with uow:
        user_answers = get_questions_service(request.session.get('username'))
        response = RESPONSE_TEMPLATE.format(show_questions(user_answers))
    return SimpleResponse(200, response)


@router.route('/process_answers', methods=['POST'])
@authentication_required
def process_answers(request: Request) -> ResponseABC:
    uow = SqlAlchemyUnitOfWork(
        sessionmaker,
        users_repo=SQLAlchemyRepository(User),
        questions_repo=SQLAlchemyRepository(Question),
        answers_repo=SQLAlchemyRepository(Answer),
        user_tests_repo=SQLAlchemyRepository(UserTest),
        user_answers_repo=SQLAlchemyRepository(UserAnswer),
    )
    finish_user_test_service = FinishUserTest(uow)
    with uow:
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
        except service_layer.exceptions.InvalidUsernameException:
            content = '<a href="http://uni_site.com">Ввести валідні імʼя та прізвище</a>'
    return SimpleResponse(200,  RESPONSE_TEMPLATE.format(content))


@router.route('/my_results', methods=['GET'])
@authentication_required
def get_user_results(request: Request) -> ResponseABC:
    username = request.session['username']
    uow = SqlAlchemyUnitOfWork(sessionmaker, user_tests_repo=SQLAlchemyRepository(UserTest))
    get_user_tests_service = GetUserTestsService(uow)
    with uow:
        user_tests = get_user_tests_service(username)
        response = RESPONSE_TEMPLATE.format(show_user_results(username, user_tests))
    return SimpleResponse(200, response)
