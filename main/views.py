from datetime import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .forms import RegisterForm, LoginForm, MedicineForm, MedicineTimeFormSet, ProfileForm
from .models import IntakeHistory, Medicine, MedicineTime, Pet, Profile, PetAction

def index(request):
    return render(request, 'main/index.html')


class UserLoginView(LoginView):
    template_name = 'main/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('main:dashboard')


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'main/register.html'
    success_url = reverse_lazy('main:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


def user_logout(request):
    logout(request)
    return redirect('main:index')


def get_today_weekday_field():
    weekday = timezone.localdate().weekday()

    fields = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    ]

    return fields[weekday]


def get_today_medicines(user):
    today = timezone.localdate()
    weekday_field = get_today_weekday_field()

    filters = {
        'user': user,
        'start_date__lte': today,
        weekday_field: True,
    }

    medicines = Medicine.objects.filter(**filters).prefetch_related('times')

    medicines = medicines.filter(end_date__isnull=True) | medicines.filter(end_date__gte=today)

    return medicines.distinct()


def get_or_create_pet(user):
    pet, _ = Pet.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Чупакабрик',
            'level': 1,
            'health': 100,
            'experience': 0,
            'missed_in_row': 0,
            'status': Pet.STATUS_NORMAL,
            'is_alive': True,
        }
    )

    return pet


def update_pet_after_taken(pet):
    if not pet.is_alive:
        return

    pet.experience += 10
    pet.health = min(pet.health + 5, 100)
    pet.missed_in_row = 0

    if pet.experience >= pet.level * 50:
        pet.level += 1
        pet.experience = 0

    if pet.health >= 75:
        pet.status = Pet.STATUS_HAPPY
    elif pet.health >= 35:
        pet.status = Pet.STATUS_NORMAL
    else:
        pet.status = Pet.STATUS_SAD

    pet.save()


def update_pet_after_missed(pet):
    if not pet.is_alive:
        return

    pet.health = max(pet.health - 20, 0)
    pet.missed_in_row += 1

    if pet.missed_in_row >= 3 or pet.health <= 0:
        pet.status = Pet.STATUS_DEAD
        pet.is_alive = False
        pet.health = 0
    elif pet.health < 35:
        pet.status = Pet.STATUS_SAD
    elif pet.health < 75:
        pet.status = Pet.STATUS_NORMAL

    pet.save()


def fix_missed_intakes(user):
    today = timezone.localdate()
    now_time = timezone.localtime().time()
    pet = get_or_create_pet(user)

    medicines = get_today_medicines(user)

    for medicine in medicines:
        for medicine_time in medicine.times.all():
            if medicine_time.time >= now_time:
                continue

            exists = IntakeHistory.objects.filter(
                user=user,
                medicine=medicine,
                planned_time=medicine_time.time,
                date=today,
            ).exists()

            if exists:
                continue

            IntakeHistory.objects.create(
                user=user,
                medicine=medicine,
                planned_time=medicine_time.time,
                date=today,
                status=IntakeHistory.STATUS_MISSED,
            )

            update_pet_after_missed(pet)


def build_today_schedule(user):
    today = timezone.localdate()
    medicines = get_today_medicines(user)

    schedule = []

    for medicine in medicines:
        for medicine_time in medicine.times.all():
            history = IntakeHistory.objects.filter(
                user=user,
                medicine=medicine,
                planned_time=medicine_time.time,
                date=today,
            ).first()

            schedule.append({
                'medicine': medicine,
                'time': medicine_time.time,
                'history': history,
            })

    schedule.sort(key=lambda item: item['time'])

    return schedule


@login_required
def dashboard(request):
    fix_missed_intakes(request.user)

    pet = get_or_create_pet(request.user)
    schedule = build_today_schedule(request.user)

    return render(request, 'main/dashboard.html', {
        'pet': pet,
        'schedule': schedule,
    })


@login_required
def mark_taken(request, medicine_id, planned_time):
    if request.method != 'POST':
        return redirect('main:dashboard')

    medicine = get_object_or_404(Medicine, pk=medicine_id, user=request.user)
    today = timezone.localdate()

    planned_time_obj = datetime.strptime(planned_time, '%H:%M').time()

    history, created = IntakeHistory.objects.get_or_create(
        user=request.user,
        medicine=medicine,
        planned_time=planned_time_obj,
        date=today,
        defaults={
            'status': IntakeHistory.STATUS_TAKEN,
            'marked_at': timezone.now(),
        }
    )

    if not created and history.status != IntakeHistory.STATUS_TAKEN:
        history.status = IntakeHistory.STATUS_TAKEN
        history.marked_at = timezone.now()
        history.save()

    pet = get_or_create_pet(request.user)
    update_pet_after_taken(pet)

    return redirect('main:dashboard')


@login_required
def pet_action(request, action):
    if request.method != 'POST':
        return redirect('main:dashboard')

    pet = get_or_create_pet(request.user)

    if not pet.is_alive:
        return redirect('main:dashboard')

    if action not in [PetAction.ACTION_PAT, PetAction.ACTION_PLAY]:
        return redirect('main:dashboard')

    PetAction.objects.create(
        user=request.user,
        pet=pet,
        action=action
    )

    if action == PetAction.ACTION_PAT:
        pet.health = min(pet.health + 3, 100)
        pet.experience += 3

    if action == PetAction.ACTION_PLAY:
        pet.health = min(pet.health + 5, 100)
        pet.experience += 5

    if pet.experience >= pet.level * 50:
        pet.level += 1
        pet.experience = 0

    if pet.health >= 75:
        pet.status = Pet.STATUS_HAPPY
    elif pet.health >= 35:
        pet.status = Pet.STATUS_NORMAL
    else:
        pet.status = Pet.STATUS_SAD

    pet.save()

    return redirect('main:dashboard')


@login_required
def create_new_pet(request):
    if request.method != 'POST':
        return redirect('main:dashboard')

    old_pet = get_or_create_pet(request.user)

    if old_pet.is_alive:
        return redirect('main:dashboard')

    old_pet.delete()

    Pet.objects.create(
        user=request.user,
        name='Чупакабрик',
        level=1,
        health=100,
        experience=0,
        missed_in_row=0,
        status=Pet.STATUS_NORMAL,
        is_alive=True,
    )

    return redirect('main:dashboard')

@login_required
def medicines_list(request):
    medicines = Medicine.objects.filter(user=request.user).prefetch_related('times')

    return render(request, 'main/medicines.html', {
        'medicines': medicines,
    })


@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        formset = MedicineTimeFormSet(
            request.POST,
            queryset=MedicineTime.objects.none()
        )

        if form.is_valid() and formset.is_valid():
            medicine = form.save(commit=False)
            medicine.user = request.user
            medicine.save()

            for time_form in formset:
                if time_form.cleaned_data and not time_form.cleaned_data.get('DELETE'):
                    medicine_time = time_form.save(commit=False)
                    medicine_time.medicine = medicine
                    medicine_time.save()

            return redirect('main:medicines')
    else:
        form = MedicineForm()
        formset = MedicineTimeFormSet(queryset=MedicineTime.objects.none())

    return render(request, 'main/medicine_form.html', {
        'form': form,
        'formset': formset,
        'page_title': 'Добавить лекарство',
        'button_text': 'Сохранить',
    })


@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        formset = MedicineTimeFormSet(
            request.POST,
            queryset=MedicineTime.objects.filter(medicine=medicine)
        )

        if form.is_valid() and formset.is_valid():
            form.save()

            for time_form in formset:
                if not time_form.cleaned_data:
                    continue

                if time_form.cleaned_data.get('DELETE'):
                    if time_form.instance.pk:
                        time_form.instance.delete()
                    continue

                medicine_time = time_form.save(commit=False)
                medicine_time.medicine = medicine
                medicine_time.save()

            return redirect('main:medicines')
    else:
        form = MedicineForm(instance=medicine)
        formset = MedicineTimeFormSet(
            queryset=MedicineTime.objects.filter(medicine=medicine)
        )

    return render(request, 'main/medicine_form.html', {
        'form': form,
        'formset': formset,
        'page_title': 'Редактировать лекарство',
        'button_text': 'Обновить',
    })

@login_required
def profile(request):
    user_profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'display_name': request.user.username
        }
    )

    get_or_create_pet(request.user)

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=user_profile
        )

        if form.is_valid():
            form.save()
            return redirect('main:profile')
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'main/profile.html', {
        'form': form,
        'profile': user_profile,
    })
def intake_history(request):
    history = IntakeHistory.objects.filter(
        user=request.user
    ).select_related('medicine')

    return render(request, 'main/history.html', {
        'history': history,
    })

def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)

    if request.method == 'POST':
        medicine.delete()
        return redirect('main:medicines')

    return render(request, 'main/medicine_confirm_delete.html', {
        'medicine': medicine,
    })
@login_required
def dashboard(request):
    fix_missed_intakes(request.user)

    pet = get_or_create_pet(request.user)

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'display_name': request.user.username
        }
    )

    schedule = build_today_schedule(request.user)

    return render(request, 'main/dashboard.html', {
        'pet': pet,
        'profile': profile,
        'schedule': schedule,
    })
