from django import forms


class CheckboxSelectMultipleSurvey(forms.CheckboxSelectMultiple):
    option_template_name = 'djf/widgets/checkbox_option.html'


class RadioSelectSurvey(forms.RadioSelect):
    option_template_name = 'djf/widgets/radio_option.html'


class DateSurvey(forms.DateTimeInput):
    template_name = 'djf/widgets/datepicker.html'


class RatingSurvey(forms.HiddenInput):
    template_name = 'djf/widgets/star_rating.html'

