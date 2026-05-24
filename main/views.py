from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm, LoginForm, MedicineForm, MedicineTimeFormSet
from .models import Medicine, MedicineTime


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


@login_required
def dashboard(request):
    medicines = Medicine.objects.filter(user=request.user).prefetch_related('times')

    return render(request, 'main/dashboard.html', {
        'medicines': medicines,
    })


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
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)

    if request.method == 'POST':
        medicine.delete()
        return redirect('main:medicines')

    return render(request, 'main/medicine_confirm_delete.html', {
        'medicine': medicine,
    })
