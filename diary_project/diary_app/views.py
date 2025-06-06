from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm, MoodEntryForm, EventForm, DiaryPageForm, FilterByEmotionForm
from .models import User, MoodEntry, Event, DiaryPage
from django.utils import timezone
from django.contrib.auth import login


# Create your views here.
def register(request):
    form = UserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('profile')
    else:
        form = UserForm()
    return render(request, 'register.html', {'form': form})


#view for profile
def profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('login')
    return render(request, 'confirm_delete.html')


def mood_entry_list(request):
    # filtration form
    filter_form = FilterByEmotionForm(request.GET)
    if filter_form.is_valid():
        selected_emotion = filter_form.cleaned_data.get('emotion')
        if selected_emotion:
            entries = MoodEntry.objects.filter(emotion=selected_emotion)
        else:
            entries = MoodEntry.objects.all()
    else:
        entries = MoodEntry.objects.all()
    return render(request, 'mood_entries.html', {'entries': entries, 'filter_form': filter_form})


def mood_entry_create(request):
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('mood_entry_list')
    else:
        form = MoodEntryForm()

    return render(request, 'mood_entry_form.html', {'form': form})


def mood_entry_edit(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk)
    form = MoodEntryForm(instance=entry)
    if request.method == 'POST':
        form = MoodEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('mood_entry_list')
    return render(request, 'mood_entry_form.html', {'form': form})


def mood_entry_delete(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk)
    if request.method == 'POST':
        entry.delete()
        return redirect('mood_entry_list')
    return render(request, 'confirm_delete.html', {'object': entry})


# Аналогично для Events и DiaryPages
# Вьюшки для модели Event
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events.html', {'events': events})


def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form})


def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {'form': form})


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'confirm_delete.html', {'object': event})


# Вьюшки для модели DiaryPage
def diary_page_list(request):
    pages = DiaryPage.objects.all()
    return render(request, 'diary_pages.html', {'pages': pages})


def diary_page_create(request):
    if request.method == 'POST':
        form = DiaryPageForm(request.POST)
        if form.is_valid():
            today = timezone.localdate()
            # Считаем количество записей за сегодняшний день
            count = DiaryPage.objects.filter(date=today).count()
            # Формируем заголовок
            title = f"{today:%d.%m.%Y} {count + 1}"

            entry = form.save(commit=False)
            entry.user = request.user
            entry.title = title  # Устанавливаем сформированный заголовок
            entry.save()
            return redirect('diary_page_list')
    else:
        form = DiaryPageForm()

    return render(request, 'diary_page_form.html', {'form': form})
    """form = DiaryPageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('diary_page_list')
    return render(request, 'diary_page_form.html', {'form': form})
"""


def diary_page_edit(request, pk):
    page = get_object_or_404(DiaryPage, pk=pk)
    if request.method == 'POST':
        form = DiaryPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('diary_page_list')
    else:
        form = DiaryPageForm(instance=page)

    return render(request, 'diary_page_form.html', {'form': form})
"""def diary_page_edit(request, pk):
    page = get_object_or_404(DiaryPage, pk=pk)
    form = DiaryPageForm(instance=page)
    if request.method == 'POST':
        form = DiaryPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('diary_page_list')
    return render(request, 'diary_page_form.html', {'form': form})
"""


def diary_page_delete(request, pk):
    page = get_object_or_404(DiaryPage, pk=pk)
    if request.method == 'POST':
        page.delete()
        return redirect('diary_page_list')
    return render(request, 'confirm_delete.html', {'object': page})