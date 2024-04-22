from django.contrib import admin
from django.contrib.admin import DateFieldListFilter,SimpleListFilter
from django import forms
from songdew_tv.songdewtv_forms import SongdewTvForm,UploadFileForm,VideoLibraryForm,UploadPlayoutFileForm,VideoTicketForm, SongdewTvForm1
from django.contrib import messages
from django.forms import ModelForm
from django.contrib.admin import site
from songdew_tv.models import Tv,Tv_Fpc,UploadFile,d2hSingingstar,video_library,UploadPlayoutFile,Tv_Playoutlist, Ticket
from songdewUser.models import User,UserProfile,UserAchievement,UserVideo,FollowingDetails
from django.urls import path,reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from agreement.models import CreatedAgreement
import csv
import json
import ast
from django.conf import settings
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rangefilter.filter import DateRangeFilter
from django.utils.html import format_html
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from songdew_tv.songdewtv_forms import MetaDataForm
from django.contrib.admin.filters import AllValuesFieldListFilter
from django.utils.translation import gettext_lazy as _
# from daterangefilter.filters import PastDateRangeFilter, FutureDateRangeFilter
from django.utils.http import urlencode
from django.contrib.admin.filters import AllValuesFieldListFilter

#himanshu
from songdew_tv.models import Meta_Data_Lisiting,Program


def save_meta_data(ticket_id):
    existing_meta_data_entry = Meta_Data_Lisiting.objects.filter(ticket_id=ticket_id)
    
    if existing_meta_data_entry.exists():
       
        return 1

    ticket_obj = Ticket.objects.get(id = ticket_id)
    print(ticket_obj)
    
    # print(" 2 save meta Data")
    print("source",ticket_obj.source)
    
    if ticket_obj.source in ('3','4','5','6'):
        # print(" 3 save meta Data")
        meta_obj = Meta_Data_Lisiting()
        meta_obj.video_name  = None
        meta_obj.artist_name = None
        meta_obj.songdew_url = None
        meta_obj.youtube_url = None
        meta_obj.profile_image = None
        meta_obj.artist_type = None
        meta_obj.ticket_id = ticket_obj

        meta_obj.save()

        return  1



    else:
        if ticket_obj.agreement is not None:
            
            video_name  = ticket_obj.videoid.title
            artist_name = ticket_obj.videoid.user.full_name
            artistSD    = ticket_obj.videoid.user.slug_username
            genre       = ticket_obj.videoid.genre
            language    = ticket_obj.videoid.language
            youtube_link = ticket_obj.videoid.youtube_url
            profile_image = ticket_obj.videoid.user.profile.first()._profile_pic
            start_date = ticket_obj.agreement.signed_date
            end_date = ticket_obj.agreement.agreement_end_date
            agreement_state = ticket_obj.agreement.country
            
            artist_type = ticket_obj.videoid.user.is_type
            print("printing language \n  \n   \n",language)
            

            meta_obj = Meta_Data_Lisiting()
            meta_obj.video_name  = ticket_obj.videoid.title
            meta_obj.artist_name = ticket_obj.videoid.user.full_name
            meta_obj.songdew_url = ticket_obj.videoid.user.slug_username
            meta_obj.youtube_url = ticket_obj.videoid.youtube_url
            meta_obj.profile_image = ticket_obj.videoid.user.profile.first()._profile_pic
            meta_obj.artist_type = ticket_obj.videoid.user.is_type
            meta_obj.ticket_id = ticket_obj
            meta_obj.duration_start = ticket_obj.agreement.signed_date
            meta_obj.duration_end = ticket_obj.agreement.agreement_end_date
            meta_obj.territory = ticket_obj.agreement.country
            meta_obj.genre = genre
            meta_obj.language = language

            meta_obj.save()

            return   meta_obj.id

    
##################################################################################################################################

#Himanshu
class TicketAdmin(admin.ModelAdmin):
    form = VideoTicketForm
    date_hierarchy = 'created_at'
    list_filter = ('status','source',('created_at',DateRangeFilter),
                    ('updated_at',DateRangeFilter),
                    )
    list_display = ('Ticket_ID','Uploaded_Date', 'Video_name', 'artist_email_id' ,'get_artist_name',
                    'source','assignee','status' ,'updated_at', 'button','metaform'
                    )
    search_fields = ['assignee__username','title','status','ticket_id']
   
    change_list_template = "songdewtv/ticketAdminChangeList.html"
    # actions = ['dashboard_button']
    

    def metaform(self, obj):
        ticket_id = obj.id
        meta_obj = Meta_Data_Lisiting.objects.filter(ticket_id = obj.id)
        if meta_obj.exists():
            change_url = reverse("admin:songdew_tv_meta_data_lisiting_change", args=[meta_obj[0].id])

            button_color = "btn-success" if meta_obj[0].broadcast_ready else "btn-primary"


            return format_html(
                '<a href="{}" class=" btn btn-block {} btn-xs" type="button" target="_blank">Update</a>',
                change_url, button_color
            )
        else:
            if obj.source in ('3','4','5','6'):
                # print(" 3 save meta Data")
                save_meta_data_url = reverse('save_meta_data_view', args=[ticket_id])

               
                button_html = format_html('<a href="{}" type="button" class="button btn btn-block  btn-xs">Add Metadata</a>', save_meta_data_url)
                return button_html

        
        
    metaform.short_description = 'Meta Data Form'  
   


    def dashboard_button(self):
        url = '/songdewtv/songdew_tv_dashboard/'
        return format_html('<a href="{}" class=" btn btn-block btn-success btn-xs" type="button" target="_blank">Update</a>', url)



    # Agreement Button
    def button(self, obj):

        agreement_present = obj.agreement is not None

        action_url = ''
        button_label = ''
        agreement_pdf = ''
        if agreement_present:
            if obj.agreement.pdf :
                 button_label = 'Download'
                 agreement_pdf = obj.agreement.pdf
                 action_url = obj.agreement.pdf.url
        else:
            # button_label = 'No Agreement'
            # action_url = ''
            return

        # Set the CSS class based on the presence of an agreement
        css_class = 'green-button' if obj.agreement is not None else 'blue-button'

        # Render the button with the appropriate CSS class
        button_html = format_html('<a href="{0}" class="{1}" target="_blank">{2}</a>'
                                # '<a class="{1}"  href="/sgmedia/{3}"  target="_blank">Download</a>'
	                                , action_url, css_class, button_label, agreement_pdf
                                )

        # TicketAdmin.metaform(obj)
        
        return button_html

    button.short_description = 'Agreement '
    button.allow_tags = True

    #Himanshu
    # @admin.display(empty_value="???")
    # def get_artist_name(self, obj):
    #     # print(obj.artist_name.first_name)
    #     if obj.videoid:
    #         return obj.videoid.user.full_name
    #     return "hima"

    def get_artist_name(self, obj):
        if obj.videoid:
            url = reverse('admin:songdewUser_user_change', args=[obj.videoid.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.videoid.user.full_name)
       

    def artist_email_id(self,obj):
        if obj.videoid:
            return obj.videoid.user.email

    def artist_slug(self,obj):
        if obj.videoid:
            return obj.videoid.user.slug_username

    # def artist_slug(self,obj):
    #     if obj.videoid:
    #         url = reverse('admin:yourapp_yourvideomodel_change', args=[obj.videoid.id])
    #         return format_html('<a href="{}">{}</a>', url, obj.videoid.user.slug_username)
    #     return '-'

    def artist_phone_number(self,obj):
        if obj.videoid:
            return obj.videoid.user.mobile
        

    def Video_URL(self,obj):
        return obj.youtube_url
    
    def Ticket_ID(self,obj):
        return obj.ticket_id

    def Comment(self,obj):
        return obj.description

    def Uploaded_Date(self,obj):
        return obj.created_at
    
    def Video_name(self,obj):
        return obj.title
    
    get_artist_name.short_description = 'Artist Name'


    

    def get_form(self, request, obj=None, **kwargs):
        form = super(TicketAdmin, self).get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['assignee'].required =  True
            form.base_fields['assignee'].disabled = True
            form.base_fields['assignee'].initial = request.user.id

        if obj and obj.source in ('1','2'):
            form.base_fields['source'].disabled = True
            form.base_fields['agreement_id'].disabled =True
        else: 
            form.base_fields['agreement_id'].disabled =False

        if  obj and obj.agreement:
            form.base_fields['status'].disabled = True
        return form
    

#Export CSV Himanshu
    def export_csv(self, request):
            # Extract selected fields
        data = [key for key in request.POST.keys() if key not in ['csv', 'csrfmiddlewaretoken']]
        column_names = data

        queryset =  Ticket.objects.all().prefetch_related('assignee').order_by('-id')
        length_queryset  = len(queryset)
        print(length_queryset)
        print(queryset)          


        # Get model metadata
        opts = self.model._meta

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(opts.verbose_name)
        writer = csv.writer(response)
        writer.writerow(column_names)

        adding_rows = []
        for column in column_names:
            if column == "assignee":
                # Extract email and mobile from the related User model
                assignee_data = [
                    f"{query.assignee.user.email},{query.assignee.usermobile}" for query in queryset
                ]
                adding_rows.append(assignee_data)
            else:
                adding_rows.append(
                    queryset.values_list(column, flat=True)
                )

        # Transpose the data and write rows to CSV
        for row in zip(*adding_rows):
            writer.writerow(row)

        return response


    export_csv.short_description = "Export to CSV"

    # actions = [export_csv]

    def changelist_view(self, request, extra_context=None):
        # if 'csv' in request.POST:
        #     return self.export_csv(request, self.get_queryset(request))
        # return super(TicketAdmin,self).changelist_view(request, extra_context=extra_context)
        if request.POST:
            if request.POST.get("csv"):
                return self.export_csv(request)
        extra_context = extra_context or {}
        extra_fields = ['ticket_id', 'title', 'get_artist_name', 
                    'Video_URL','Comment','source','assignee','status' ,'updated_at',
                    'assignee__email','assignee__mobile']
        extra_context['ticket_fields_dict'] = extra_fields

        # Uploaded_Date
        # extra_context['ticket_fields_dict'] = self.get_fields(request)
        print(extra_context)
        return super(TicketAdmin, self).changelist_view(request, extra_context=extra_context,)


"""

def changelist_view(self, request, extra_context=None):

        if request.POST:
            if request.POST.get("csv"):
                return self.export_csv(request)
        extra_context = extra_context or {}

        extra_fields = ['video_id', 'artist_id', 'scheduled_date', 'video_type', 'asset_id', 'category', 'name', 'profile_link', 'username', 'biography', 'achievement', 'checked_out', 'sms_code', 'sd_likes', 'title', 'social_followers', 'sd_plays', 'genre', 'profile_image', 'card_image', 'band_pic', 'video_url', 'youtube_url', 'ordering', 'status', 'is_update', 'is_update_datetime', 'youtube_likes', 'youtube_plays']
        extra_context['tvfpc_fields_dict'] = extra_fields

        print(extra_context)
        return super(Tv_FpcAdmin, self).changelist_view(request, extra_context=extra_context,)



"""




# class Admin_meta_data(admin.ModelAdmin):

#     # change_list_template = "songdewtv/change_list.html"
#     pass









from django.core.files import File
class TvAdmin(admin.ModelAdmin):

    class Media:
        js=('js/songdewtv/add_selected_artists.js','js/toggle.js','js/songdewtv/tv_zigzag.js',)
        css={'all': ('admin/css/mychangelists.css',),}

    form = SongdewTvForm

    search_fields = ('video_id', 'username','name','artist_id','category')
    list_display = ['name','video_id','artist_id','id','last_update','created_date','username','profile_link','biography','achievement','sms_code',
    'sd_likes','top_track1','top_track2','top_track3','top_track4','top_track5','title',
    'social_followers','sd_plays','genre','video_id','band_pic','video_url','youtube_url',
    'bm1','bm1_role','bm2','bm2_role','bm3',
    'bm3_role','bm4','bm4_role','bm5','bm5_role',
    'bm6','bm6_role','bm7','bm7_role','bm8',
    'bm8_role','bm9','bm9_role','bm10','bm10_role',
    'bm11','bm11_role','bm12','bm12_role','bm13',
    'bm13_role','bm14','bm14_role','bm15','bm15_role','video_type','category',
    'is_Status','updated_time']
    list_per_page = 20
    change_list_template = "songdewtv/change_list.html"
    site.disable_action('delete_selected')

    def get_urls(self):
        urls = super(TvAdmin,self).get_urls()
        my_urls = [
            path(r'^usersearch/$',self.admin_site.admin_view(self.search_button) ,name="usersearch"),
            path('toggle_status', self.admin_site.admin_view(self.toggle_status), name="toggle_status"),
            path(r'selected_artists/$',self.display_selected_artists,name="selected_artists"),
            ]
        return my_urls + urls

    def display_selected_artists(self,request):
        print("YAY")
        print(request.GET['action'])
        if request.GET['tv_id']:
            if request.GET['action'] == "change":
                tv_id=request.GET['tv_id']
                print(tv_id)
                tv=Tv.objects.get(id=tv_id)
                res=ast.literal_eval(tv.artist_id)
                if res:
                    users = User.objects.filter(id__in=res)
                    artist_list={}
                    for user in users:
                        artist_list[user.id]=user.username
                    context={
                    'artist_list':artist_list,
                    }
                else:
                    context={
                    'artist_list':{},
                    }
                return HttpResponse(json.dumps(context))
        else:
            return HttpResponse(json.dumps("false"))

    def get_form(self, request, obj=None, **kwargs):

        print("kwargs ", kwargs)

        form = super(TvAdmin, self).get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['video_type'].required =  True
            form.base_fields['video_type'].initial = "programme"
            # form.base_fields['meta_tv_id'].disabled = True
        if request.GET.get('id'):
            meta_id = request.GET.get('id')
            print("print first time meta_id",meta_id)
            if meta_id != None:
                try:
                    meta_obj = Meta_Data_Lisiting.objects.get(id=meta_id)
                    print("printng meta obj", meta_obj)
                    print("printng meta obj id", meta_obj.id)
                    if meta_obj != None:
                        form.base_fields['name'].initial = meta_obj.artist_name
                        print(" I am insidde get form without meta_id")
                        form.base_fields['profile_link'].initial = "songdew.com/{}".format(meta_obj.songdew_url)
                        form.base_fields['username'].initial = meta_obj.songdew_url
                        if meta_obj.ticket_id.source in ('1','2'):
                            user_obj = User.objects.filter(id = meta_obj.ticket_id.videoid.user.id)
                            form.base_fields['artist_id'].initial = user_obj
                        form.base_fields['video_type'].initial = meta_obj.programme_types
                        form.base_fields['biography'].initial = meta_obj.profile_english
                        form.base_fields['biography_hindi'].initial = meta_obj.profile_hindi
                        form.base_fields['achievement'].initial = meta_obj.spotlight_english
                        form.base_fields['achievement_hindi'].initial = meta_obj.spotlight_hindi
                        form.base_fields['top_track1'].initial = meta_obj.track_1
                        form.base_fields['top_track2'].initial = meta_obj.track_2
                        form.base_fields['top_track3'].initial = meta_obj.track_3
                        form.base_fields['top_track4'].initial = meta_obj.track_4
                        form.base_fields['bm1'].initial = meta_obj.bm_1
                        form.base_fields['bm2'].initial = meta_obj.bm_2
                        form.base_fields['bm3'].initial = meta_obj.bm_3
                        form.base_fields['bm4'].initial = meta_obj.bm_4
                        form.base_fields['bm1_role'].initial = meta_obj.bm_1_role
                        form.base_fields['bm2_role'].initial = meta_obj.bm_2_role
                        form.base_fields['bm3_role'].initial = meta_obj.bm_3_role
                        form.base_fields['bm4_role'].initial = meta_obj.bm_4_role
                        form.base_fields['title'].initial = meta_obj.video_name
                        form.base_fields['genre'].initial = meta_obj.genre
                        form.base_fields['youtube_url'].initial = meta_obj.youtube_url
                        form.base_fields['card_image'].initial = meta_obj.screenshot_upload if meta_obj.screenshot_upload else None
                        form.base_fields['profile_image'].initial = meta_obj.profile_image if meta_obj.profile_image else None
                        if meta_obj:
                            form.base_fields['meta_tv_id'].initial = meta_obj.id
                except meta_id == None:
                    return 0
        
        return form
    
   
    
   

    



    def add_view(self, request, form_url='', extra_context=None):
     
            achievement_description=""

            


            print("Aaaaaaaaaaaadssdvffdsnvkjsfnbvjfdnbi nfbgnubdkfnbkjfdggbkjfdbuifdbkndfhubinfbdfdfbjnkfngbkdnfjbikfnbidfrribgnbiribnirtnbirnbvrigodgbif")

            if request.GET.get('userid'):
                userid=request.GET.get('userid')
                
                source = UserProfile.objects.get(user=userid)

                followers=""
                try:
                    achievement = UserAchievement.objects.get(user=source.user)
                    achievement_description=achievement.achievement_description
                except UserAchievement.DoesNotExist:
                    pass
                try:
                    followers = FollowingDetails.objects.filter(user_to_follow=source.user).count()
                except FollowingDetails.DoesNotExist:
                    pass
                g = request.GET.copy()
                g.update({
                    'name':'{0} {1}'.format( source.first_name, source.last_name ),
                    'video_type':"video",
                    'artist_id':userid,'username':source.user.username,'profile_link':"https://songdew.com/"+source.user.username,
                'biography':source.biography,'achievement':achievement_description,
                'social_followers':followers
                })

                request.GET = g
                return super(TvAdmin, self).add_view(request, form_url, extra_context)


            elif request.GET.get('videoid'):
                videoid=request.GET.get('videoid')
                video_list = UserVideo.objects.get(id=videoid)
                user_list = UserProfile.objects.get(user=video_list.user.id)
                achievement = UserAchievement.objects.filter(user=video_list.user.id).first()
                followers = FollowingDetails.objects.filter(user_to_follow=video_list.user.id).count()
                g = request.GET.copy()
                g.update({
                    'name':'{0} {1}'.format( user_list.first_name, user_list.last_name ),
                    'video_type':"video",'artist_id':user_list.user.id,
                'username':user_list.user.username,'profile_link':"https://songdew.com/"+user_list.user.username,
                'biography':user_list.biography,'achievement':achievement_description,
                'sd_likes':video_list.video_likes,'title':video_list.title,'plays':video_list.video_plays,
                'genre':video_list.genre.name,'social_followers':followers,
                'video_url':"https://songdew.com/video-songs/"+video_list.slug_uservideo,'youtube_url':video_list.youtube_url
                })
                request.GET = g
                return super(TvAdmin, self).add_view(request, form_url, extra_context)

            else:
                return super(TvAdmin, self).add_view(request, form_url, extra_context)

       




    def export_csv(self, request):
        print(request.POST)
        data = [key for key in request.POST.keys() if key not in ['csv','csrfmiddlewaretoken']]
        column_names = data

        queryset =  Tv.objects.all().order_by('-id')
        length_queryset  = len(queryset)


        opts = Tv._meta

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(opts.verbose_name)
        writer = csv.writer(response)
        writer.writerow(column_names)
        adding_rows = []
        for column in column_names:

            adding_rows.append(
            queryset.values_list(column, flat=True))
        writer.writerows(list(zip(*adding_rows)))
        return response


    def changelist_view(self, request, extra_context=None):

        if request.POST:
            if request.POST.get("csv"):
                return self.export_csv(request)
        extra_context = extra_context or {}
        extra_context['tv_fields_dict'] = self.get_fields(request)
        print(extra_context)
        return super(TvAdmin, self).changelist_view(request, extra_context=extra_context,)

    def search_button(self,request):
        username=request.POST.get('username')
        url=request.POST.get('url')
        url_slug=url[32:]
        if username:
            try:
                user_list = User.objects.get(slug_username=username)
                url="/admin/songdew_tv/tv/add/?userid=%s" %user_list.id
                return HttpResponseRedirect(url)
            except User.DoesNotExist as e:
                messages.success(request, 'Enter a valid user slug.')
                return HttpResponseRedirect("/admin/songdew_tv/tv/")

        elif url:
            try:
                video_list = UserVideo.objects.get(slug_uservideo=url_slug)
                print(video_list.id)
                url="/admin/songdew_tv/tv/add/?videoid=%s" %video_list.id
                return HttpResponseRedirect(url)
            except UserVideo.DoesNotExist as e:
                messages.success(request, 'Enter a valid video slug.')
                return HttpResponseRedirect("/admin/songdew_tv/tv/")

        else:
            return HttpResponseRedirect("/admin/songdew_tv/tv/")

    def toggle_status(self,request):
        tv_id=request.GET['id']
        print(tv_id)
        status=request.GET['status']
        print(status)
        tv=Tv.objects.get(id=tv_id)
        if(status=='1'):
            tv.status='0'
            tv.save()
            data={
            'status':"0",
            }
            return HttpResponse(json.dumps(data))

        else:
            tv.status='1'
            tv.save()
            data={
            'status':"0",
            }
            return HttpResponse(json.dumps(data))

    def is_Status(self, obj):
        if(obj.status):
            return mark_safe('<div type="button" name="status" class="status green" value="1" ><img class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"> <img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
        elif(not obj.status):
            return mark_safe('<div type="button" name="status" class="status red" value="0" ><img  class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"><img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
    is_Status.boolean = False
    is_Status.admin_order_field = 'status'
    is_Status.short_description  = 'Status'

class Tv_FpcAdmin(admin.ModelAdmin):

    class Media:
        js=('js/toggle.js',)
        css={'all': ('admin/css/mychangelists.css',),}

    change_list_template = "tvfpc/change_list.html"
    list_display =['video_id','artist_id','scheduled_date','created_date','updated_date','status']
    list_filter = (
    ('created_date', DateRangeFilter),
    ('scheduled_date', DateRangeFilter),
    'status'

    )

    def get_urls(self):
        urls = super(Tv_FpcAdmin,self).get_urls()
        my_urls = [
            path('toggle_status', self.admin_site.admin_view(self.toggle_status), name="toggle_status"),
            path('upload_csv', self.admin_site.admin_view(self.upload_csv), name='upload_csv'),
            ]
        return my_urls + urls

    def toggle_status(self,request):
        tv_id=request.GET['id']
        print(tv_id)
        status=request.GET['status']
        print(status)
        tv=Tv.objects.get(id=tv_id)
        tv.is_update=1
        if(status=='1'):
            tv.status='0'
            tv.save()
            data={
            'status':"0",
            }
            return HttpResponse(json.dumps(data))

        else:
            tv.status='1'
            tv.save()
            data={
            'status':"0",
            }
            return HttpResponse(json.dumps(data))

    def is_Status(self, obj):
        if(obj.status):
            return mark_safe('<div type="button" name="status" class="status green" value="1" ><img class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"> <img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
        elif(not obj.status):
            return mark_safe('<div type="button" name="status" class="status red" value="0" ><img  class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"><img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
    is_Status.boolean = False
    is_Status.admin_order_field = 'status'
    is_Status.short_description  = 'Status'

    def upload_csv(self, request):
        form = UploadFileForm()
        if request.method == 'POST':
            print(request.POST)
            print(request.FILES)
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                instance = UploadFileForm(request.POST,request.FILES)
                try:
                    csv_file = request.FILES['tv_csv']
                    file_data = csv_file.read().decode("utf-8")
                    lines = file_data.split("\n")
                    count=0
                    #loop over the lines and save them in db. If error , store as string and then display
                    for line in lines:
                        fields = line.split(",")
                        if fields[0].startswith("SD"):
                            try:
                                print(fields[0])
                                video_id=fields[0]
                                video=Tv.objects.get(video_id=fields[0])
                                artist_id=video.artist_id
                                scheduled_date=datetime.strptime(fields[1],'%d.%m.%Y').strftime('%Y-%m-%d')
                                fpc=Tv_Fpc.objects.filter(video_id=fields[0])
                                print(fpc)
                                print("count ",fpc.count())
                                if fpc.count()>0:
                                    fpc.update(scheduled_date=scheduled_date,artist_id=artist_id)
                                else:
                                    new_tv = Tv_Fpc(video_id=video_id,artist_id=artist_id,scheduled_date=scheduled_date)
                                    new_tv.save()
                            except Tv.DoesNotExist:
                                count+=1
                    instance.save()
                    if count>0:
                        messages.success(request, 'File Successfully Uploaded but '+str(count)+' artist ids not found')
                        return HttpResponseRedirect("/admin/songdew_tv/tv_fpc/")
                    else:
                        messages.success(request, 'File Successfully Uploaded ')
                        return HttpResponseRedirect("/admin/songdew_tv/tv_fpc/")
                except Exception as e:
                    print(e)
                    messages.success(request, 'Data in CSV in not in correct format')
                    return HttpResponseRedirect("/admin/songdew_tv/tv_fpc/")
            else:
                messages.success(request, 'Wrong File Uploaded')
                return HttpResponseRedirect("/admin/songdew_tv/tv_fpc/")
        else:
            messages.success(request, 'No File Uploaded')
            return HttpResponseRedirect("/admin/songdew_tv/tv_fpc/")





    def export_csv(self, request):
        print(request.POST)
        data = [key for key in request.POST.keys() if key not in ['csv','csrfmiddlewaretoken']]
        column_names = data
        total_columns = len(column_names)

        queryset =  Tv_Fpc.objects.all().order_by('-id')
        length_queryset  = len(queryset)

        opts = Tv_Fpc._meta

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(opts.verbose_name)
        writer = csv.writer(response)
        writer.writerow(column_names)
        adding_rows = []

        qids = list(queryset.values_list("id", flat=True))

        qdata = []
        for id in qids:
            qrow = []
            qobj = queryset.get(id=id)
            video_id = qobj.video_id
            print("Video_id", video_id)
            if video_id:
                tvobj = Tv.objects.filter(video_id=video_id)
            else:
                tvobj = Tv.objects.none()
            print("tv obj", tvobj)

            for column in column_names:
                if column=="video_id" or column=="artist_id" or column=="scheduled_date":
                    qrow.append(getattr(qobj, column))

                else:
                    if tvobj:
                        qrow.append(getattr(tvobj[0], column))
                    else:
                        qrow.append("")

            writer.writerow(qrow)


        return response


    def changelist_view(self, request, extra_context=None):

        if request.POST:
            if request.POST.get("csv"):
                return self.export_csv(request)
        extra_context = extra_context or {}

        extra_fields = ['video_id', 'artist_id', 'scheduled_date', 'video_type', 'asset_id', 'category', 'name', 'profile_link', 'username', 'biography', 'achievement', 'checked_out', 'sms_code', 'sd_likes', 'title', 'social_followers', 'sd_plays', 'genre', 'profile_image', 'card_image', 'band_pic', 'video_url', 'youtube_url', 'ordering', 'status', 'is_update', 'is_update_datetime', 'youtube_likes', 'youtube_plays']
        extra_context['tvfpc_fields_dict'] = extra_fields

        print(extra_context)
        return super(Tv_FpcAdmin, self).changelist_view(request, extra_context=extra_context,)

class d2hSingingstarAdmin(admin.ModelAdmin):

    class Media:
        js=('js/toggle.js','js/songdewtv/toggle_shortlist_winner.js')
        css={'all': ('admin/css/mychangelists.css',),}


    change_list_template = "d2h/d2hchange_list.html"
    list_display = ['name','id','email','created_date','music_url','music_file','is_Shortlisted','is_Winner','is_Rejected','d2h_registerd_mobile','mobile','user_id']

    list_filter = (
    ('created_date', DateRangeFilter),
    )
    search_fields = ['name']
    ordering = ["-id"]

    def get_urls(self):
        urls = super(d2hSingingstarAdmin,self).get_urls()
        my_urls = [
            path('toggle_is_shortlisted', self.admin_site.admin_view(self.toggle_is_shortlisted), name="toggle_is_shortlisted"),
            path('toggle_is_winner', self.admin_site.admin_view(self.toggle_is_winner), name="toggle_is_winner"),
            path('toggle_is_rejected', self.admin_site.admin_view(self.toggle_is_rejected), name="toggle_is_rejected"),

            ]
        return my_urls + urls

    def toggle_is_shortlisted(self,request):
        d2h_id=request.GET['id']
        print(d2h_id)
        is_shortlisted=request.GET['is_shortlisted']
        print(is_shortlisted)
        star=d2hSingingstar.objects.get(id=d2h_id)
        if(is_shortlisted =='1'):
            star.is_shortlisted='0'
            star.save()
            data={
            'is_shortlisted':"0",
            }
            return HttpResponse(json.dumps(data))

        else:
            star.is_shortlisted='1'
            star.save()
            data={
            'is_shortlisted':"1",
            }
            return HttpResponse(json.dumps(data))

    def is_Shortlisted(self, obj):
        if(obj.is_shortlisted):
            return mark_safe('<div type="button" name="is_shortlisted" class="shortlist green" value="1" ><img class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"> <img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
        elif(not obj.is_shortlisted):
            return mark_safe('<div type="button" name="is_shortlisted" class="shortlist red" value="0" ><img  class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"><img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
    is_Shortlisted.boolean = False
    is_Shortlisted.admin_order_field = 'is_shortlisted'
    is_Shortlisted.short_description  = 'is_Shortlisted'


    def toggle_is_winner(self,request):
        d2h_id=request.GET['id']
        print(d2h_id)
        is_winner=request.GET['is_winner']
        print(is_winner)
        star=d2hSingingstar.objects.get(id=d2h_id)
        if(is_winner =='1'):
            star.is_winner='0'
            star.save()
            data={
            'is_winner':"0",
            }
            return HttpResponse(json.dumps(data))

        else:
            star.is_winner='1'
            star.save()
            data={
            'is_winner':"1",
            }
            return HttpResponse(json.dumps(data))

    def is_Winner(self, obj):
        if(obj.is_winner):
            return mark_safe('<div type="button" name="is_winner" class="winner green" value="1" ><img class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"> <img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
        elif(not obj.is_winner):
            return mark_safe('<div type="button" name="is_winner" class="winner red" value="0" ><img  class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"><img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
    is_Winner.boolean = False
    is_Winner.admin_order_field = 'is_winner'
    is_Winner.short_description  = 'is_winner'


    def toggle_is_rejected(self,request):
        d2h_id=request.GET['id']
        print(d2h_id)
        is_rejected=request.GET['is_rejected']
        print(is_rejected)
        star=d2hSingingstar.objects.get(id=d2h_id)
        if(is_rejected =='1'):
            star.is_rejected='0'
            star.save()
            data={
            'is_rejected':"0",
            }
            return HttpResponse(json.dumps(data))

        else:
            star.is_rejected='1'
            star.save()
            data={
            'is_rejected':"1",
            }
            return HttpResponse(json.dumps(data))

    def is_Rejected(self, obj):
        if(obj.is_rejected):
            return mark_safe('<div type="button" name="is_rejected" class="reject green" value="1" ><img class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"> <img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
        elif(not obj.is_rejected):
            return mark_safe('<div type="button" name="is_rejected" class="reject red" value="0" ><img  class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"><img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
    is_Rejected.boolean = False
    is_Rejected.admin_order_field = 'is_rejected'
    is_Rejected.short_description  = 'is_kachra'

    def changelist_view(self, request, extra_context=None):
        participants =  d2hSingingstar.objects.all().values_list("d2h_registerd_mobile")
        registered = d2hSingingstar.objects.all().values_list("user_id")

        unique_participants = participants.distinct().count()
        total_count =   participants.count()
        registered_users = registered.distinct().count()
        extra_context = extra_context or {}
        extra_context['registered_users'] = registered_users
        extra_context['unique_count'] = unique_participants
        extra_context['total_count'] = total_count
        return super(d2hSingingstarAdmin, self).changelist_view(request, extra_context=extra_context)
# Register your models here.

class video_libraryAdmin(admin.ModelAdmin):
    form = VideoLibraryForm
    class Media:
        css={'all': ('admin/css/mychangelists.css',),}
        js=('js/songdewtv/add_selected_artists.js','js/toggle.js',)

    search_fields = ['tv_video__name','language','program_category','duration','drive_link','grade','playlist_name','status']
    list_display = ['id','get_name','get_id','get_artist_id','get_profile_link','get_likes','language','program_category','duration','drive_link','grade','playlist_name','is_Status']
    list_filter = [('created_at', DateRangeFilter),'status','grade','program_category','playlist_name','language']
    ordering = ('-created_at','-updated_date')
    list_per_page = 10
    # site.disable_action('delete_selected')
    def get_name(self, obj):
        return obj.tv_video.name
    get_name.admin_order_field  = 'Video name'  #Allows column order sorting
    get_name.short_description = 'Video Name'  #Renames column head

    def get_id(self, obj):
        return obj.tv_video.video_id
    get_id.admin_order_field  = 'Video id'  #Allows column order sorting
    get_id.short_description = 'Video ID'  #Renames column head

    def get_artist_id(self, obj):
        return obj.tv_video.artist_id
    get_artist_id.admin_order_field  = 'Artist id'  #Allows column order sorting
    get_artist_id.short_description = 'Artist ID'  #Renames column head

    def get_profile_link(self, obj):
        return obj.tv_video.profile_link
    get_profile_link.admin_order_field  = 'Profile Link'  #Allows column order sorting
    get_profile_link.short_description = 'Profile Link'  #Renames column head

    def get_likes(self, obj):
        return obj.tv_video.sd_likes
    get_likes.admin_order_field  = 'SD Likes'  #Allows column order sorting
    get_likes.short_description = 'SD Likes'  #Renames column head

    def get_urls(self):
        urls = super(video_libraryAdmin,self).get_urls()
        my_urls = [
            path('toggle_status', self.admin_site.admin_view(self.toggle_status), name="toggle_status"),
            # path('upload_csv', self.admin_site.admin_view(self.upload_csv), name='upload_csv'),
            ]
        new_urls = my_urls + urls
        
        return new_urls

    def toggle_status(self,request):
        tv_video_id=request.GET['id']
        print(tv_video_id)
        status=request.GET['status']
        print(status)
        tv=video_library.objects.get(id=tv_video_id)
        if(status=='1'):
            tv.status='0'
            tv.save()
            data={
            'status':"0",
            }
            return HttpResponse(json.dumps(data))

        else:
            tv.status='1'
            tv.save()
            data={
            'status':"0",
            }
            return HttpResponse(json.dumps(data))

    def is_Status(self, obj):
        if(obj.status):
            return mark_safe('<div type="button" name="status" class="status green" value="1" ><img class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"> <img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
        elif(not obj.status):
            return mark_safe('<div type="button" name="status" class="status red" value="0" ><img  class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"><img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
    is_Status.boolean = False
    is_Status.admin_order_field = 'status'
    is_Status.short_description  = 'Status'






import openpyxl

class Tv_PlayoutlistAdmin(admin.ModelAdmin):

    class Media:
        js=('js/toggle.js',)
        css={'all': ('admin/css/mychangelists.css',),}

    change_list_template = "tvplayoutlist/change_list.html"
    list_display =['video_id','artist_id','scheduled_date_time','created_date','updated_date']
    list_filter = (
    ('created_date', DateRangeFilter),
    ('scheduled_date', DateRangeFilter),
  

    )

    def get_urls(self):
        urls = super(Tv_PlayoutlistAdmin,self).get_urls()
        my_urls = [
            path('upload_playlist', self.admin_site.admin_view(self.upload_playlist), name='upload_playlist'),
            ]
        return my_urls + urls
    def get_sec(time_str):
        #Get seconds from time.
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    def upload_playlist(self, request):
        form = UploadPlayoutFileForm()
        if request.method == 'POST':
            print(request.POST)
            print(request.FILES)
            form = UploadPlayoutFileForm(request.POST, request.FILES)
            def get_artist_id(row):
                        print( row[0])
                        q = Tv.objects.get(video_id=row[0])[0]
                        row[0] = q
                        return row
            if form.is_valid():
               xyd = form.save()

               try:
                    file_path = settings.MEDIA_ROOT+'/'+str(xyd.tv_playout_xls)
                    book = openpyxl.load_workbook(file_path, data_only=True)
                    sheet = book.active
                    i=0
                    count =0
                    for H in sheet['C']:
                       fieldv =sheet['D'][i].value
                       if fieldv.startswith("SD"):
                            try:
                                video_id=str(sheet['D'][i].value)
                                video=Tv.objects.get(video_id=video_id)
                                artist_id=video.artist_id
                                scheduled_date=str(sheet['C'][i].value).split(' ')[0]
                                scheduled_time=str(sheet['H'][i].value)
                                duration=Tv_PlayoutlistAdmin.get_sec(str(sheet['I'][i].value))
                                scheduled_date_time = str(scheduled_date+' '+scheduled_time)
                                print(video_id+'----:scheduled_date='+scheduled_date+'---scheduled_time='+ scheduled_time +'---scheduled_date_time='+scheduled_date_time+'-----artist_id----'+str(artist_id))
                                playlist_video=Tv_Playoutlist.objects.filter(video_id=video_id, scheduled_date=scheduled_date, scheduled_time=scheduled_time)
                                #print(fpc)
                                print("count --",playlist_video.count())
                                if playlist_video.count()>0:
                                    playlist_video.update(id=playlist_video[0].id,scheduled_date_time=scheduled_date_time,artist_id=artist_id)
                                else:
                                    new_tv = Tv_Playoutlist(video_id=video_id,artist_id=artist_id,scheduled_date=scheduled_date, scheduled_time=scheduled_time, scheduled_date_time=scheduled_date_time, duration=duration)
                                    new_tv.save()
                            except Tv.DoesNotExist as e:
                                print(e)
                                count+=1
                       i += 1
                    
                    if count > 0:
                        messages.success(request, 'File Successfully Uploaded but '+str(count)+' artist ids not found')
                        return HttpResponseRedirect("/admin/songdew_tv/tv_playoutlist/")
                    else:
                        messages.success(request, 'File Successfully Uploaded ')
                        return HttpResponseRedirect("/admin/songdew_tv/tv_playoutlist/")
               except Exception as e:
                    print(e)
                    messages.success(request, 'Data in CSV in not in correct format')
                    return HttpResponseRedirect("/admin/songdew_tv/tv_playoutlist/")
            else:
                messages.success(request, 'Wrong File Uploaded')
                return HttpResponseRedirect("/admin/songdew_tv/tv_playoutlist/")
        else:
            messages.success(request, 'No File Uploaded')
            return HttpResponseRedirect("/admin/songdew_tv/tv_playoutlist/")






#himanshu work





# class Dropdownfilter(AllValuesFieldListFilter):
#     template = 'songdewtv/dropdown_filter.html'










# print('\n hi')
# ticket_id = 1
# tick_id = Ticket.objects.get(id = ticket_id)
# print(tick_id)
# # for id in tick_id:
# #     print(id.first())

class Mood_dropdown(SimpleListFilter):
    title = _('Mood')  # The title displayed for the filter
    parameter_name = 'video_mood_tag'  # The URL parameter for the filter

    def lookups(self, request, model_admin):
        # Define the filter options and their labels here
        return (
            ('happy', _('Happy')),
            ('sad', _('Sad')),
            ('chill', _('Chill')),
            ('funny', _('Funny')),
            ('anger', _('Anger')),
            ('nostalgic', _('Nostalgic')),
        )

    def queryset(self, request, queryset):
        # Modify the queryset based on the selected filter option
        if self.value() == 'happy':
            return queryset.filter(video_mood_tag='Happy')
        elif self.value() == 'sad':
            return queryset.filter(video_mood_tag='Sad')
        elif self.value() == 'chill':
            return queryset.filter(video_mood_tag='Chill')


"""

class BroadcastReadyFilter(admin.SimpleListFilter):
    title = _('Broadcast Ready')
    parameter_name = 'broadcast_ready'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            return queryset.filter(broadcast_ready=True).order_by('-updated_date')
        elif value == '0':
            return queryset.filter(broadcast_ready=False).order_by('-updated_date')

"""

class BroadcastReadyFilter(admin.SimpleListFilter):
    title = _('Broadcast Ready')
    parameter_name = 'broadcast_ready'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes - Video Broadcasted')),
            ('0', _('Yes - Broadcast Ready')),
            ('2', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            return queryset.filter(broadcast_ready=True, tv__isnull=False).order_by('-updated_date')
        elif value == '0':
            return queryset.filter(broadcast_ready=True, tv__isnull=True).order_by('-updated_date')
        elif value == '2':
            return queryset.filter(broadcast_ready=False)

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }



class DropdownFilters(AllValuesFieldListFilter):
    template = 'songdewtv/dropdown_filter.html'




class MetaDataListingAdmin(admin.ModelAdmin):
    change_form_template = 'songdewtv/custom_change_form.html'
    
    form = MetaDataForm


    def get_agreement(self, obj):
        if obj.agreement is not None:
            return obj.agreement
        return "No Agreement"  
    
    # change_list_template = "songdewtv/Metachangelist.html"
    class Media:
        js=('js/jQuery.3.7.1.js','js/zigzag_meta.js','js/bootstrap.min.js')

        css={'all': ('admin/css/mychangelists.css', 'css/bootstrap-grid.min.css'),}

    # change_list_template = "songdewtv/meta_filters.html"
    
    print("reading change list html")  

    # def edit(self, obj):
    #     return format_html('<a href="/songdewtv/meta_data_lisiting/add_meta_data/" type="button" class="btn btn-block btn-primary btn-xs">Edit</a>', obj.id)


    # change_list_template = "songdewtv/Metachangelist.html"

    list_display = ('programme_types','video_name', 'artist_name','language', 'genre', 'video_quality_tag', 'video_mood_tag','video_themes', 'open_tv_admin_button')
    list_filter = (
                    ('language',DropdownFilter),
                    ( 'genre',DropdownFilters),
                    ('video_quality_tag',DropdownFilters),
                    ('video_year_release',DateRangeFilter),
                    # 'broadcast_ready',
                    BroadcastReadyFilter,
                   
                    ('video_mood_tag',DropdownFilters),
                    ('debut_video',DropdownFilters),
                    ('playlist_inclusion',DropdownFilters),
                    ('gender_video_tag',DropdownFilters),
                    ('video_themes',DropdownFilters))
    # exclude = ['ticket_id']
    date_hierarchy = 'created_date'

    # actions = ['open_tv_admin']

    # def open_tv_admin(self, request, queryset):
    #     selected_ids = [str(obj.id) for obj in queryset]
    #     url = reverse('admin:songdew_tv_tv_add') + f'?id={",".join(selected_ids)}'
    #     return redirect(url)

    # open_tv_admin.short_description = 'Open TvAdmin with Metadata'




    def open_tv_admin_button(self, obj):
        if obj.broadcast_ready:
            tv_entry_exists = Tv.objects.filter(meta_tv_id=obj).exists()
            tv_entry = Tv.objects.filter(meta_tv_id=obj)

            if tv_entry_exists:
                return format_html('<span style="color: green;">&#10004; {} </span>', tv_entry[0].video_id)
            else:
                url = reverse('admin:songdew_tv_tv_add') + '?id={}'.format(obj.id)
                return format_html('<a class="button" href="{}">Broadcast Ready</a>', url)

        return format_html('<span style="color: red;"></span>')

    open_tv_admin_button.short_description = 'Broadcast Ready'
    open_tv_admin_button.allow_tags = True




    
    # def open_tv_admin_button(self, obj):

    #     tv_entry_exists = Tv.objects.filter(meta_tv_id=obj).exists()
    #     tv_entry= Tv.objects.filter(meta_tv_id=obj)
    #     # tv_id = tv_entry[0].video_id

    #     if tv_entry_exists:
    #         return format_html('<span style="color: green;">&#10004; {} </span>', tv_entry[0].video_id)
    #     else:
    #         url = reverse('admin:songdew_tv_tv_add') + '?id={}'.format(obj.id)
    #         return format_html('<a class="button" href="{}">Broadcast Ready</a>', url)

    # open_tv_admin_button.short_description = 'Broadcast Ready'
    # open_tv_admin_button.allow_tags = True

    

admin.site.register(Program)
admin.site.register(Meta_Data_Lisiting, MetaDataListingAdmin)


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Tv, TvAdmin)
admin.site.register(Tv_Fpc, Tv_FpcAdmin)
admin.site.register(Tv_Playoutlist, Tv_PlayoutlistAdmin)
admin.site.register(d2hSingingstar, d2hSingingstarAdmin)
admin.site.register(video_library,video_libraryAdmin)
