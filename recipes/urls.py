from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('recipes/', views.recipe_list_view, name='list'),
    path('recipes/create/', views.create_recipe_view, name='create'),
    path('recipes/<slug:slug>/', views.recipe_detail_view, name='detail'),
    path('recipes/<slug:slug>/edit/', views.edit_recipe_view, name='edit'),
    path('recipes/<int:recipe_id>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('recipes/<int:recipe_id>/add-to-shopping/', views.add_to_shopping_list_view, name='add_to_shopping'),
    path('shopping-list/', views.shopping_list_view, name='shopping_list'),
    path('shopping-list/<int:item_id>/toggle/', views.toggle_shopping_item_view, name='toggle_shopping_item'),
    path('shopping-list/<int:item_id>/delete/', views.delete_shopping_item_view, name='delete_shopping_item'),
    path('shopping-list/clear-checked/', views.clear_checked_shopping_items_view, name='clear_checked_shopping_items'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/moderate/<int:recipe_id>/<str:action>/', views.moderate_recipe_view, name='moderate_recipe'),
]
