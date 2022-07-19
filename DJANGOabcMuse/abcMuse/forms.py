from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


class SliderForm(forms.Form):  # this is a form for values of both sliders on the main page
    consonants = forms.IntegerField(label='consonants', validators=[MinValueValidator(1), MaxValueValidator(30)])
    vowels = forms.IntegerField(label='vowels', validators=[MinValueValidator(1), MaxValueValidator(30)])


class WordForm(forms.Form):  # this is a form for
    onlyLetters = RegexValidator(r'^[a-zA-Z ]*$')  # input should contain only letters and spaces
    # input can be empty, maximum length of input - 200
    words = forms.CharField(label='words', max_length=200, required=False, validators=[onlyLetters])
