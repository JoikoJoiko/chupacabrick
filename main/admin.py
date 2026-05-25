from django.contrib import admin
from .models import Profile, Pet, Medicine, MedicineTime, IntakeHistory, PetAction

class MedicineTimeInline(admin.TabularInline):
    model = MedicineTime
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name')
    search_fields = ('user__username', 'display_name')


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'level',
        'health',
        'experience',
        'missed_in_row',
        'status',
        'is_alive',
    )
    list_filter = ('status', 'is_alive')
    search_fields = ('name', 'user__username')


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'start_date',
        'end_date',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    )
    list_filter = (
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    )
    search_fields = ('title', 'user__username', 'comment')
    inlines = [MedicineTimeInline]


@admin.register(MedicineTime)
class MedicineTimeAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'time')
    list_filter = ('time',)
    search_fields = ('medicine__title',)


@admin.register(IntakeHistory)
class IntakeHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'medicine',
        'user',
        'date',
        'planned_time',
        'status',
        'marked_at',
    )
    list_filter = ('status', 'date')
    search_fields = ('medicine__title', 'user__username')

@admin.register(PetAction)
class PetActionAdmin(admin.ModelAdmin):
    list_display = ('pet', 'user', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('pet__name', 'user__username')
