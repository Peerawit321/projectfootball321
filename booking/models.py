from django.db import models
from django.contrib.auth.models import AbstractUser , User
from django.conf import settings
from django.core.exceptions import ValidationError

# User Model
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    # แยก role เป็น boolean fields
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """ อัปเดตค่า is_admin และ is_user ตาม role ที่เลือก """
        if self.role == 'admin':
            self.is_admin = True
            self.is_user = False
        else:
            self.is_admin = False
            self.is_user = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# Field Model
class Field(models.Model):
    field_id = models.AutoField(primary_key=True)
    field_name = models.CharField(max_length=100)
    price_weekday = models.DecimalField(max_digits=10, decimal_places=2)
    price_weekend = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='field_images/', null=True, blank=True)  # ฟิลด์รูปภาพใหม่

    def __str__(self):
        return self.field_name

from datetime import date
# Booking Model
class Booking(models.Model):
    nickname =  models.CharField(max_length=100)
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    field = models.ForeignKey("Field", on_delete=models.CASCADE)
    booking_date = models.DateField(default=date.today)
    start_time = models.TimeField(verbose_name="เวลาเริ่มต้น")
    end_time = models.TimeField(verbose_name="เวลาสิ้นสุด")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคารวม")


    # เชื่อมไปที่ Payment (One-to-One)
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name="booking_payment")

    def clean(self):
        if not self.start_time or not self.end_time:
            raise ValidationError("กรุณาระบุเวลาเริ่มต้นและเวลาสิ้นสุดให้ถูกต้อง")

        if self.start_time >= self.end_time:
            raise ValidationError("เวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด")

        overlapping_bookings = Booking.objects.filter(
            field=self.field,
            booking_date=self.booking_date
        ).exclude(booking_id=self.booking_id)

        for booking in overlapping_bookings:
            if (self.start_time < booking.end_time and self.end_time > booking.start_time):
                raise ValidationError("ช่วงเวลาที่เลือกถูกจองไปแล้ว")

    def save(self, *args, **kwargs):
        self.clean()  # ตรวจสอบความถูกต้องของข้อมูลก่อนบันทึก
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_id} by {self.user.username}"



# Payment Model
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'เงินสด'),
        ('credit_card', 'บัตรเครดิต'),
        ('bank_transfer', 'โอนผ่านธนาคาร'),
    ]

    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('approved', 'อนุมัติ'),
        ('rejected', 'ถูกปฏิเสธ'),
    ]

    payment_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment_info")
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    receipt = models.FileField(upload_to="receipts/", blank=True, null=True)

    def __str__(self):
        return f"Payment {self.payment_id} for Booking {self.booking.booking_id} {self.status}"


# Schedule Model
class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.BooleanField(default=True)  # True = Available, False = Booked

    def __str__(self):
        return f"Schedule {self.schedule_id} for {self.field.field_name}"
