from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('tests', views.tests, name='tests'),
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('landing', views.landing, name='landing'),

    path('articles/<int:collection_id>', views.articles, name='articles'),
    path('articles_all/<int:collection_id>', views.articles_all, name='articles_all'),
    path('article/<int:article_id>', views.article, name='article'),
    path('article_create/<int:collection_id>', views.article_create, name='article_create'),
    path('article_edit/<int:article_id>', views.article_edit, name='article_edit'),
    path('article_append_note/<int:article_id>/<int:note_id>', views.article_append_note, name='article_append_note'),
    path('article_delete/<int:article_id>', views.article_delete, name='article_delete'),
    
    path('collections', views.collections, name='collections'),
    path('collection_create', views.collection_create, name='collection_create'),
    path('collection_main/<int:collection_id>', views.collection_main, name='collection_main'),
    path('collection_edit/<int:collection_id>', views.collection_edit, name='collection_edit'),
    path('collection_delete/<int:collection_id>', views.collection_delete, name='collection_delete'),
    path('collection_manage/<int:collection_id>', views.collection_manage, name='collection_manage'),
    path('collection_find', views.collection_find, name='collection_find'),

    path('notes/<int:collection_id>', views.notes, name='notes'),
    path('notes_all/<int:collection_id>', views.notes_all, name='notes_all'),
    path('note_edit/<int:note_id>', views.note_edit, name='note_edit'),
    path('note_delete/<int:note_id>', views.note_delete, name='note_delete'),

    path('tags/<int:collection_id>', views.tags, name='tags'),

    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('invite/<int:collection_id>', views.invite, name='invite'),
    path('respond_to_invite/<int:collection_id>', views.respond_to_invite, name='respond_to_invite'),
    path('dark_mode', views.dark_mode, name="dark_mode"),

    path('password_reset/', 
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html"), 
            name='password_reset'),
    path('password_reset_done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'), 
            name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'), 
            name='password_reset_confirm'),
    path('password_reset_complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'), 
            name='password_reset_complete'),

    path('terms_of_service', views.terms_of_service, name="terms_of_service"),
]