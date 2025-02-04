"""The module contains the screens the bot consists of."""

import json
import random

import aiofiles

from hammett.conf import settings
from hammett.core import Button, Screen
from hammett.core.constants import SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.utils.translation import gettext as _
from hammett.widgets import MultiChoiceWidget, SingleChoiceWidget
from hammett.widgets.base import BaseChoiceWidget


class BaseScreen(Screen):
    """The base screen for all the screens in the bot."""

    hide_keyboard = True

    caption = ''

    async def get_description(self, _update, context):
        """Return the translated description of the screen."""
        language_code = context.user_data.get('language_code', 'en')
        return _(self.caption, language_code)

    @staticmethod
    def get_next_choice_widget(next_correct_answer):
        """Return the widget screen according to the type of answer to
        the next question.
        """
        return (
            QuizMultiChoiceWidget
            if isinstance(next_correct_answer, list)
            else QuizSingleChoiceWidget
        )


class BaseQuizScreen(BaseScreen, BaseChoiceWidget):
    """The base screen for all the screens participating in the quiz."""

    async def add_extra_keyboard(self, _update, context):
        """Add an extra keyboard below the widget buttons."""
        language_code = context.user_data.get('language_code', 'en')
        return [[
            Button(
                _('🏠 Main Menu', language_code),
                MainMenuScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE),
            Button(
                _('Next ➡️', language_code),
                self.next_question,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE),
        ]]

    async def get_choices(self, _update, context, **_kwargs):
        """Return the choices with the available answers to the question."""
        index = context.user_data['question_index']
        questions = context.user_data['questions']

        result = []
        for i, answer in enumerate(questions[index]['answers']):
            result.append((i, answer))

        return tuple(result)

    async def get_description(self, _update, context):
        """Return the `description` attribute of the screen."""
        index = context.user_data['question_index']
        questions = context.user_data['questions']
        language_code = context.user_data.get('language_code', 'en')

        return (
            f'№ <b>{index + 1}/{len(context.user_data["questions"])}.</b> '
            f'{questions[index]["question"][language_code]}'
        )

    @register_button_handler
    async def next_question(self, update, context):
        """Check the answer and switch to the next question or to the screen
        with the results of the completed quiz.
        """
        index = context.user_data['question_index']
        questions = context.user_data['questions']

        if (
            # List with selected answers must be sorted to be equal with the correct answer
            isinstance(context.user_data['answer'], list) and
            sorted(context.user_data['answer']) == questions[index]['correct_answer']
        ) or (
            context.user_data['answer'] == questions[index]['correct_answer']
        ):
            context.user_data['correct_answers_num'] += 1

        context.user_data['question_index'] += 1

        try:  # Choose type of the next widget screen or finish the quiz
            next_correct_answer = questions[context.user_data['question_index']]['correct_answer']
        except IndexError:
            return await ResultScreen().move(update, context)

        return await self.get_next_choice_widget(next_correct_answer)().move(update, context)


class LanguageSwitcherScreen(BaseScreen, SingleChoiceWidget):
    """The class implements LanguageSwitcherScreen."""

    choices = (
        ('en', '🇬🇧 English'),
        ('pt-br', '🇧🇷 Português'),
        ('ru', '🇷🇺 Русский'),
    )

    caption = 'language_switcher_screen'

    async def add_extra_keyboard(self, _update, context):
        """Add an extra keyboard below the widget buttons."""
        language_code = context.user_data.get('language_code', 'en')
        return [[
            Button(
                _('⬅️ Back', language_code),
                MainMenuScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE),
        ]]

    async def get_initial_value(self, _update, context):
        """Return updated or default language code."""
        language_code = context.user_data.get('language_code', 'en')
        if not language_code:
            return 'en'

        return language_code

    async def switch(self, update, context, selected_choice):
        """Save the selected language and re-render the screen."""
        selected_language, _ = selected_choice
        context.user_data['language_code'] = selected_language

        return await super().switch(update, context, selected_choice)


class MainMenuScreen(BaseScreen, StartMixin):
    """The class implements MainMenuScreen."""

    caption = 'main_menu_screen'

    async def add_default_keyboard(self, _update, context):
        """Set up the default keyboard for the screen."""
        language_code = context.user_data.get('language_code', 'en')
        return [
            [Button(
                _('❓ Start Quiz', language_code),
                self.start_quiz_handler,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            )],
            [Button(
                _('🌍 Change Language', language_code),
                LanguageSwitcherScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE,
            )],
        ]

    async def render(self, update, context, *, config=None, **kwargs):
        """Initiate or reset necessary data and set new questions for the quiz."""
        context.user_data['question_index'] = \
        context.user_data['correct_answers_num'] = \
        context.user_data['answer'] = 0

        context.user_data['questions'] = random.sample(context.user_data['all_questions'], k=5)

        return await super().render(update, context, config=config, **kwargs)

    async def start(self, update, context):
        """Reply to the /start command, load and save the questions from the file."""
        async with aiofiles.open(settings.BASE_DIR / 'questions.json') as file:
            questions = json.loads(await file.read())
            context.user_data['all_questions'] = questions

        return await super().start(update, context)

    @register_button_handler
    async def start_quiz_handler(self, update, context):
        """Handle a request to start the quiz."""
        index = context.user_data['question_index']
        questions = context.user_data['questions']

        return await self.get_next_choice_widget(
            questions[index]['correct_answer'],
        )().move(update, context)


class QuizMultiChoiceWidget(BaseQuizScreen, MultiChoiceWidget):
    """The class implements QuizSingleChoiceWidget, which acts as a response
    if the question has more than one correct answer.
    """

    async def switch(self, update, context, selected_choice):
        """Save the passed answer and re-render the screen with the updated emoji
        of the clicked button.
        """
        answer, _ = selected_choice
        if isinstance(context.user_data.get('answer'), list):
            if answer in context.user_data['answer']:  # Answer was canceled
                context.user_data['answer'].remove(answer)
            else:
                context.user_data['answer'].append(answer)
        else:
            context.user_data['answer'] = [answer]

        return await super().switch(update, context, selected_choice)


class QuizSingleChoiceWidget(BaseQuizScreen, SingleChoiceWidget):
    """The class implements QuizSingleChoiceWidget, which acts as a response
    if the question has only one correct answer.
    """

    async def switch(self, update, context, selected_choice):
        """Save the passed answer and re-render the screen with the updated emoji
        of the clicked button.
        """
        answer, _ = selected_choice
        context.user_data['answer'] = answer

        return await super().switch(update, context, selected_choice)


class ResultScreen(BaseScreen):
    """The class implements ResultScreen."""

    caption = 'result_screen'

    async def add_default_keyboard(self, _update, context):
        """Set up the default keyboard for the screen."""
        language_code = context.user_data.get('language_code', 'en')
        return [[
            Button(_('🏠 Main Menu', language_code), MainMenuScreen,
                   source_type=SourcesTypes.MOVE_SOURCE_TYPE),
        ]]

    async def get_description(self, update, context):
        """Return the `description` attribute of the screen."""
        template = await super().get_description(update, context)
        return template.format(
            correct_answers_num=context.user_data['correct_answers_num'],
            questions_num=len(context.user_data['questions']),
        )
