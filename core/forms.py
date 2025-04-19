from django import forms

class AnilistLinkForms(forms.Form):
    anilist_url = forms.URLField(
        label='Anilist URL',
        max_length=200,
        widget=forms.URLInput(attrs={
            'placeholder': 'https://anilist.co/anime/123456/Your-Anime-Title',
            'class': 'form-control'
        }),
        error_messages={
            'required': 'Please enter a valid Anilist URL.',
            'invalid': 'Please enter a valid URL.'
        }
    )

class UserDataForm(forms.Form):
    pass