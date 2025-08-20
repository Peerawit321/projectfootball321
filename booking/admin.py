from django.contrib import admin
from .models import CustomUser,Field,Booking,Payment,Schedule

class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'address')

admin.site.register(CustomUser)
admin.site.register(Field)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Schedule)