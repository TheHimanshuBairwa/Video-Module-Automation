from django.shortcuts import render, redirect,reverse
from django.db.models import Count,Q
from django.http import HttpResponse
from django.contrib import messages
from .models import Tv,Ticket,Meta_Data_Lisiting
from googletrans import Translator
from django.views.generic.edit import FormView
from .songdewtv_forms import UserSearchForm,SongdewTvForm
from songdewUser.models import UserProfile,UserVideo,UserAchievement,FollowingDetails
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from songdew.config import error_method
from django.core import serializers
from django.http import JsonResponse
import json
import html
from dal import autocomplete

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

    if songdewtv_id:
        data = Tv.objects.get(id=songdewtv_id)

        form = SongdewTvForm(request.POST or None,instance=data)
    else:
        form = SongdewTvForm(request.POST or None)

    if request.POST:
        if  form.is_valid():
            try:
                if request.POST and form.is_valid():
                    model_instance = form.save(commit=True)
                    model_instance.save()
                    context = {
                            'result_list' : Tv.objects.all(),
                            }
                    return redirect('showdata')
            except Tv.DoesNotExist as e:
                    print(e)
        else:
            print(form.errors)

            return render(request,'songdewtv/add_update_tvdata.html',{'form':form})
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




###############new##################################################################################################06/11######################


def add_meta_data(request):
    print("yes, I'm here")
    ticket_id = request.GET.get('ticket_id')
    if ticket_id is not None:
        try:
            ticket_obj = Ticket.objects.get(id=ticket_id)
            print("ticket_obj", ticket_obj)

            if ticket_obj.agreement is not None:
                print(ticket_obj)
                epk_bio = ticket_obj.videoid.user.profile.first()._biography
                epk_achievements = ticket_obj.videoid.user.achievements.first().achievement_description
                obj = Meta_Data_Lisiting()
                obj.video_name = ticket_obj.videoid.title
                print("printing bio", epk_bio)
                print("printing achievements", epk_achievements)

                meta_obj = Meta_Data_Lisiting.objects.get(ticket_id=ticket_id)
                print(meta_obj)
                eng_prof = meta_obj.profile_english
                print("print English profile", eng_prof)
                translator = Translator()
                try:
                    tr_pr = translator.translate(eng_prof, dest='hi')
                    hin_prof = tr_pr.text
                except Exception as e:
                    hin_prof = "Hindi Translation is not working on Orbit"
                eng_spot = meta_obj.spotlight_english
                try:
                    tr_sp = translator.translate(eng_spot, dest='hi')
                    hin_spot = tr_sp.text
                except Exception as e:
                    hin_spot = "Hindi Translation is not working on Orbit"
                res_spot = hin_spot.encode("utf-8")
                print("eng_prof", eng_prof)

                print("printing Hindi bio", hin_prof)
                print("printing Hindi spotlight", hin_spot)

                choices = {'epk_bio': epk_bio, 'epk_achievements': epk_achievements, 'hin_prof': hin_prof, 'hin_spot': hin_spot}
                data = json.dumps(choices)
                return HttpResponse(data, content_type='application/json')
            elif ticket_obj.source in ('3', '4', '5', '6'):
                meta_obj = Meta_Data_Lisiting.objects.get(ticket_id=ticket_id)
                print(meta_obj)
                eng_prof = meta_obj.profile_english
                print("print English profile", eng_prof)
                translator = Translator()
                try:
                    tr_pr = translator.translate(eng_prof, dest='hi')
                    hin_prof = tr_pr.text
                except Exception as e:
                    hin_prof = "Hindi Translation is not working on Orbit"
                eng_spot = meta_obj.spotlight_english
                try:
                    tr_sp = translator.translate(eng_spot, dest='hi')
                    hin_spot = tr_sp.text
                except Exception as e:
                    hin_spot = "Hindi Translation is not working on Orbit"
                res_spot = hin_spot.encode("utf-8")
                print("eng_prof", eng_prof)
                print("printing Hindi bio", hin_prof)
                print("printing Hindi spotlight", hin_spot)
                choices = {'hin_prof': hin_prof, 'hin_spot': hin_spot}
                data = json.dumps(choices)
                return HttpResponse(data, content_type='application/json')
        except Ticket.DoesNotExist:
            return HttpResponse(status=404)  # Not Found
    else:
        return HttpResponse('Missing "ticket_id" parameter in the request.', status=400)  # Bad Request




def save_meta_data_ticket(ticket_id):
    print(ticket_id)
    print("1 save meta Data")
    existing_meta_data_entry = Meta_Data_Lisiting.objects.filter(ticket_id=ticket_id)
    if existing_meta_data_entry.exists():
        return 1
    ticket_obj = Ticket.objects.get(id = ticket_id)
    if ticket_obj.source in ('3','4','5','6'):
        print(" 3 save meta Data")
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





def save_meta_data_view(request, ticket_id):
    result = save_meta_data_ticket(ticket_id)
    if result:
        meta_obj = Meta_Data_Lisiting.objects.filter(ticket_id = ticket_id)
        change_url = reverse("admin:songdew_tv_meta_data_lisiting_change", args=[meta_obj[0].id])
        return redirect(change_url)






######################################################################################################################################################################


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
from agreement.models import CreatedAgreement

@csrf_exempt
def songdew_tv_dashboard(request):
    template_name = 'songdewtv/dashboard.html'
    login_url = '/login/'

    start_date_orig = request.POST.get('startdate')
    print("start date", start_date_orig)

    end_date_orig = request.POST.get('enddate')
    print("end date",end_date_orig )

    context = {'domain_url': settings.DOMAIN_URL}

    if request.method == 'POST' and request.is_ajax():
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

        }
        # context.update(category_emails)

        return JsonResponse(context, status=200)

    return render(request, template_name, context)

def get_website_upload(start_date, end_date):
    query = """
        SELECT id FROM (
            SELECT id FROM songdew_tv_ticket 
            WHERE (created_at >= %(start_date)s AND created_at <= %(end_date)s) 
            ORDER BY created_at DESC
        ) AS subquery_alias 
        WHERE source = 1
    """
    # unique_count = Ticket.objects.raw(query, params={'start_date': str(start_date), 'end_date': str(end_date)})
    unique_count = Ticket.objects.filter(source = 1, created_at__range=(start_date, end_date))
    print("unique count", unique_count)
    length_rawqueryset = len(list(unique_count))
    print("print length for website upload", length_rawqueryset)

    return length_rawqueryset

def get_website_broadcast(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 2, created_at__range=(start_date, end_date))
    print("unique count", unique_count)
    length_rawqueryset = len(list(unique_count))
    print("print length for website upload", length_rawqueryset)

    return length_rawqueryset


def get_offline_reachout(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 3, created_at__range=(start_date, end_date))
    print("unique count", unique_count)
    length_rawqueryset = len(list(unique_count))
    print("print length for website upload", length_rawqueryset)

    return length_rawqueryset

def get_offline_label(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 4, created_at__range=(start_date, end_date))
    print("unique count", unique_count)
    length_rawqueryset = len(list(unique_count))
    print("print length for website upload", length_rawqueryset)

    return length_rawqueryset

    get_offline_music_release

def get_offline_music_release(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 5, created_at__range=(start_date, end_date))
    print("unique count", unique_count)
    length_rawqueryset = len(list(unique_count))
    print("print length for website upload", length_rawqueryset)

    return length_rawqueryset



def get_offline_others(start_date, end_date):
    unique_count = Ticket.objects.filter(source = 6, created_at__range=(start_date, end_date))
    print("unique count", unique_count)
    length_rawqueryset = len(list(unique_count))
    print("print length for website upload", length_rawqueryset)

    return length_rawqueryset



def get_agreement_sent(start_date, end_date):

    sent_agreements_count = CreatedAgreement.objects.filter(send_date__range=(start_date, end_date)).count()
    print("sent agreement check",sent_agreements_count)
    agreements_sent = Ticket.objects.filter(
    agreement__isnull = False, videoid = F('agreement__media_id'), created_at__range = (start_date,end_date)).values().distinct().count()
    print('unique agreemnt count',agreements_sent)
    return agreements_sent
    



def get_meta_data(start_date, end_date):
    unique_count = Meta_Data_Lisiting.objects.filter(ticket_id = F('ticket_id__id'), ticket_id__created_at__range=(start_date, end_date), ticket_id__isnull = False)
    print("unique count", unique_count)
    length_rawqueryset = len(list(unique_count))
    print("print length for website upload", length_rawqueryset)

    return length_rawqueryset




def get_agreement_signed(start_date, end_date):

    agreements_signed = Ticket.objects.filter(
    agreement__isnull = False, agreement__signed_date__isnull = False,videoid = F('agreement__media_id'), created_at__range = (start_date,end_date)).values().distinct().count()
    print('unique agreemnt count',agreements_signed)
    return agreements_signed
    



