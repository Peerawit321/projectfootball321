from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from .models import FieldBooking
from .models import Field, Booking, CustomUser,Booking, CustomUser  ,Booking ,Payment
from django.contrib.auth import get_user_model
# รายการเวลาที่สามารถเลือกได้ (ชั่วโมงเต็ม)
TIME_CHOICES = [
    ('08:00', '08:00'),
    ('09:00', '09:00'),
    ('10:00', '10:00'),
    ('11:00', '11:00'),
    ('12:00', '12:00'),
    ('13:00', '13:00'),
    ('14:00', '14:00'),
    ('15:00', '15:00'),
    ('16:00', '16:00'),
    ('17:00', '17:00'),
    ('18:00', '18:00'),
    ('19:00', '19:00'),
    ('20:00', '20:00'),
    ('21:00', '21:00'),
    ('22:00', '22:00'),
    ('23:00', '23:00'),
    # คุณสามารถเพิ่มเวลาอื่นๆ ตามต้องการ
]

class BK_T(forms.ModelForm):
    class Meta:
        model = Booking
        exclude = ['user','payment']  # หรือระบุฟิลด์ที่ต้องการยกเว้น
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input block w-full py-2 px-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'}),
        }

       

    # กำหนดฟิลด์เลือกเวลาเริ่มและสิ้นสุดด้วย ChoiceField
    start_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input block w-full py-2 px-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'})
    )

    end_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input block w-full py-2 px-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'})
    )

User = get_user_model()

class ProfileEditForm(forms.ModelForm):
    """ฟอร์มแก้ไขข้อมูลโปรไฟล์"""
    class Meta:
        model = User
        fields = ["username", "email"]   
    
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text="",  
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )   

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': '',
            'password1': '',
            'password2': '',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
    
class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ['field_name', 'price_weekday', 'price_weekend', 'image']



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['field', 'start_time', 'end_time', 'total_price','nickname']
        
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'receipt']  # เอา 'status' ออกจากผู้ใช้ทั่วไป

        widgets = {
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'เลือกวิธีการชำระเงิน'
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)

        # เพิ่ม placeholder และจัดรูปแบบฟอร์ม
        self.fields['payment_method'].label = "วิธีการชำระเงิน"
        self.fields['receipt'].label = "อัปโหลดสลิปการชำระเงิน"

        # สำหรับสถานะให้เฉพาะแอดมินแก้ไขได้
        if self.instance and self.instance.pk:
            if self.instance.status != 'pending':
                self.fields['payment_method'].disabled = True
                self.fields['receipt'].disabled = True
        
        

         