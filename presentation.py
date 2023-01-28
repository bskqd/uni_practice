from typing import Optional, Union


def show_question(question_id: str, question_data: dict, selected_answer: Optional[Union[str, list[str, ...]]]) -> str:
    if question_data['type'] == 'multi':
        return show_multichoice_question(question_id, question_data, selected_answer or [])
    return show_single_choice_question(question_id, question_data, selected_answer)


def show_multichoice_question(question_id: str, question_data: dict, selected_answers: list[str, ...]) -> str:
    output = ''
    output += (
        f'<h3><label for="{question_id}">{question_data["text"]}</label></h3>'
        f'<select name="{question_id}" id="{question_id}" multiple>'
    )
    for answer_index, answer in enumerate(question_data['answers']):
        output += (
            f'<option value="{answer["id"]}" {"selected" if answer["id"] in selected_answers else ""}>'
            f'{answer["label"]}</option>'
        )
    output += '</select><br><br>'
    return output


def show_single_choice_question(question_id: str, question_data: dict, selected_answer: Optional[str]) -> str:
    output = ''
    output += f'<h3>{question_data["text"]}</h3>'
    for answer_index, answer in enumerate(question_data['answers']):
        output += (
            f'<input type="radio" id="{answer["id"]}" name="{question_id}" value="{answer["id"]}"'
            f'{"checked" if selected_answer == answer["id"] else ""}>'
            f'<label for="{answer["id"]}">{answer["label"]}</label><br>'
        )
        if answer_index == len(question_data['answers']) - 1:
            output += '<br>'
    return output


def show_not_all_answered_questions_response(answered_questions: dict):
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
