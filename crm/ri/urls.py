from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('reference_tables/', views.reference_tables, name='reference_tables'),
    path('display_table/<str:model_name>/', views.display_table, name='display_table'),
    path('add_item/<str:model_name>/', views.add_item_view, name='add_item_view'),
    path('delete/<str:model_name>/<int:pk>/', views.delete_item_view, name='delete_item_view'),
    path('edit/<str:model_name>/<int:pk>/', views.edit_item_view, name='edit_item_view'),

    path('documents/<str:document_type>/', views.display_documents, name='display_documents'),
    path('add_doc/<str:document_type>/', views.add_document_view, name='add_document_view'),
    path('edit_doc/<str:document_type>/<int:pk>/', views.edit_document_view, name='edit_document_view'),
    path('delete_doc/<str:document_type>/<int:pk>/', views.delete_document_view, name='delete_document_view'),
    # path('', views.home_view, name='home'),
]