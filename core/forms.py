import re
from django import forms

class AnilistLinkForms(forms.Form):
    anilist_search = forms.CharField(
        label='Search Anime Title',
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Monogatari Series: Second Season',
            'class': 'form-control',
            'autocomplete': 'off',
            'autocorrect': 'off',
        }),
        error_messages={
            'required': 'Please enter a search term.',
            'invalid': 'Please enter a valid anime title.'
        }
    )

class UserDataForm(forms.Form):
    user_rating = forms.FloatField(
        min_value=0,
        max_value=10,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter your rating here... (0-10)',
            'class': 'form-control',
            'step': '0.1',
            'maxlength': '4',
        }),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your notes here... (max 200 characters)',
            'class': 'form-control',
            'rows': 3,
            'maxlength': '200',
        }),
    )

    link_1 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your link here... (max 50 characters)',
            'class': 'form-control',
            'maxlength': '50',
        }),
    )

    link_2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your link here... (max 50 characters)',
            'class': 'form-control',
            'maxlength': '50',
        }),
    )

    link_3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your link here... (max 50 characters)',
            'class': 'form-control',
            'maxlength': '50',
        }),
    )