from django.shortcuts import render, redirect,reverse
from django.db.models import Count,Q
from django.http import HttpResponse
from django.contrib import messages
from .models import Tv
from django.views.generic.edit import FormView
from .songdewtv_forms import UserSearchForm,SongdewTvForm, MetaDataForm,VideoTicketForm,SongdewTvForm1
from songdewUser.models import UserProfile,UserVideo,UserAchievement,FollowingDetails,User
from songdew_tv.models import Meta_Data_Lisiting,Ticket
from genre.models import Genre
from language.models import Language
from artistCat.models import ArtistCat

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from songdew.config import error_method
from django.core import serializers
from django.http import JsonResponse
import json
from dal import autocomplete
from googletrans import Translator
from django.contrib.admin.options import ModelAdmin
from agreement.models import CreatedAgreement
import html

# Create your views here.
@login_required(login_url='/administrator/')
@permission_required("songdew_tv.view_tv",raise_exception=True)
def show_tvdata(request):
    form = UserSearchForm(request.POST or None)
    s_id = request.GET.get('sid')
    s_updated = request.GET.get('su')

    if s_id != None:
        if s_id == '':
            s_id = '-'
        else:
            s_id = ''
        result = None
        try:
            if not result:
                print("CACHE NOT FOUND")
                result = Tv.objects.order_by(s_id+'id')
            else:
                print("CACHE FOUND")
            context = {
                'form':form,
                'result_list' : Tv.objects.order_by(s_id+'id'),
                's_title': s_id,
            }
        except Exception as e:
                error_method(e)


        context = {
                'form':form,
                'result_list' : result,
                's_title': s_id,
                }

    elif s_updated != None:
        if s_updated == '':
            s_updated = '-'
        else:
            s_updated = ''

        result = None

        try:
            if not result:
                print("CACHE NOT FOUND")
                result = Tv.objects.order_by(s_updated+ 'updated_date')
            else:
                print("CACHE FOUND")

            context = {
                'form':form,
                'result_list' : Tv.objects.order_by(s_updated+ 'updated_date'),
                's_updated': s_updated,
            }
        except Exception as e:
            error_method(e)


        context = {
                'form':form,
                'result_list' : result,
                's_updated': s_updated,
            }

    else:
        result = None

        try:
            if not result:
                print("CACHE NOT FOUND")
                result = Tv.objects.all().order_by('-created_date')
                # cache.set(cache_key,result,cache_time)
            else:
                print("CACHE FOUND")
            # result_list = Tv.objects.all()

        except Exception as e:
            error_method(e)


        context = {
                'form':form,
                'result_list' : Tv.objects.all(),
                's_updated': '-',
                's_title':'-'
            }

    return render(request, 'songdewtv/sdewtv_home.html',context)


@login_required(login_url='/administrator/')
@permission_required("songdew_tv.change_tv",raise_exception=True)
def search_result(request):
    user   = request.POST.get('user')
    url = request.POST.get('video_slug')
    if user is not None:
        try:
            user_list = UserProfile.objects.get(id=user)
            achievement = UserAchievement.objects.get(user=user_list.user)
            followers = FollowingDetails.objects.filter(user_to_follow=user_list.user).count()

            form=SongdewTvForm(initial={'name':'{0} {1}'.format( user_list.first_name, user_list.last_name ),
                'username':user_list.user.username,'profile_link':"https://songdew.com/"+user_list.user.username,
                'biography':user_list.biography,'achievement':achievement.achievement_description,
                'social_followers':followers})

            context = {'form':form}
        except UserProfile.DoesNotExist as e:
            messages.success(request, 'Enter a valid name.')
            context = {
                       'result_list' : Tv.objects.all(),
                       'user_data' : UserProfile.objects.all(),
                       'url_list' : UserVideo.objects.all(),
                       }
            return render(request, 'songdewtv/sdewtv_home.html',context)

    elif url is not None:
        try:
            video_list = UserVideo.objects.get(slug_uservideo=url)
            user_list = UserProfile.objects.get(user=video_list.user.id)
            achievement = UserAchievement.objects.get(user=video_list.user.id)
            followers = FollowingDetails.objects.filter(user_to_follow=video_list.user.id).count()

            form=SongdewTvForm(initial={'name':'{0} {1}'.format( user_list.first_name, user_list.last_name ),
                'username':user_list.user.username,'profile_link':"https://songdew.com/"+user_list.user.username,
                'biography':user_list.biography,'achievement':achievement.achievement_description,
                'sd_likes':video_list.video_likes,'title':video_list.title,'plays':video_list.video_plays,
                'genre':video_list.genre.name,'asset_id':video_list.id,'social_followers':followers,
                'video_url':"https://songdew.com/video-songs/"+video_list.slug_uservideo,'youtube_url':video_list.youtube_url
                })

            context = {'form':form}
        except UserVideo.DoesNotExist as e:
            messages.success(request, 'Enter a valid video slug.')
            context = {
                       'result_list' : Tv.objects.all(),
                       'user_data' : UserProfile.objects.all(),
                       'url_list' : UserVideo.objects.all(),
                       }
            return render(request, 'songdewtv/sdewtv_home.html',context)

    else:
        context = {
                       'result_list' : Tv.objects.all(),
                       'user_data' : UserProfile.objects.all(),
                       'url_list' : UserVideo.objects.all(),
                       }
        return render(request, 'songdewtv/sdewtv_home.html',context)

    return render(request, 'songdewtv/search_user_result.html',context)

@login_required(login_url='/administrator/')
@permission_required("songdew_tv.add_tv",raise_exception=True)
def add_update_tvdata(request,songdewtv_id=None):

    
    # meta_id = request.GET.get
    # if m



    if songdewtv_id:
        data = Tv.objects.get(id=songdewtv_id)

        form = SongdewTvForm(request.POST or None,instance=data)
    else:
        form = SongdewTvForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            try:
                if request.POST and form.is_valid():
                    
                    print("checking hima")

                    model_instance = form.save(commit=False)
                    print("checking hima")
                    
                    
                    


                    model_instance.is_update = 1
                    # print(model_instance)
                    model_instance.save()
                    context = {
                        'result_list': Tv.objects.all(),
                    }
                    return redirect('showdata')
            except Tv.DoesNotExist as e:
                print(e)
        else:
            print(form.errors)

            return render(request, 'songdewtv/add_update_tvdata.html', {'form': form})
    else:
        return render(request, 'songdewtv/add_update_tvdata.html', {'form': form})



@login_required(login_url='/administrator/')
@permission_required("songdew_tv.delete_tv",raise_exception=True)
def delete_tvdata(request,songdewtv_id):
    try:
        data = Tv.objects.get(id=songdewtv_id)
        data.delete()
    except Exception as e:
        error_method(e)
        return redirect('showdata')

class AutoCompleteUserView(FormView):
    def get(self,request,*args,**kwargs):
        data = request.GET
        username = data.get("term")
        if username:
            users = UserProfile.objects.filter(first_name__istartswith= username)
        else:
            users = UserProfile.objects.all()
        results = []
        for user in users:
            user_json = {}
            user_json['id'] = user.id
            user_json['label'] = user.user.slug_username
            user_json['value'] = user.user.slug_username
            results.append(user_json)
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


class VideoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tv.objects.all()

        if self.q:
            qs = qs.filter(video_id__istartswith=self.q)

        return qs





    


##############################################################################################################################

# Himanshu work



def add_meta_data(request):
    ticket_id = request.GET['ticket_id']
    if ticket_id is not None:
        try:
            ticket_obj = Ticket.objects.get(id=ticket_id)
            print("ticket_obj",ticket_obj)
            if ticket_obj.agreement is not None:
                print(ticket_obj)
                epk_bio = ticket_obj.videoid.user.profile.first()._biography
                epk_achievements = ticket_obj.videoid.user.achievements.first().achievement_description
                obj = Meta_Data_Lisiting()
                obj.video_name  = ticket_obj.videoid.title
                # obj.save()
                print("printing bio",epk_bio)
                print("printing achie",epk_achievements)
                meta_obj = Meta_Data_Lisiting.objects.get(ticket_id = ticket_id)
                print(meta_obj)
                eng_prof = meta_obj.profile_english
                print("print english prfile",eng_prof)
                hin_prof=''
                hin_spot=''
                translator = Translator()
                if eng_prof:
                   hin_prof = Translator().translate(html.unescape(eng_prof), dest='hi').text
           
                eng_spot = meta_obj.spotlight_english
                if eng_spot:
                   hin_spot = Translator().translate(html.unescape(eng_prof), dest='hi').text

                res_spot = hin_spot.encode("utf-8")
                #print("eng_prof", eng_prof)
                #print("printing hindi bio",hin_prof)
                #print("printing hindi spotlight",hin_spot)
                choices = {'epk_bio': epk_bio, 
                'epk_achievements': epk_achievements, 
                'hin_prof':hin_prof,
                'hin_spot':hin_spot }
                data = json.dumps(choices)
                return HttpResponse(data, content_type='application/json')
            elif ticket_obj.source in ('3','4','5','6'):
                meta_obj = Meta_Data_Lisiting.objects.get(ticket_id = ticket_id)
                print(meta_obj)
                eng_prof = meta_obj.profile_english
                print("print english prfile",eng_prof)
                translator = Translator()
                tr_pr = translator.translate(eng_prof, dest='hi')
                hin_prof = tr_pr.text
                eng_spot = meta_obj.spotlight_english
                tr_sp = translator.translate(eng_spot, dest='hi')
                hin_spot = tr_sp.text
                res_spot = hin_spot.encode("utf-8")
                choices = {
                'hin_prof':hin_prof,
                'hin_spot':hin_spot }
                data = json.dumps(choices)
                return HttpResponse(data, content_type='application/json')
        except Ticket.DoesNotExist:
            return HttpResponse(status=404)
    else:
        return HttpResponse('Missing "ticket_id" parameter in the request.', status=400)








##############################################################################################################################

def save_meta_data_ticket(ticket_id):
    print(ticket_id)
    print("1 save meta Data")
    existing_meta_data_entry = Meta_Data_Lisiting.objects.filter(ticket_id=ticket_id)
    if existing_meta_data_entry.exists():
        return 1
    ticket_obj = Ticket.objects.get(id = ticket_id)
    if ticket_obj.source in ('3','4','5','6'):
        # print(" 3 save meta Data")
        meta_obj = Meta_Data_Lisiting()
        meta_obj.video_name  = ticket_obj.title
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
            artist_type = ticket_obj.videoid.user.is_type
            meta_obj = Meta_Data_Lisiting()
            meta_obj.video_name  = ticket_obj.videoid.title
            meta_obj.artist_name = ticket_obj.videoid.user.full_name
            meta_obj.songdew_url = ticket_obj.videoid.user.slug_username
            meta_obj.youtube_url = ticket_obj.videoid.youtube_url
            meta_obj.profile_image = ticket_obj.videoid.user.profile.first()._profile_pic
            meta_obj.artist_type = ticket_obj.videoid.user.is_type
            meta_obj.ticket_id = ticket_obj
            meta_obj.language = language
            meta_obj.genre = genre
            meta_obj.save()

            return   meta_obj.id
        return 0

        
##############################################################################################################################

def save_meta_data_view(request, ticket_id):
    # Call the save_meta_data function with the ticket_id
    result = save_meta_data_ticket(ticket_id)
    print("printing_ticket_id",ticket_id)
    
    if result:
        meta_obj = Meta_Data_Lisiting.objects.filter(ticket_id = ticket_id)
        print("printing meta obj",meta_obj)
        
        if meta_obj.exists():
            
            change_url = reverse("admin:songdew_tv_meta_data_lisiting_change", args=[meta_obj[0].id])
            return redirect(change_url)
        else:
            
            return HttpResponse("Meta_Data_Lisiting object not found for ticket_id: {}".format(ticket_id))
    
    

    
    response_data = {'message': f'save_meta_data executed with result {result}'}

    



##############################################################################################################################

########################
#Use this function for sdtv dashboard

def ticket_dashboard_list(request):

    template_name = 'songdewtv/sdtv_dashboard.html'
    

    context = {'domain_url': settings.DOMAIN_URL}
    if request.method == "POST" :
        start_date_orig = request.POST.get('startdate')
        print("start date", start_date_orig)

        end_date_orig = request.POST.get('enddate')
        print("end date",end_date_orig )
        

        website_upload = get_website_upload(start_date_orig, end_date_orig)
        
        website_broadcast = get_website_broadcast(start_date_orig, end_date_orig)
        offline_reachout = get_offline_reachout(start_date_orig, end_date_orig)
        offline_label = get_offline_label(start_date_orig, end_date_orig)
        offline_music_release = get_offline_music_release(start_date_orig, end_date_orig)
        offline_others = get_offline_others(start_date_orig, end_date_orig)
        agreement_sent = get_agreement_sent(start_date_orig, end_date_orig)
        agreement_signed = get_agreement_signed(start_date_orig,end_date_orig)
        meta_data_created = get_meta_data(start_date_orig, end_date_orig)
        broadcast_ready = get_broadcast_ready(start_date_orig, end_date_orig)
        approved_website = get_approved_website(start_date_orig, end_date_orig)
        rejected_website = get_rejected_website(start_date_orig, end_date_orig)
        todo_website = get_todo_website(start_date_orig, end_date_orig)


        context ={
			"start_date":start_date_orig,
			"end_date": end_date_orig,
			'website_upload': website_upload,
            'website_broadcast': website_broadcast,
            'offline_reachout':offline_reachout,
            'offline_label':offline_label,
            'offline_music_release':offline_music_release,
            'offline_others':offline_others,
            'agreement_sent':agreement_sent,

            'agreement_signed':agreement_signed,

            'meta_data_created':meta_data_created,
            'broadcast_ready' : broadcast_ready,
            'approved_website':approved_website,
            'rejected_website':rejected_website,
            'todo_website':todo_website,

		}
        print("printng context",context)
        return render(request,template_name,context=context)



    if request.method == "GET":
       return render(request, template_name, context={})



###################






















from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from .models import Ticket
import json
from django.db.models import F
from django.db.models import Q

@csrf_exempt
def songdew_tv_dashboard(request):
    template_name = 'songdewtv/dashboard.html'
    # login_url = '/login/'

    start_date_orig = request.POST.get('startdate')
    print("start date", start_date_orig)

    end_date_orig = request.POST.get('enddate')
    print("end date",end_date_orig )

    context = {'domain_url': settings.DOMAIN_URL}

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        start_date = timezone.make_aware(datetime.strptime(start_date_orig, '%Y-%m-%d'))
        print("start_date",start_date )
        end_date = timezone.make_aware(datetime.strptime(end_date_orig, '%Y-%m-%d'))
        print("end_date", end_date)

        website_upload = get_website_upload(start_date_orig, end_date_orig)
        # category_emails = get_category_emails(start_date_orig, end_date_orig)
        print("website upload", website_upload)
        website_broadcast = get_website_broadcast(start_date_orig, end_date_orig)
        offline_reachout = get_offline_reachout(start_date_orig, end_date_orig)
        offline_label = get_offline_label(start_date_orig, end_date_orig)
        offline_music_release = get_offline_music_release(start_date_orig, end_date_orig)
        offline_others = get_offline_others(start_date_orig, end_date_orig)
        agreement_sent = get_agreement_sent(start_date_orig, end_date_orig)
        agreement_signed = get_agreement_signed(start_date_orig,end_date_orig)
        meta_data_created = get_meta_data(start_date_orig, end_date_orig)
        broadcast_ready = get_broadcast_ready(start_date_orig, end_date_orig)
        approved_website = get_approved_website(start_date_orig, end_date_orig)
        rejected_website = get_rejected_website(start_date_orig, end_date_orig)
        todo_website = get_todo_website(start_date_orig, end_date_orig)
        print("broadcast_ready",broadcast_ready)

        context = {
            'domain_url': settings.DOMAIN_URL,
            'website_upload': website_upload,
            'website_broadcast': website_broadcast,
            'offline_reachout':offline_reachout,
            'offline_label':offline_label,
            'offline_music_release':offline_music_release,
            'offline_others':offline_others,
            'agreement_sent':agreement_sent,

            'agreement_signed':agreement_signed,

            'meta_data_created':meta_data_created,
            'broadcast_ready' : broadcast_ready,
            'approved_website':approved_website,
            'rejected_website':rejected_website,
            'todo_website':todo_website,



        }
        # context.update(category_emails)

        return JsonResponse(context, status=200)

    return render(request, template_name, context)

# def get_website_upload(start_date, end_date):
    
#     # unique_count = Ticket.objects.raw(query, params={'start_date': str(start_date), 'end_date': str(end_date)})
#     unique_count = Ticket.objects.filter(source = 1, created_at__range=(start_date, end_date))
    
#     print("unique count", unique_count[::1][::1])
#     length_rawqueryset = len(list(unique_count))
#     # print("print length for website upload", length_rawqueryset)

#     return unique_count



# checking for website upload videos which are approved
def get_approved_website(start_date, end_date):

    unique_count = Ticket.objects.filter(source=1, status = "APPROVED" ,created_at__range=(start_date, end_date)).count()
    return unique_count


# checking for website uplaod videos which are rejected
def get_rejected_website(start_date, end_date):

    unique_count = Ticket.objects.filter(source=1, status = "REJECTED" ,created_at__range=(start_date, end_date)).count()
    return unique_count


# checking for website uplaod videos which are todo
def get_todo_website(start_date, end_date):

    unique_count = Ticket.objects.filter(source=1, status = "TO_DO" ,created_at__range=(start_date, end_date)).count()
    return unique_count


def get_website_upload(start_date, end_date):
    unique_count = Ticket.objects.filter(source=1, created_at__range=(start_date, end_date)).count()
    # print(unique_count.values().count())
    
    # Convert the QuerySet to a list of dictionaries
    # ticket_list = [{'id': ticket.id, 'ticket_id': ticket.ticket_id, 'created_at': ticket.created_at} for ticket in unique_count]

    return unique_count



def get_website_broadcast(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 2, created_at__range=(start_date, end_date)).count()
    # print("unique count", unique_count)
    # length_rawqueryset = len(list(unique_count))
    # print("print length for website upload", length_rawqueryset)

    return unique_count


def get_offline_reachout(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 3, created_at__range=(start_date, end_date)).count()
    # print("unique count", unique_count)
    # length_rawqueryset = len(list(unique_count))
    # print("print length for website upload", length_rawqueryset)

    return unique_count

def get_offline_label(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 4, created_at__range=(start_date, end_date)).count()
    # print("unique count", unique_count)
    # length_rawqueryset = len(list(unique_count))
    # print("print length for website upload", length_rawqueryset)

    return unique_count

    

def get_offline_music_release(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 5, created_at__range=(start_date, end_date)).count()
    # print("unique count", unique_count)
    # length_rawqueryset = len(list(unique_count))
    # print("print length for website upload", length_rawqueryset)

    return unique_count



def get_offline_others(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 6, created_at__range=(start_date, end_date)).count()
    # print("printing start date for offlin eothers",start_date)
    # print("printing end date for offlin eothers",end_date)
    # print("unique coun for offline others", unique_count)
    # length_rawqueryset = len(list(unique_count))
    # print("print length for website upload", length_rawqueryset)

    return unique_count



def get_agreement_sent(start_date, end_date):

    sent_agreements_count = CreatedAgreement.objects.filter(send_date__range=(start_date, end_date)).count()
    # print("sent agreement check",sent_agreements_count)
    agreements_sent = Ticket.objects.filter(
                agreement__isnull = False, agreement__status = 3,videoid = F('agreement__media_id'), 
                created_at__range = (start_date,end_date)).count()
    # print('unique agreemnt count',agreements_sent)
    return agreements_sent
    



def get_meta_data(start_date, end_date):
    unique_count = Meta_Data_Lisiting.objects.filter(ticket_id = F('ticket_id__id'), ticket_id__created_at__range=(start_date, end_date), ticket_id__isnull = False).count()
    # print("unique count", unique_count)
    # length_rawqueryset = len(list(unique_count))
    # print("print length for website upload", length_rawqueryset)

    return unique_count

def get_broadcast_ready(start_date, end_date):
    unique_count = Meta_Data_Lisiting.objects.filter(ticket_id = F('ticket_id__id'), ticket_id__created_at__range=(start_date, end_date), broadcast_ready=True, 
    ticket_id__isnull = False).count()
    # print("unique count", unique_count)
    # length_rawqueryset = len(list(unique_count))
    print("broadcast ready",unique_count)

    return unique_count


def get_agreement_signed(start_date, end_date):

    agreements_signed = Ticket.objects.filter(
                agreement__isnull = False, agreement__status = 4,videoid = F('agreement__media_id'), 
                created_at__range = (start_date,end_date)).values().distinct().count()
    # print('unique agreemnt count',agreements_signed)
    return agreements_signed
    



# Change len to .count method
####################################################################################################################################################


@csrf_exempt
def update_songdew_url(request):
    if request.method == 'POST':
        
        
        print("\n\n\n\n\n\n\n\n Checking for post API for saving \n\n\n\n\n\n\n\n")
       
        # print("request", request.POST.getlist('videoID'))
        tvid = request.POST.getlist('videoID')
        ticketid = request.POST.get('ticket_id')
        print("ticket_id",ticketid)
        print("printing tvid",tvid)

        meta_obj = Meta_Data_Lisiting.objects.get(ticket_id = ticketid)
        print("printing meta_obj",meta_obj)


        for tv_id in tvid:
            print(tv_id)
            tv_obj = Tv.objects.get(video_id = tv_id) 
            print("tv_obj",tv_obj)
            tv_obj.username = meta_obj.songdew_url    
            tv_obj.save()   

        # meta_obj = Meta_Data_Lisiting.objects.get()
        # print(meta_obj)


    data = json.dumps({'success':'Saved Successfully'})
        
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def update_songdew_bio(request):
    if request.method == 'POST':
        
        
        print("\n\n\n\n\n\n\n\n Checking for post API for saving \n\n\n\n\n\n\n\n")
       
        print("request", request.POST.getlist('videoID'))
        tvid = request.POST.getlist('videoID')
        ticketid = request.POST.get('ticket_id')
        print("ticket_id",ticketid)
        print("printing tvid",tvid)

        meta_obj = Meta_Data_Lisiting.objects.get(ticket_id = ticketid)
        print("printing meta_obj",meta_obj)


        for tv_id in tvid:
            print(tv_id)
            tv_obj = Tv.objects.get(video_id = tv_id) 
            print("tv_obj",tv_obj)
            tv_obj.biography = meta_obj.profile_english    
            tv_obj.save()   

        



        
    return JsonResponse({'message': 'Saved Succesfully'}, status=200)


@csrf_exempt
def update_songdew_achie(request):
    if request.method == 'POST':
        
        
        print("\n\n\n\n\n\n\n\n Checking for post API for saving \n\n\n\n\n\n\n\n")
       
        print("request", request.POST.getlist('videoID'))
        tvid = request.POST.getlist('videoID')
        ticketid = request.POST.get('ticket_id')
        print("ticket_id",ticketid)
        print("printing tvid",tvid)

        meta_obj = Meta_Data_Lisiting.objects.get(ticket_id = ticketid)
        print("printing meta_obj",meta_obj)


        for tv_id in tvid:
            print(tv_id)
            tv_obj = Tv.objects.get(video_id = tv_id) 
            print("tv_obj",tv_obj)
            tv_obj.achievement = meta_obj.spotlight_english    
            tv_obj.save()   

        
    return JsonResponse({'message': 'Saved Succesfully'}, status=200)


@csrf_exempt
def update_hindi_achie(request):
    if request.method == 'POST':
        
        
        print("\n\n\n\n\n\n\n\n Checking for post API for saving \n\n\n\n\n\n\n\n")
       
        print("request", request.POST.getlist('videoID'))
        tvid = request.POST.getlist('videoID')
        ticketid = request.POST.get('ticket_id')
        print("ticket_id",ticketid)
        print("printing tvid",tvid)

        meta_obj = Meta_Data_Lisiting.objects.get(ticket_id = ticketid)
        print("printing meta_obj",meta_obj)


        for tv_id in tvid:
            print(tv_id)
            tv_obj = Tv.objects.get(video_id = tv_id) 
            print("tv_obj",tv_obj)
            tv_obj.achievement_hindi = meta_obj.spotlight_hindi    
            tv_obj.save()   

        
    return JsonResponse({'message': 'Saved Succesfully'}, status=200)

@csrf_exempt
def update_hindi_bio(request):
    if request.method == 'POST':
        
        
        print("\n\n\n\n\n\n\n\n Checking for post API for saving \n\n\n\n\n\n\n\n")
       
        print("request", request.POST.getlist('videoID'))
        tvid = request.POST.getlist('videoID')
        ticketid = request.POST.get('ticket_id')
        print("ticket_id",ticketid)
        print("printing tvid",tvid)

        meta_obj = Meta_Data_Lisiting.objects.get(ticket_id = ticketid)
        print("printing meta_obj",meta_obj)


        for tv_id in tvid:
            print(tv_id)
            tv_obj = Tv.objects.get(video_id = tv_id) 
            print("tv_obj",tv_obj)
            tv_obj.biography_hindi = meta_obj.profile_hindi    
            tv_obj.save()   

        
    return JsonResponse({'message': 'Saved Succesfully'}, status=200)






def open_popup_dialog(request):
    # Fetch the user_id based on your authentication logic
    print("\n\n\n\n\n\n\n\n my function start \n\n\n\n\n\n\n\n\n\n\n\n")
    ticket_id = request.GET['ticket_id']
    tick_obj = Ticket.objects.get(id = ticket_id)
    print("ticket_id",tick_obj)

    user_id=""
    if tick_obj.videoid:
        print("inside if condn")
        user_id = tick_obj.videoid.user.id
        print("printing user_id", user_id) 
    


        meta_obj= Meta_Data_Lisiting.objects.get(ticket_id=ticket_id)
        print("meta obj", meta_obj.id)
        meta_id = meta_obj.id

        tv_obj = Tv.objects.filter(artist_id=user_id)
        print("TV obj",tv_obj)
        
        # sd_slug = []
        tv_data = []
        for obj in tv_obj:
            sdid_slug = []
            sdid_slug.append(str(obj.video_id))
            sdid_slug.append(str(obj.username))
            sdid_slug.append(str(obj.biography))
            sdid_slug.append(str(obj.achievement))
            sdid_slug.append(str(obj.biography_hindi))
            sdid_slug.append(str(obj.achievement_hindi))
           
            print("printing sdid_list",sdid_slug)
            tv_data.append(sdid_slug)



        # print("printing request",request.data)   

    choices = {
        'tv_data':tv_data
        
        }

    data = json.dumps(choices)
    return HttpResponse(data, content_type='application/json')

    

######################################################### Songdew TV Report ###############################################################################################

from mailer.models import Email
from notification.models import Notification
from cards.models import Card
from songdew_sms.models import SMS


def ticket_report_list(request):

    template_name = 'songdewtv/sdtv_report.html'
    

    context = {'domain_url': settings.DOMAIN_URL}
    if request.method == "POST" :
        start_date_orig = request.POST.get('startdate')
        print("start date", start_date_orig)

        end_date_orig = request.POST.get('enddate')
        print("end date",end_date_orig )
        

        tv_mail = get_email_count(start_date_orig, end_date_orig)
        tv_sms = get_sms_count(start_date_orig, end_date_orig)
        tv_notifications = get_notification_count(start_date_orig, end_date_orig)
        tv_cards = get_cards_count(start_date_orig, end_date_orig)

       

        context ={
			"start_date":start_date_orig,
			"end_date": end_date_orig,
            "tv_mail" : tv_mail,
            "tv_sms": tv_sms,
            "tv_notifications": tv_notifications,
            "tv_cards" : tv_cards,

		

		}
        print("printng context",context)
        return render(request,template_name,context=context)



    if request.method == "GET":
       return render(request, template_name, context={})



def get_email_count(start_date, end_date):
    unique_count = Email.objects.filter(message__startswith = 'video_upload_mailer',created__range=(start_date, end_date)).count()
    return unique_count


def get_notification_count(start_date, end_date):
    unique_count = Notification.objects.filter(created_date__range=(start_date, end_date)).count()
    return unique_count


def get_cards_count(start_date, end_date):
    unique_count = Card.objects.filter(created_date__range=(start_date, end_date)).count()
    return unique_count

   

def get_sms_count(start_date, end_date):
    unique_count = SMS.objects.filter(sms_name__startswith = 'onair_playout' ,created_date__range=(start_date, end_date)).count()
    return unique_count