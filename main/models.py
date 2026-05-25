from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Имя на сайте'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.display_name or self.user.username


class Pet(models.Model):
    STATUS_HAPPY = 'happy'
    STATUS_NORMAL = 'normal'
    STATUS_SAD = 'sad'
    STATUS_DEAD = 'dead'

    STATUS_CHOICES = [
        (STATUS_HAPPY, 'Счастлив'),
        (STATUS_NORMAL, 'Обычный'),
        (STATUS_SAD, 'Грустный'),
        (STATUS_DEAD, 'Умер'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='pet',
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=100,
        default='Чупакабрик',
        verbose_name='Имя питомца'
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='Уровень'
    )
    health = models.PositiveIntegerField(
        default=100,
        verbose_name='Здоровье'
    )
    experience = models.PositiveIntegerField(
        default=0,
        verbose_name='Опыт'
    )
    missed_in_row = models.PositiveIntegerField(
        default=0,
        verbose_name='Пропусков подряд'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NORMAL,
        verbose_name='Состояние'
    )
    is_alive = models.BooleanField(
        default=True,
        verbose_name='Жив'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'

    def __str__(self):
        return f'{self.name} — {self.user.username}'


class Medicine(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medicines',
        verbose_name='Пользователь'
    )
    title = models.CharField(
        max_length=150,
        verbose_name='Название лекарства'
    )
    comment = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Комментарий'
    )
    start_date = models.DateField(
        verbose_name='Дата начала'
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата окончания'
    )

    monday = models.BooleanField(default=False, verbose_name='Понедельник')
    tuesday = models.BooleanField(default=False, verbose_name='Вторник')
    wednesday = models.BooleanField(default=False, verbose_name='Среда')
    thursday = models.BooleanField(default=False, verbose_name='Четверг')
    friday = models.BooleanField(default=False, verbose_name='Пятница')
    saturday = models.BooleanField(default=False, verbose_name='Суббота')
    sunday = models.BooleanField(default=False, verbose_name='Воскресенье')

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Лекарство'
        verbose_name_plural = 'Лекарства'
        ordering = ['title']

    def __str__(self):
        return self.title


class MedicineTime(models.Model):
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name='times',
        verbose_name='Лекарство'
    )
    time = models.TimeField(
        verbose_name='Время приёма'
    )

    class Meta:
        verbose_name = 'Время приёма'
        verbose_name_plural = 'Время приёма'
        ordering = ['time']

    def __str__(self):
        return f'{self.medicine.title} — {self.time.strftime("%H:%M")}'


class IntakeHistory(models.Model):
    STATUS_TAKEN = 'taken'
    STATUS_MISSED = 'missed'

    STATUS_CHOICES = [
        (STATUS_TAKEN, 'Принято'),
        (STATUS_MISSED, 'Пропущено'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='intake_history',
        verbose_name='Пользователь'
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        verbose_name='Лекарство'
    )
    planned_time = models.TimeField(
        verbose_name='Запланированное время'
    )
    date = models.DateField(
        verbose_name='Дата'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )
    marked_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Время отметки'
    )

    class Meta:
        verbose_name = 'История приёма'
        verbose_name_plural = 'История приёма'
        ordering = ['-date', '-planned_time']
        unique_together = ('user', 'medicine', 'planned_time', 'date')

    def __str__(self):
        return f'{self.medicine.title} — {self.date} — {self.get_status_display()}'


class PetAction(models.Model):
    ACTION_PAT = 'pat'
    ACTION_PLAY = 'play'

    ACTION_CHOICES = [
        (ACTION_PAT, 'Погладить'),
        (ACTION_PLAY, 'Поиграть'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pet_actions',
        verbose_name='Пользователь'
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name='Питомец'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Действие'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата действия'
    )

    class Meta:
        verbose_name = 'Действие с питомцем'
        verbose_name_plural = 'Действия с питомцем'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.pet.name} — {self.get_action_display()}'
