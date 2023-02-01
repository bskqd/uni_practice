from typing import Optional, Union


def show_questions(questions: dict, selected_answers: dict[Union[str, list[str, ...]], ...]) -> str:
    response = '<form action="/process_answers" method="post">'
    for question_id, question_data in questions.items():
        if question_data['type'] == 'multi':
            response += show_multichoice_question(question_id, question_data, selected_answers.get(question_id) or [])
        else:
            response += show_single_choice_question(question_id, question_data, selected_answers.get(question_id))
    response += '<input type="submit" value="Надіслати відповіді"></form>'
    return response


def show_multichoice_question(question_id: str, question_data: dict, selected_answers: list[str, ...]) -> str:
    response = (
        f'<h3><label for="{question_id}">{question_data["text"]}</label></h3>'
        f'<select name="{question_id}" id="{question_id}" multiple>'
    )
    for answer_index, answer in enumerate(question_data['answers']):
        response += (
            f'<option value="{answer["id"]}" {"selected" if answer["id"] in selected_answers else ""}>'
            f'{answer["label"]}</option>'
        )
    response += '</select><br><br>'
    return response


def show_single_choice_question(question_id: str, question_data: dict, selected_answer: Optional[str]) -> str:
    response = f'<h3>{question_data["text"]}</h3>'
    for answer_index, answer in enumerate(question_data['answers']):
        response += (
            f'<input type="radio" id="{answer["id"]}" name="{question_id}" value="{answer["id"]}"'
            f'{"checked" if selected_answer == answer["id"] else ""}>'
            f'<label for="{answer["id"]}">{answer["label"]}</label><br>'
        )
        if answer_index == len(question_data['answers']) - 1:
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
