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
    personal_rating = forms.FloatField(
        min_value=0,
        max_value=10,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Your Rating (0-10)',
            'class': 'form-control',
            'step': '0.1'
        }),
    )

    review = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Your Review',
            'class': 'form-control',
            'rows': 3
        }),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Your Notes',
            'class': 'form-control',
            'rows': 3
        }),
    )

    download_link_1080p = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': '1080p Download Link',
            'class': 'form-control'
        }),
    )

    download_link_720p = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': '720p Download Link',
            'class': 'form-control'
        }),
    )

    download_link_480p = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': '480p Download Link',
            'class': 'form-control'
        }),
    )

    download_link_360p = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': '360p Download Link',
            'class': 'form-control'
        }),
    )