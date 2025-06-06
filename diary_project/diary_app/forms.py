# diary_app/forms.py
from django import forms
from .models import User, MoodEntry, Event, DiaryPage


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'password', 'email']


class FilterByEmotionForm(forms.Form):
    emotion = forms.ChoiceField(required=False, label="Choose an emotion:", choices=(("", "All"), ) )
    """+ tuple(MoodEntry.MOOD_CHOICES)"""


class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['text', 'emotion']
        widgets = {
            'emotion': forms.Select(attrs={'class': 'form-control'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date']


class DiaryPageForm(forms.ModelForm):
    class Meta:
        model = DiaryPage
        fields = ['date', 'content']