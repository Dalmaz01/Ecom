from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store, name='store'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('login', views.login_page, name='login'),
    path('register', views.register_page, name='register'),
    path('logout_view', views.logout_view, name='logout_view'),

    path('update_item', views.updateItem, name='update_item'),
    path('process_order', views.processOrder, name='process_order'),
    path('product_detail/<int:pk>', views.productDetail, name='product_detail'),
]