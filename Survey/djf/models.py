import random, string
from collections import namedtuple

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import app_settings
from .utils import create_star

TYPE_FIELD = namedtuple(
    'TYPE_FIELD', 'text number radio select multi_select text_area url email date rating'
)._make(range(10))


def generate_unique_slug(klass, field, id, identifier='slug'):
    """
    Generate unique slug.
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    mapping = {
        identifier: unique_slug,
    }
    obj = klass.objects.filter(**mapping).first()
    while obj:
        if obj.id == id:
            break
        rnd_string = random.choices(string.ascii_lowercase, k=(len(unique_slug)))
        unique_slug = '%s-%s-%d' % (origin_slug, ''.join(rnd_string[:10]), numb)
        mapping[identifier] = unique_slug
        numb += 1
        obj = klass.objects.filter(**mapping).first()
    return unique_slug


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Survey(BaseModel):
    name = models.CharField(_("Название"), max_length=200)
    description = models.TextField(_("Описание"), default='', blank=True, null=True)
    slug = models.SlugField(_("slug"), max_length=225, default='')
    editable = models.BooleanField(_("Редактируемый"), default=True, help_text=_("Если False, пользователь не может редактировать запись"))
    deletable = models.BooleanField(_("Удаляемый"), default=True, help_text=_("Если False, пользователь не может удалить запись"))
    duplicate_entry = models.BooleanField(_("Несколько представлений"), default=False, help_text=_("Если True, пользователь может повторно отправить"))
    private_response = models.BooleanField(_("частный ответ"), default=False, help_text=_("Если True, только администратор и владелец могут получить доступ"))
    can_anonymous_user = models.BooleanField(_("Анонимный опрос"), default=False, help_text=_("Если True, пользователь без аутентификации может пройти опрос"))

    class Meta:
        verbose_name = _("опрос")
        verbose_name_plural = _("опросы")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = generate_unique_slug(Survey, self.slug, self.id)
        else:
            self.slug = generate_unique_slug(Survey, self.name, self.id)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("опрос")
        verbose_name_plural = _("опросы")


class Question(BaseModel):
    TYPE_FIELD = [
        (TYPE_FIELD.text, _("Text")),
        (TYPE_FIELD.number, _("Number")),
        (TYPE_FIELD.radio, _("Radio")),
        (TYPE_FIELD.select, _("Select")),
        (TYPE_FIELD.multi_select, _("Multi Select")),
        (TYPE_FIELD.text_area, _("Text Area")),
        (TYPE_FIELD.url, _("URL")),
        (TYPE_FIELD.email, _("Email")),
        (TYPE_FIELD.date, _("Date")),
        (TYPE_FIELD.rating, _("Rating"))
    ]

    key = models.CharField(_("key"), max_length=225, unique=True, null=True, blank=True, help_text=_("Уникальный ключ для этого вопроса. Заполните поле, если вы хотите использовать его для автоматической генерации"))
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE, verbose_name=_("Опрос"))
    label = models.CharField(_("label"), max_length=500, help_text=_("Введите свой вопрос здесь"))
    type_field = models.PositiveSmallIntegerField(_("тип поля ввода"), choices=TYPE_FIELD)
    choices = models.TextField(
        _("choices"),
        blank=True, null=True,
        help_text=_("Если тип поля — радио, выбор или множественный выбор, заполните параметры, разделенные запятыми. Например: мужчина, женщина")
    )
    help_text = models.CharField(
        _("help text"),
        max_length=200, blank=True, null=True,
        help_text=_("Здесь вы можете добавить текст справки")
    )
    required = models.BooleanField(_("Обязательный"), default=True, help_text=_("Если True, пользователь должен дать ответ на этот вопрос"))
    ordering = models.PositiveIntegerField(_("Выбор"), default=0, help_text=_("Определяет порядок вопросов в опросах"))

    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.label}-survey-{self.survey.id}"

    def save(self, *args, **kwargs):
        if self.key:
            self.key = generate_unique_slug(Question, self.key, self.id, "key")
        else:
            self.key = generate_unique_slug(Question, self.label, self.id, "key")

        super(Question, self).save(*args, **kwargs)


class UserAnswer(BaseModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("survey"))
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("user"))

    class Meta:
        verbose_name = _("Ответ пользователя")
        verbose_name_plural = _("Ответы пользователей")
        ordering = ["-updated_at"]

    def __str__(self):
        return str(self.id)

    def get_user_photo(self):
        if app_settings.SURVEY_USER_PHOTO_PROFILE:
            return eval(app_settings.SURVEY_USER_PHOTO_PROFILE)
        return "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"


class Answer(BaseModel):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE, verbose_name=_("answer"))
    value = models.TextField(_("значение"), help_text=_("Значение ответа, данного пользователем"))
    user_answer = models.ForeignKey(UserAnswer, on_delete=models.CASCADE, verbose_name=_("user answer"))

    class Meta:
        verbose_name = _("Ответ")
        verbose_name_plural = _("Ответы")
        ordering = ["question__ordering"]

    def __str__(self):
        return f"{self.question}: {self.value}"

    @property
    def get_value(self):
        if self.question.type_field == TYPE_FIELD.rating:
            return create_star(active_star=int(self.value))
        elif self.question.type_field == TYPE_FIELD.url:
            return mark_safe(f'<a href="{self.value}" target="_blank">{self.value}</a>')
        elif self.question.type_field == TYPE_FIELD.radio or self.question.type_field == TYPE_FIELD.select or \
                self.question.type_field == TYPE_FIELD.multi_select:
            return self.value.strip().replace("_", " ").capitalize()
        else:
            return self.value

    @property
    def get_value_for_csv(self):
        if self.question.type_field == TYPE_FIELD.radio or self.question.type_field == TYPE_FIELD.select or \
                self.question.type_field == TYPE_FIELD.multi_select:
            return self.value.strip().replace("_", " ").capitalize()
        else:
            return self.value.strip()

