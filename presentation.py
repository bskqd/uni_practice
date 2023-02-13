from typing import Optional, Union

from models import UserAnswer, Question


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
            f'{"checked" if user_answer.answer_id else ""}>'
            f'<label for="{answer.id}">{answer.text}</label><br>'
        )
        if answer_index == len(user_answer.question.answers) - 1:
            response += '<br>'
    return response


def show_not_all_answered_questions_response(answered_questions: dict) -> str:
    response = '<h1>Ви відповіли не на всі запитання, <a href="http://uni_site.com/questions?'
    for index, (question_id, answer) in enumerate(answered_questions.items()):
        character = '' if index == 0 else '&'
        if isinstance(answer, list):
            for answer_id in answer:
                response += f'{character}{question_id}={answer_id}'
            continue
        response += f'{character}{question_id}={answer}'
    response += '">допройти тест</a></h1>'
    return response


def show_user_results(username:str, user_results: list[dict, ...]) -> str:
    response = f'<h1>{username}, результати:<br></h1>'
    for result in user_results:
        response += f'Дата та час: {result["datetime"]}, Результат: {result["result"]}%<br>'
    response += '<br><a href="http://uni_site.com">На головну</a>'
    return response
