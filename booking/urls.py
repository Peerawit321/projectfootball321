from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from .views import login_view , confirm_payment_view , approve_payment , reject_payment ,booking_events  ,payment ,SignUpView ,profile_view, edit_profile, change_password ,logout_view 
from .views import *

urlpatterns = [
    path('',views.page,name='page'),#หน้าเเรก
    path('home/',views.home, name='home'), # หน้าhome
    path('about/', views.about, name='about'), #หน้าเกี่ยวกับ
    path('bookings/', views.booking_view, name='bookings'), #ดูรายการจอง
    path('contact/', views.contact, name='contact'), #หน้าติดต่อ
    path('manage-user/', views.manage_users, name='manage_users'), #หน้าดูรายชื่อผู้ใช้งาน
    path('booking_admin/', views.booking_admin, name='booking_admin'), #หน้าดูรายการคนจองสนาม
    path('Check_field_status/', views.check_field_status, name='Check_field_status'), #ดูรายการสถานะสนาม
    path('accounts/', include("django.contrib.auth.urls")),  # login
    path('login/', views.login_view, name='login'), # login
    path("signup/", SignUpView.as_view(), name="signup"),# สมัครสมาชิก
    path('add_user/', views.add_user, name='add_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('api/bookings/', booking_events, name='booking_events'),
    path('logout/', logout_view, name='logout'), #ออกจากระบบ
    # path("delete-user/", delete_user, name="delete_user"), #ลบผู้ใช้งานหน้าสถานะสนาม
    path('get_bookings/', views.get_bookings, name='get_bookings'),
    path('users/delete/<int:user_id>/', views.delete_user, name='usrs_delete_user'),

    #หน้า เพิ่ม ลบ สนาม
    path('home_admin/', views.home_admin, name='home_admin'),
    path('add/', views.add_field, name='add_field'),
    path('edit/<int:field_id>/', views.edit_field, name='edit_field'),
    path('delete/<int:field_id>/', views.delete_field, name='delete_field'),
    

    #จ่ายเงิน
    # ==================== USER URLs ====================
    path("payment/<int:booking_id>/", payment, name="payment"),  # หน้าจ่ายเงินสำหรับผู้ใช้
    path("payment/view/", payment_view, name="payment_view"),              # ดูสถานะการชำระเงิน
    path("payment/confirm/", confirm_payment, name="confirm_payment"),    # ยืนยันการชำระเงินโดยผู้ใช้
    path("payment/success/<int:book_id>", payment_success, name="payment_success"),    # หน้าสำเร็จหลังจากชำระเงิน
    path("loading/", loading_page, name="loading_page"), # หน้ารอดําเนินการ
    # ==================== ADMIN URLs ====================
    path("admins/confirm/", confirm_payment_view, name="admin_confirm"),  # แสดงรายการที่รอการตรวจสอบ
    path("admins/approve/<int:payment_id>/", approve_payment, name="approve_payment"),  # อนุมัติการชำระเงิน
    path("admins/reject/<int:payment_id>/", reject_payment, name="reject_payment"),    # ปฏิเสธการชำระเงิน
    path("admins/payments/", confirm_page, name="confirm_page"),          # แสดงรายการชำระเงินทั้งหมด
    # ==================== BOOKING ====================
    path("book_field/", book_field, name="book_field"),  # จองสนาม
    

    #เเก้ไขโปรไฟล์กับเเก้ไขรหัสผ่าน
    path('profile/', profile_view, name='profile_view'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/change-password/', change_password, name='change_password'),
    
] 
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
