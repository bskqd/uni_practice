from models import UserAnswer, Question, UserTest


def show_questions(user_answers: list[UserAnswer]) -> str:
    response = '<form action="/process_answers" method="post">'
    for user_answer in user_answers:
        response += show_question(user_answer)
    response += '<input type="submit" value="Надіслати відповіді"></form>'
    return response


def show_question(user_answer: UserAnswer) -> str:
    response = f'<h3><label for="{user_answer.question_id}">{user_answer.question.text}</label></h3>'
    for answer_index, answer in enumerate(user_answer.question.answers):
        response += (
            f'<input type="{"checkbox" if user_answer.question.type == Question.QuestionTypes.MULTI else "radio"}"'
            f'id="{answer.id}" name="{user_answer.question_id}" value="{answer.id}"'
            f'{"checked" if answer in user_answer.answers else ""}>'
            f'<label for="{answer.id}">{answer.text}</label><br>'
        )
        if answer_index == len(user_answer.question.answers) - 1:
            response += '<br>'
    return response


def show_user_results(username:str, user_tests: list[UserTest]) -> str:
    response = f'<h1>{username}, результати:<br></h1>'
    for user_test in user_tests:
        response += f'Дата та час: {user_test.finished_at}, Результат: {user_test.result}%<br>'
    response += '<br><a href="http://uni_site.com">На головну</a>'
    return response
