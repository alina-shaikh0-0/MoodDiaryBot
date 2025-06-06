# diary_app/urls.py
from django.urls import path
from .views import register, profile,  mood_entry_list, mood_entry_create, mood_entry_edit, mood_entry_delete, event_list, event_create, event_edit, event_delete, diary_page_list, diary_page_create, diary_page_edit, diary_page_delete


app_name = 'diary_app'

urlpatterns = [
    # Auth routes
    path('register/', register, name='register'),

    path('profile/', profile, name='profile'),  # Добавляем маршрут для профиля

    # CRUD operations for MoodEntry
    path('mood_entries/', mood_entry_list, name='mood_entry_list'),
    path('mood_entries/create/', mood_entry_create, name='mood_entry_create'),
    path('mood_entries/<int:pk>/edit/', mood_entry_edit, name='mood_entry_edit'),
    path('mood_entries/<int:pk>/delete/', mood_entry_delete, name='mood_entry_delete'),

    # CRUD operations for Event
    path('events/', event_list, name='event_list'),
    path('events/create/', event_create, name='event_create'),
    path('events/<int:pk>/edit/', event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', event_delete, name='event_delete'),

    # CRUD operations for DiaryPage
    path('diary_pages/', diary_page_list, name='diary_page_list'),
    path('diary_pages/create/', diary_page_create, name='diary_page_create'),
    path('diary_pages/<int:pk>/edit/', diary_page_edit, name='diary_page_edit'),
    path('diary_pages/<int:pk>/delete/', diary_page_delete, name='diary_page_delete'),
]