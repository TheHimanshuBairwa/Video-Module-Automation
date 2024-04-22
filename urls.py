from django.urls import path, include
from . import views
from songdew_tv.views import AutoCompleteUserView,songdew_tv_dashboard,update_songdew_url


urlpatterns = [
   
    path('', views.show_tvdata, name="showdata"),
    path('add', views.add_update_tvdata, name="add_tvdata"),

    
    # path('addMeta', views.metadatalist, name = "add_metadata"),
    # path('meta-data-listing/', views.meta_data_listing_view, name='meta_data_listing_view'),
    path('search/result', views.search_result, name="search_result"),
    path('<int:songdewtv_id>/update', views.add_update_tvdata, name="update"),
    
    path('songdew_tv_dashboard/', views.ticket_dashboard_list, name  = "songdew_tv_dashboard"),
    path('songdew_tv_report/', views.ticket_report_list, name  = "songdew_tv_report"),
    
    path('<int:songdewtv_id>/delete', views.delete_tvdata, name="delete"),
    path('autocompleteuser',AutoCompleteUserView.as_view(), name='autocompleteuser'),
    path('tv-autocomplete/', views.VideoAutocomplete.as_view(), name="tv-autocomplete"),
    path('get_info/', views.add_meta_data, name="get_info"),
    # path('meta_data_lisiting/add_meta_data/', views.add_meta_data, name="add_meta_data"),
    path('meta_data_lisiting/', views.add_meta_data, name  = "add_meta_data"),
    path('save_meta_data/<int:ticket_id>/', views.save_meta_data_view, name='save_meta_data_view'),
    # path('/<int:meta_id>/', views.show_meta_tv_data, name='add_tv_meta_data'),
    # path('sdtv_dashboard/', views.sdtv_dashboard, name = 'sdtv_dashboard'),
    # path('songdew_tv_dashboard/', views.songdew_tv_dashboard, name  = "songdew_tv_dashboard"),
    # path('update_tv_entries/', views.update_tv_entries, name='update_tv_entries'),

    path('open-popup-dialog/', views.open_popup_dialog, name='open_popup_dialog'),
    path('update-songdew-url', views.update_songdew_url, name='update_songdew_url'),
    path('update-songdew-bio', views.update_songdew_bio, name='update_songdew_bio'),
    path('update-songdew-achie', views.update_songdew_achie, name='update_songdew_achie'),
    path('update-hindi-achie', views.update_hindi_achie, name='update_hindi_achie'),
    path('update-hindi-bio', views.update_hindi_bio, name='update_hindi_bio'),


]
