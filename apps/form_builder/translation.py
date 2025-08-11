from modeltranslation.translator import translator, TranslationOptions
from .models import DynamicForm, Page, QuestionType, Question


class DynamicFormTranslationOptions(TranslationOptions):
    fields = ('name',)


class PageTranslationOptions(TranslationOptions):
    fields = ('name',)


class QuestionTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class QuestionTranslationOptions(TranslationOptions):
    fields = ('name', 'text', 'subtext')


translator.register(DynamicForm, DynamicFormTranslationOptions)
translator.register(Page, PageTranslationOptions)
translator.register(QuestionType, QuestionTypeTranslationOptions)
translator.register(Question, QuestionTranslationOptions)