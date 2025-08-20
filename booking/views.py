from django.contrib.auth.views import LoginView
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login ,update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.forms import UserCreationForm ,PasswordChangeForm
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth.models import User  # หากใช้โมเดล `User` ของ Django
from django.contrib import messages
from .models import Field , Booking , CustomUser , Payment 
from .forms import FieldForm, CustomUserCreationForm ,BK_T ,BookingForm ,PaymentForm ,ProfileEditForm  
from django.contrib.auth import authenticate, login, logout
from django import forms
from datetime import datetime , timezone ,date
from django.utils.dateformat import format
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt 
import json
from django.apps import apps
from django.conf import settings

def booking_view(request):
    pending_bookings = Booking.objects.filter(payment__status__iexact='approved')
    # ฟอร์มการจอง
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # บันทึกผู้ใช้ที่ทำการจอง
            booking.save()
            return redirect("payment", booking_id=booking.booking_id)  # ไปยังหน้าชำระเงิน
    else:
        form = BookingForm()

    print(pending_bookings)
    return render(request, "user/bookings.html", {"bookings": pending_bookings, "form": form})


def home(request):
    user = request.user
    if request.method == "POST":
        form = BK_T(request.POST)
        if form.is_valid():
            form.instance.user = request.user  # กำหนดผู้ใช้ที่จอง
            form.save()
            return redirect("payment")  # ไปยังหน้าที่แสดงรายการจองทั้งหมด
    else:
        form = BK_T()
    
    fields = Field.objects.all()  # ดึงข้อมูลสนามทั้งหมด
    return render(request, "user/home.html", {"form": form, "fields": fields})


def get_bookings(request):
    bookings = Booking.objects.all()
    data = [
        {
            "booking_id": booking.booking_id,  # ส่ง ID การจอง
            "user_id": booking.user.id,  # ส่ง user_id ของผู้จอง
            "field_id": booking.field.id,  # ส่ง ID สนาม
            "booking_date": booking.booking_date.strftime("%Y-%m-%d"),  # วันที่จอง
            "start_time": booking.start_time.strftime("%H:%M"),  # เวลาเริ่มต้น
            "end_time": booking.end_time.strftime("%H:%M"),  # เวลาสิ้นสุด
            "total_price": float(booking.total_price),  # ราคารวม (แปลง Decimal เป็น float)
        }
        for booking in bookings
    ]
    return JsonResponse(data, safe=False)


def about(request):
    return render(request, 'user/about.html')

def contact(request):
    return render(request, 'user/contact.html')

def page(request):
    return render(request, 'registration/page.html')

def signup(request):
    return render(request, 'user/signup.html')

def manage_users(request):
    user = CustomUser.objects.all()
    return render(request, 'admin/manage.html', {'usertest':user})

def booking_admin(request):
    books = Booking.objects.all()
    return render(request, 'admin/booking_admin.html', {'booking':books})

def check_field_status(request):
    bookss = Booking.objects.all()

    for book in bookss:
        # แปลง start_time และ end_time เป็น datetime.datetime ถ้ายังไม่ใช่
        if isinstance(book.start_time, datetime):
            start_datetime = book.start_time
        else:
            start_datetime = datetime.combine(date.today(), book.start_time)

        if isinstance(book.end_time, datetime):
            end_datetime = book.end_time
        else:
            end_datetime = datetime.combine(date.today(), book.end_time)

        # แปลงเป็น Unix Timestamp
        book.start_timestamp = int(start_datetime.replace(tzinfo=timezone.utc).timestamp())
        book.end_timestamp = int(end_datetime.replace(tzinfo=timezone.utc).timestamp())

    return render(request, 'admin/check_field_status.html', {'booking': bookss})


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')  # เมื่อสมัครเสร็จแล้วจะ redirect ไปที่หน้า login

    def form_valid(self, form):
        # เมื่อฟอร์มถูกยืนยันและส่งข้อมูลที่ถูกต้อง
        user = form.save()
        # login user หลังจากสมัคร
        login(self.request, user)
        return super().form_valid(form)
    
def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        role = request.POST['role']
        try:
            # สร้างผู้ใช้ใหม่
            user = CustomUser.objects.create_user(username=username, email=email)
            user.profile.role = role  # หากมีฟิลด์ role ใน profile
            user.save()
            messages.success(request, "ผู้ใช้ถูกเพิ่มเรียบร้อยแล้ว!")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('manage_users')  # เปลี่ยนเป็น URL ของหน้าจัดการผู้ใช้
    return render(request, 'manage_user/add_user.html')

def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.save()
        messages.success(request, 'บันทึกข้อมูลเรียบร้อยแล้ว!')
        return redirect('manage_users')
    return render(request, 'manage_user/edit_user.html', {'user': user})

def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'ลบผู้ใช้เรียบร้อยแล้ว!')
    return redirect('manage_users')

#************Admin Field

def home_admin(request):
    fields = Field.objects.all()  # ดึงข้อมูลสนามทั้งหมดจากฐานข้อมูล
    return render(request, 'admin/home_admin.html', {'fields': fields})

# เพิ่มสนาม
def add_field(request):
    if request.method == 'POST':
        form = FieldForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home_admin')
    else:
        form = FieldForm()
    return render(request, 'admin/add_field.html', {'form': form})

# แก้ไขสนาม
def edit_field(request, field_id):
    field = get_object_or_404(Field, pk=field_id)
    if request.method == 'POST':
        form = FieldForm(request.POST, request.FILES, instance=field)
        if form.is_valid():
            form.save()
            return redirect('home_admin')
    else:
        form = FieldForm(instance=field)
    return render(request, 'admin/edit_field.html', {'form': form, 'field': field})

# ลบสนาม
def delete_field(request, field_id):
    field = get_object_or_404(Field, pk=field_id)
    if request.method == 'POST':
        field.delete()
        return redirect('home_admin')
    return render(request, 'admin/confirm_delete.html', {'field': field})

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'เข้าสู่ระบบสำเร็จ')
                return redirect('home')  # เปลี่ยน 'home' เป็นชื่อ route ของหน้าแรกของคุณ
            else:
                messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})



    #ปฏิทินตารางสนาม
def booking_events(request):
    bookings = Booking.objects.select_related("user", "field").all()  # ✅ ดึงข้อมูล User และ Field

    data = [
        {
            "booking_id": booking.booking_id,  # ✅ รหัสการจอง
            "user": booking.user.username,  # ✅ ชื่อผู้จอง
            "field": booking.field.field_name,  # ✅ ชื่อสนาม (ต้องตรงกับฟิลด์ของ Field Model)
            "booking_date": booking.booking_date.strftime("%Y-%m-%d"),  # ✅ วันที่จอง
            "start_time": booking.start_time.strftime("%H:%M:%S"),  # ✅ เวลาเริ่ม
            "end_time": booking.end_time.strftime("%H:%M:%S"),  # ✅ เวลาสิ้นสุด
            "total_price": str(booking.total_price),  # ✅ แปลงราคาจองเป็น string
        }
        for booking in bookings
    ]

    print("✅ ส่งข้อมูลให้ปฏิทิน:", data)  # Debug API
    return JsonResp
    onse(data, safe=False) 

# 🔸 Helper: ตรวจสอบว่าเป็น Admin หรือไม่
def is_admin(user):
    return user.is_superuser

# ==================== USER VIEWS ====================

@login_required
def payment(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    bookings = Booking.objects.filter(booking_id=booking_id)

    if booking:
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={'amount': booking.total_price}
        )

        if created or booking.payment != payment:
            booking.payment = payment 
            booking.save()

    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.status = 'pending'  # ตั้งค่าสถานะ "รอดำเนินการ"
            payment.save()
            messages.success(request, "✅ บันทึกการชำระเงินเรียบร้อย! โปรดรอการตรวจสอบ")
            return redirect(reverse('payment_success', args=[booking_id]))
    else:
        form = PaymentForm(instance=payment)

    return render(request, "payment_page/payment.html", {"form": form, "bookings": bookings, "payment": payment})


@login_required
def payment_view(request):
    """แสดงรายการจองและสถานะการชำระเงินของผู้ใช้"""
    bookings = Booking.objects.filter(user=request.user)
    payments = {payment.booking.booking_id: payment for payment in Payment.objects.filter(booking__in=bookings)}

    context = {
        'bookings': bookings,
        'payments': payments
    }
    return render(request, 'payment_page/payment.html', context)


@login_required
def confirm_payment(request):
    if request.method == "POST":
        # รับข้อมูลจากฟอร์ม
        booking_id = request.POST.get("booking_id")
        payment_method = request.POST.get("payment_method")
        receipt = request.FILES.get("payment_receipt")

        # ตรวจสอบข้อมูล
        if not booking_id or not payment_method:
            messages.error(request, "⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
            return redirect("payment_view")

        # ดึง Booking ที่ต้องการ
        booking = get_object_or_404(Booking, pk=booking_id)

        # ใช้ get_or_create เพื่อหลีกเลี่ยง Duplicate
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_price,
                'payment_method': payment_method,
                'status': 'pending',
                'receipt': receipt
            }
        )

        if not created:
            # ถ้ามี Payment เดิม ให้แค่แก้ไขข้อมูล
            payment.payment_method = payment_method
            if receipt:
                payment.receipt = receipt
            payment.status = 'pending'  # ตั้งสถานะให้รอตรวจสอบอีกครั้ง
            payment.save()

        messages.success(request, "✅ ส่งข้อมูลการชำระเงินเรียบร้อย! กรุณารอการตรวจสอบ")
        
        # หลังบันทึกเสร็จ ให้ Redirect ไปหน้า loading_page
        return redirect("loading_page")

    # ถ้าไม่ใช่ POST Method ให้กลับไปหน้าการชำระเงิน
    return redirect("payment_view")


@login_required
def payment_success(request, book_id):
    return render(request, "payment_page/payment_success.html",{'book_id':book_id})


# ==================== ADMIN VIEWS ====================

@user_passes_test(is_admin)
def confirm_payment_view(request):
    #payments = Payment.objects.filter(status="pending")
    payments = Payment.objects.all()
    return render(request, "admin/admin_confirm.html", {"payments": payments})


def approve_payment(request, payment_id):
    print(payment_id)
    payment = Payment.objects.get(payment_id=payment_id)
    payment.status = "approved"
    payment.save()
    messages.success(request, f"✅ อนุมัติการชำระเงิน {payment.payment_id} สำเร็จ!")
    return redirect("admin_confirm")


def reject_payment(request, payment_id):
    payment = Payment.objects.get(payment_id=payment_id)
    payment.status = "rejected"
    payment.save()
    messages.error(request, f"❌ ปฏิเสธการชำระเงิน {payment.payment_id} แล้ว!")
    return redirect("admin_confirm")


# ==================== BOOKING VIEWS ====================

@login_required
def book_field(request):
    """หน้าจองสนาม"""
    if request.method == "POST":
        field = get_object_or_404(Field, pk=request.POST.get('field_id'))
        booking = Booking.objects.create(
            user=request.user,
            field=field,
            booking_date=request.POST.get('booking_date'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            total_price=request.POST.get('total_price')
        )
        messages.success(request, "✅ การจองสำเร็จ กรุณาชำระเงิน")
        return redirect('payment_page', booking_id=booking.booking_id)
    else:
        fields = Field.objects.all()
        return render(request, "book_field.html", {"fields": fields})


# ==================== ADMIN: แสดงรายการชำระเงินทั้งหมด ====================

@user_passes_test(is_admin)
def confirm_page(request):
    """แสดงรายการชำระเงินทั้งหมดที่รอตรวจสอบ"""
    payments = Payment.objects.filter(status="pending")
    return render(request, "admin/confirm.html", {"payments": payments})
    
def loading_page(request):
    return render(request, "loading_page.html")    

def confirm_payment(request):
    if request.method == "POST":
        # Logic สำหรับบันทึกข้อมูลการชำระเงิน
        return redirect("loading_page")
    



@login_required
def profile_view(request):
    """แสดงข้อมูลโปรไฟล์"""
    return render(request, 'user/profile.html', {"user": request.user})

@login_required
def edit_profile(request):
    """แก้ไขโปรไฟล์"""
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile_view")  # กลับไปยังหน้าโปรไฟล์
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'user/edit_profile.html', {"form": form})

@login_required
def change_password(request):
    """แก้ไขรหัสผ่าน"""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # ป้องกันการ logout อัตโนมัติ
            return redirect("profile_view")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'user/change_password.html', {"form": form})


def logout_view(request):
    logout(request)  # ล็อกเอาท์ผู้ใช้
    return redirect('page')  # เปลี่ยนเส้นทางไปยังหน้าแรก (หรือหน้าอื่นที่ต้องการ)

# ดึงโมเดล CustomUser ที่กำหนดใน settings.AUTH_USER_MODEL
CustomUser = apps.get_model(settings.AUTH_USER_MODEL)

def delete_user(request):
    if request.method == "POST" and request.user.is_superuser:
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return JsonResponse({"success": True})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "ไม่พบผู้ใช้"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "ไม่ได้รับอนุญาต"})   

def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(CustomUser, id=user_id)  
        user.delete()
        messages.success(request, "ลบผู้ใช้งานเรียบร้อยแล้ว")
    return redirect('manage_users')