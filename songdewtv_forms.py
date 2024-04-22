from cProfile import label
from django import forms
from .models import Tv,UploadFile,video_library,UploadPlayoutFile,Meta_Data_Lisiting, Program
from songdewUser.models import User,UserProfile,UserVideo
from django.forms import ModelMultipleChoiceField,HiddenInput


from dal import autocomplete
from .models import Genre, Language
# from .views import add_meta_data
import itertools

from django import forms
from .models import Tv,UploadFile,Ticket
from songdewUser.models import User,UserProfile,UserVideo
from django.forms import ModelMultipleChoiceField
from dal import autocomplete
from django.contrib.admin.widgets import AdminDateWidget
from agreement.models import CreatedAgreement



class VideoLibraryForm(forms.ModelForm):
    GRADE = (
        ("A", "A"),
        ("B", "B"),
        ("C","C"),
        ("D","D")
    )

    TVList = Tv.objects.filter(status=True)
    tv_video = forms.ModelChoiceField(
        label="tv_video", queryset=TVList, widget=autocomplete.ModelSelect2(url='tv-autocomplete'))
    language = forms.CharField(label="Language",widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    program_category = forms.CharField(label="Program Category",widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    duration = forms.CharField(label="Duration",widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    drive_link = forms.CharField(label='Drive Link',widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    grade = forms.ChoiceField(label='Grade',choices=GRADE,required=True)
    playlist_name = forms.CharField(label='Playlist',widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    status			=	forms.BooleanField(label='Public',required=False)

    class Meta:
        model = video_library
        fields = ['tv_video','language','program_category','duration','drive_link','grade','playlist_name','status']


class UserSearchForm(forms.ModelForm):
	UserList     =  UserProfile.objects.all()
	user         =  ModelMultipleChoiceField(label="Select User", queryset=UserList,widget=autocomplete.ModelSelect2Multiple(url='userprofile-autocomplete'),required=False)
	video_slug  =  forms.CharField(label="Enter Songdew Video Slug",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Ex-raag-kalavati-57'}),required=False)

	class Meta:
		model = UserVideo
		fields = ['user','video_slug']



# himanshu


# ticketid_obj = itertools.count()


class VideoTicketForm(forms.ModelForm):
    ArtistList=User.objects.filter(is_staff=1, is_blacklisted=False, is_active=True)
    AgreementList = CreatedAgreement.objects.filter(mid__category='SongdewTV')
    ticket_id   = forms.CharField(label='Ticket No#',  widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Ticket No'}) ,required=False)
    title = forms.CharField(label='Title',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter name'}),required=True)
    youtube_url = forms.CharField(label='Youtube Url',widget=forms.TextInput(attrs={'class':'form-control'}))
    assignee = forms.CharField(label='assignee',widget=forms.TextInput(attrs={'class':'form-control','type': 'hidden'}))
    description =forms.CharField(label='Comments',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Comments'}),required=True,max_length=255)
    # videoid = forms.CharField(label = 'Video_id', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Video Id'}) ,required=False)
    agreement_id = ModelMultipleChoiceField(label='Agreement ID', queryset=AgreementList, widget=autocomplete.ModelSelect2(url='agreement-details'),
                        required=False)
        # create url for agreement details
    

    class Meta:
        model = Ticket
        fields = ['ticket_id','title','youtube_url','description','status','assignee', 'source'] 
    
    
    # def clean_ticket_id(self):
    #     ticket_id = self.cleaned_data.get('ticket_id')

    #     if not ticket_id:
    #         raise forms.ValidationError("Please enter a Ticket ID.")

    #     existing_ticket = Ticket.objects.exclude(id=self.instance.id).filter(ticket_id=ticket_id).first()

    #     if existing_ticket:
    #         raise forms.ValidationError("Ticket with this ID already exists.")

    #     return ticket_id

        
            

    def clean_assignee(self):
        
            assignee = self.cleaned_data['assignee']
            
            ticket_id = self.cleaned_data.get('ticket_id')

            

            existing_ticket = Ticket.objects.exclude(id=self.instance.id).filter(ticket_id=ticket_id).first()

            if existing_ticket:
                print("\n",self.fields)
                msg = "Ticket with this ID already exists."
                self.add_error("ticket_id",msg)
                # raise forms.ValidationError(self.fields['ticket_id'].error_messages['invalid'])


            return User.objects.get(id=assignee)




    def save(self,commit = True):
        print("start here")
        instance = super(VideoTicketForm,self).save(commit=False)
        instance.save()
        if instance.source in ('3','4','5','6'):
            if not instance.ticket_id:
                instance.ticket_id = "Offline-{}".format(instance.id)
            instance.save()
        if instance.agreement != None:
            metaId =  save_meta_data(instance.id)
        else:
            print("agreement not present")
        return instance



    
  
    




def save_meta_data(ticket_id):
    print(ticket_id)
    print("1 save meta Data")
    
    existing_meta_data_entry = Meta_Data_Lisiting.objects.filter(ticket_id=ticket_id)
    print("existing data", existing_meta_data_entry)
    print(existing_meta_data_entry.count)
    
    if existing_meta_data_entry.exists():
        print("inside duplicate entry check")
        return 1

    ticket_obj = Ticket.objects.get(id = ticket_id)
    print(ticket_obj)
    # return 1 
    # print(ticket_obj.videoid)
    print(" 2 save meta Data")
    print("source",ticket_obj.source)
    # if ticket_obj.source 
    if ticket_obj.source in ('3','4','5','6'):
        print(" 3 save meta Data")
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
            
            artist_type = ticket_obj.videoid.user.is_type
            start_date = ticket_obj.agreement.signed_date
            end_date = ticket_obj.agreement.agreement_end_date
            agreement_state = ticket_obj.agreement.country.states.first().name
            

            meta_obj = Meta_Data_Lisiting()
            meta_obj.video_name  = ticket_obj.videoid.title
            meta_obj.artist_name = ticket_obj.videoid.user.full_name
            meta_obj.songdew_url = ticket_obj.videoid.user.slug_username
            meta_obj.youtube_url = ticket_obj.videoid.youtube_url
            meta_obj.profile_image = ticket_obj.videoid.user.profile.first()._profile_pic
            meta_obj.artist_type = ticket_obj.videoid.user.is_type
            meta_obj.ticket_id = ticket_obj
            meta_obj.duration_start = start_date
            meta_obj.duration_end = end_date
            meta_obj.territory = agreement_state
            meta_obj.genre = genre
            meta_obj.language = language

            meta_obj.save()

            return   meta_obj.id

        
        
   
    


   

   
class UploadFileForm(forms.ModelForm):
	tv_csv = forms.FileField(required=False)

	class Meta:
		model = UploadFile
		fields = ['tv_csv']

class UploadPlayoutFileForm(forms.ModelForm):
	tv_playout_xls = forms.FileField(required=False)

	class Meta:
		model = UploadPlayoutFile
		fields = ['tv_playout_xls']

class SongdewTvForm1(forms.ModelForm):
    ArtistList=User.objects.filter(is_type__in=['Artist','Band'], is_blacklisted=False, is_active=True)
    CATEGORY_CHOICES = (
            ("", ""),
            ("meet_the_music", "Meet The Music"),
            ("track_tales", "Track Tales"),
            ("world_street_music", "World Street Music"),
            )
    # asset_id				=	forms.IntegerField()
    # meta_tv_id      =   forms.CharField(label='Meta ID',widget=forms.TextInput(attrs={'class':'form-control',}),required=True)
    name 					=	forms.CharField(label='Name',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter name'}),required=True)
    name_hindi 					=	forms.CharField(label='Name in hindi',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter name in hindi'}),required=False)
    category				=	forms.ChoiceField(label='Category',choices=CATEGORY_CHOICES,required=False)
    video_type				=	forms.CharField(label='Video Type',widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    username				=	forms.CharField(label='Username',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'username'}),required=True)
    profile_link			=	forms.CharField(label='Profile Link',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Profile link'}),required=True)
    profile_image			=	forms.ImageField(label='Profile Image',required=False)
    card_image				=	forms.ImageField(label='Card Image',required=False)
    biography 				= 	forms.CharField(label='Biography',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'biography'}),required=True,max_length=115)

    biography_hindi 				= 	forms.CharField(label='Biography in hindi',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'biography in hindi'}),required=False,max_length=115)
    achievement				=	forms.CharField(label='Achievement',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'achievement'}),required=True,max_length=115)
    achievement_hindi	=	forms.CharField(label='Achievementin hindi ',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'achievement in hindi'}),required=False,max_length=115)
    sms_code				=	forms.CharField(label='SMS Code',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'sms code'}),required=False)
    sd_likes				=	forms.CharField(label='Likes',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'likes'}),required=False)
    top_track1				=	forms.CharField(label='Top Track 1',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter the track'}),required=False)
    top_track2				=	forms.CharField(label='Top Track 2',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    top_track3				=	forms.CharField(label='Top Track 3',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    top_track4				=	forms.CharField(label='Top Track 4',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    top_track5				=	forms.CharField(label='Top Track 5',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    title					=	forms.CharField(label='Video Title',widget=forms.TextInput(attrs={'class':'form-control',}),required=True)
    social_followers		=	forms.CharField(label='Social Followers',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    sd_plays				=	forms.CharField(label='Plays',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    genre					=	forms.CharField(label='Genre',widget=forms.TextInput(attrs={'class':'form-control',}),required=True)
    video_id				=	forms.CharField(label='Video Id',widget=forms.TextInput(attrs={'class':'form-control',}),required=True,max_length=9)
    artist_id              =	ModelMultipleChoiceField(label='Artist ID',queryset=ArtistList,widget=autocomplete.ModelSelect2Multiple(url='artist-autocomplete'),required=False)
    band_pic				=	forms.CharField(label='Band Pic',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    video_url				=	forms.CharField(label='Songdew URL',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    youtube_url				=	forms.CharField(label='youtube URL',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm1 			=	forms.CharField(label='Band Member 1',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm1_role 		=	forms.CharField(label='Band Member 1 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm2 			=	forms.CharField(label='Band Member 2',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm2_role 		=	forms.CharField(label='Band Member 2 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm3 			=	forms.CharField(label='Band Member 3',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm3_role 		=	forms.CharField(label='Band Member 3 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm4 			=	forms.CharField(label='Band Member 4',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm4_role 		=	forms.CharField(label='Band Member 4 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm5 			=	forms.CharField(label='Band Member 5',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm5_role 		=	forms.CharField(label='Band Member 5 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm6 			=	forms.CharField(label='Band Member 6',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm6_role 		=	forms.CharField(label='Band Member 6 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm7 			=	forms.CharField(label='Band Member 7',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm7_role 		=	forms.CharField(label='Band Member 7 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm8 			=	forms.CharField(label='Band Member 8',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm8_role 		=	forms.CharField(label='Band Member 8 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm9 			=	forms.CharField(label='Band Member 9',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm9_role 		=	forms.CharField(label='Band Member 9 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm10 			=	forms.CharField(label='Band Member 10',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm10_role		=	forms.CharField(label='Band Member 10 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm11 			=	forms.CharField(label='Band Member 11',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm11_role 		=	forms.CharField(label='Band Member 11 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm12 			=	forms.CharField(label='Band Member 12',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm12_role 		=	forms.CharField(label='Band Member 12 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm13 			=	forms.CharField(label='Band Member 13',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm13_role 		=	forms.CharField(label='Band Member 13 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm14 			=	forms.CharField(label='Band Member 14',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm14_role		=	forms.CharField(label='Band Member 14 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm15 			=	forms.CharField(label='Band Member 15',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm15_role		=	forms.CharField(label='Band Member 15 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    status			=	forms.BooleanField(label='Public',required=False)
    

    class Meta:
        model = Tv
        
        fields = ('video_type','category','name','username','title','video_id','artist_id','profile_link','profile_image','card_image','biography','biography_hindi','achievement','achievement_hindi','sms_code',
            'top_track1','top_track2','top_track3','top_track4','top_track5',
            'genre','band_pic','video_url','youtube_url','bm1','bm1_role','bm2',
            'bm2_role','bm3','bm3_role','bm4','bm4_role',
            'bm5','bm5_role','bm6','bm6_role','bm7',
            'bm7_role','bm8','bm8_role','bm9','bm9_role',
            'bm10','bm10_role','bm11','bm11_role','bm12',
            'bm12_role','bm13','bm13_role','bm14','bm14_role',
            'bm15','bm15_role','social_followers','sd_likes','sd_plays','status', )



    def clean_artist_id(self):
        artist_id = self.cleaned_data['artist_id']
        s=""
        for artist in artist_id:
            s+=str(artist.id)+","
        return s[:-1]

    
        




        
    
    


class UserSearchForm(forms.ModelForm):
    UserList     =  UserProfile.objects.all()
    user         =  ModelMultipleChoiceField(label="Select User", queryset=UserList,widget=autocomplete.ModelSelect2Multiple(url='userprofile-autocomplete'),required=False)
    video_slug  =  forms.CharField(label="Enter Songdew Video Slug",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Ex-raag-kalavati-57'}),required=False)

    class Meta:
        model = UserVideo
        fields = ['user','video_slug']

class UploadFileForm(forms.ModelForm):
    tv_csv = forms.FileField(required=False)

    class Meta:
        model = UploadFile
        fields = ['tv_csv']

class SongdewTvForm(forms.ModelForm):
    ArtistList=User.objects.filter(is_type__in=['Artist','Band'], is_blacklisted=False, is_active=True)
    CATEGORY_CHOICES = (
	    ("", ""),
            ("meet_the_music", "Meet The Music"),
            ("track_tales", "Track Tales"),
            ("world_street_music", "World Street Music"),
            )
    # asset_id				=	forms.IntegerField()
    name 					=	forms.CharField(label='Name',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter name'}),required=True)
    name_hindi 					=	forms.CharField(label='Name in hindi',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter name in hindi'}),required=False)
    category				=	forms.ChoiceField(label='Category',choices=CATEGORY_CHOICES,required=False)
    video_type				=	forms.CharField(label='Video Type',widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    username				=	forms.CharField(label='Username',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'username'}),required=True)
    profile_link			=	forms.CharField(label='Profile Link',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Profile link'}),required=True)
    profile_image			=	forms.ImageField(label='Profile Image',required=False)
    card_image				=	forms.ImageField(label='Card Image',required=False)
    biography 				= 	forms.CharField(label='Biography',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'biography'}),required=True,max_length=115)
    biography_hindi 			= 	forms.CharField(label='Biography in hindi',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'biography in hindi'}),required=False,max_length=115)
    achievement				=	forms.CharField(label='Achievement',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'achievement'}),required=True,max_length=115)
    PE1				=	forms.CharField(label='Achievement Line1',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=29)
    PE2				=	forms.CharField(label='Achievement Line2',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=29)
    PE3				=	forms.CharField(label='Achievement Line3',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=29)
    PE4				=	forms.CharField(label='Achievement Line4',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=28)
    achievement_hindi			=	forms.CharField(label='Achievement in hindi',widget=forms.Textarea(attrs={'class':'form-control','placeholder':'achievement in hindi'}),required=False,max_length=115)
    PH1				=	forms.CharField(label='Achievement Hindi Line1',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=29)
    PH2				=	forms.CharField(label='Achievement Hindi Line2',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=29)
    PH3				=	forms.CharField(label='Achievement Hindi Line3',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=29)
    PH4				=	forms.CharField(label='Achievement Hindi Line4',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'achievement'}),max_length=28)
    sms_code				=	forms.CharField(label='SMS Code',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'sms code'}),required=False)
    sd_likes				=	forms.CharField(label='Likes',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'likes'}),required=False)
    top_track1				=	forms.CharField(label='Top Track 1',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter the track'}),required=False)
    top_track2				=	forms.CharField(label='Top Track 2',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    top_track3				=	forms.CharField(label='Top Track 3',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    top_track4				=	forms.CharField(label='Top Track 4',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    top_track5				=	forms.CharField(label='Top Track 5',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    title					=	forms.CharField(label='Video Title',widget=forms.TextInput(attrs={'class':'form-control',}),required=True)
    social_followers		=	forms.CharField(label='Social Followers',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    sd_plays				=	forms.CharField(label='Plays',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    genre					=	forms.CharField(label='Genre',widget=forms.TextInput(attrs={'class':'form-control',}),required=True)
    video_id				=	forms.CharField(label='Video Id',widget=forms.TextInput(attrs={'class':'form-control',}),required=True,max_length=9)
    artist_id              =	ModelMultipleChoiceField(label='Artist ID',queryset=ArtistList,widget=autocomplete.ModelSelect2Multiple(url='artist-autocomplete'),required=False)
    band_pic				=	forms.CharField(label='Band Pic',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    video_url				=	forms.CharField(label='Songdew URL',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    youtube_url				=	forms.CharField(label='youtube URL',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm1 			=	forms.CharField(label='Band Member 1',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm1_role 		=	forms.CharField(label='Band Member 1 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm2 			=	forms.CharField(label='Band Member 2',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm2_role 		=	forms.CharField(label='Band Member 2 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm3 			=	forms.CharField(label='Band Member 3',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm3_role 		=	forms.CharField(label='Band Member 3 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm4 			=	forms.CharField(label='Band Member 4',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm4_role 		=	forms.CharField(label='Band Member 4 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm5 			=	forms.CharField(label='Band Member 5',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm5_role 		=	forms.CharField(label='Band Member 5 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm6 			=	forms.CharField(label='Band Member 6',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm6_role 		=	forms.CharField(label='Band Member 6 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm7 			=	forms.CharField(label='Band Member 7',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm7_role 		=	forms.CharField(label='Band Member 7 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm8 			=	forms.CharField(label='Band Member 8',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm8_role 		=	forms.CharField(label='Band Member 8 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm9 			=	forms.CharField(label='Band Member 9',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm9_role 		=	forms.CharField(label='Band Member 9 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm10 			=	forms.CharField(label='Band Member 10',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm10_role		=	forms.CharField(label='Band Member 10 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm11 			=	forms.CharField(label='Band Member 11',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm11_role 		=	forms.CharField(label='Band Member 11 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm12 			=	forms.CharField(label='Band Member 12',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm12_role 		=	forms.CharField(label='Band Member 12 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm13 			=	forms.CharField(label='Band Member 13',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm13_role 		=	forms.CharField(label='Band Member 13 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm14 			=	forms.CharField(label='Band Member 14',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm14_role		=	forms.CharField(label='Band Member 14 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm15 			=	forms.CharField(label='Band Member 15',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    #bm15_role		=	forms.CharField(label='Band Member 15 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    status			=	forms.BooleanField(label='Public',required=False)
    meta_tv_id = forms.CharField(widget=HiddenInput(), required=False)
    class Meta:
        model = Tv
        fields = ('video_type','category','name','username','title','video_id','artist_id','profile_link','profile_image','card_image','biography','biography_hindi','achievement','PE1','PE2','PE3','PE4','achievement_hindi','PH1','PH2','PH3','PH4','sms_code',
            'top_track1','top_track2','top_track3','top_track4','top_track5',
            'genre','band_pic','video_url','youtube_url','bm1','bm1_role','bm2',
            'bm2_role','bm3','bm3_role','bm4','bm4_role',
            'bm5','bm5_role','bm6','bm6_role','bm7',
            'bm7_role','bm8','bm8_role','bm9','bm9_role',
            'bm10','bm10_role','bm11','bm11_role','bm12',
            'bm12_role','bm13','bm13_role','bm14','bm14_role',
            'bm15','bm15_role','social_followers','sd_likes','sd_plays','status','meta_tv_id')


    # def __init__(self, *args, **kwargs):
        
    #     super(SongdewTvForm, self).__init__(*args, **kwargs)
    #     self.fields['meta_tv_id'].initial = self.instance.meta_tv_id.id

    def clean_artist_id(self):
        artist_id = self.cleaned_data['artist_id']
        s=""
        for artist in artist_id:
            s+=str(artist.id)+","
        return s[:-1]

    def clean_meta_tv_id(self):
        # print("start Here")
        # print("printng meta id",self.cleaned_data['meta_tv_id'])
        meta_tv = self.cleaned_data['meta_tv_id']
        if meta_tv:
            meta_obj = Meta_Data_Lisiting.objects.filter(id=meta_tv)
        
            if meta_obj.exists():
                self.meta_tv_id = meta_obj[0]
       
            return meta_obj[0]
        
    # def save(self,commit = True):
    #     print("start here by himanshu")
    #     instance = super(SongdewTvForm,self).save(commit=False)
        
    #     meta_id = instance.meta_tv_id
        
    #     print("printnig meta_id", meta_id.id)
        
    #     if meta_id:
    #         meta_obj = Meta_Data_Lisiting.objects.filter(id = meta_id.id)
    #         if meta_obj.exists():
    #             instance.card_image = meta_obj[0].screenshot_upload
    #             instance.save()
    #         return instance
        



#Himanshu Work
class MetaDataForm(forms.ModelForm):

    # obj = Ticket.objects.filter

    queryset = Genre.objects.all()
    GENRE_OPTIONS = ((i.name, i.name) for i in queryset)


    queryset = Language.objects.all()
    LANGUAGE_OPTIONS = [(i.name, i.name) for i in queryset]
    LANGUAGE_OPTIONS.insert(0, ("", ""))


    POPULARITY_CHOICES = (

        ( 'Popular' , 'Popular'),
        ( 'Rising_Star' , 'Rising Star'),
        ('Beginners' , 'Beginners')

    )


    QUALITY_CHOICES = (

        ( 'A+' , 'A+'),
        ( 'A' , 'A'),
        ('B' , 'B')

    )

    MOOD_CHOICES = (

        ( 'Happy' , 'Happy'),
        ( 'Sad' , 'Sad'),
        ('Chill' , 'Chill'),
        ('Funny' , 'Funny'),
        ('Anger' , 'Anger'),
        ('Nostalgic' , 'Nostalgic')

    )

    THEME_CHOICES = (

        ('Love' , 'Love'),
        ('Devotional' , 'Devotional'),
        ('Self_Realization/_Story' , 'Self Realization/ Story'),
        ('Friendship' , 'Friendship'),
        ('Inspiration' , 'Inspiration'),
        ('Heartbreak' , 'Heartbreak'),
        ('Rebel/_Anti-Establishment' , 'Rebel/ Anti-Establishment'),
        ('Travel' , 'Travel'),
        ('Life' , 'Life')


    )


    TYPE_CHOICES = (

        ('Live' , 'Live'),
        ('Storyline' , 'Storyline'),
        ('Animation' , 'Animation'),
        ('Performance_Video' , 'Performance Video'),
        ('Lyrics' , 'Lyrics')

    )

    GENDER_CHOICES = (

        ('Male' , 'Male'),
        ('Female' , 'Female'),
        ('Queer' , 'Queer')

    )

    DEBUT_CHOICES = (

        ('Yes' , 'Yes'),
        ('No' , 'No')

    )


    META_STATUS_CHOICES = (

        ('Broadcast_Ready', 'Broadcast Ready'),
        ('Not-Ready' , 'Not Ready'),
        ('Under_Process' , 'Under Process')

    )


    PROGRAM_CHOICES = (

        ('Best_of_Pop' , 'Best of Pop'),
        ('Best_of_Rock' , 'Best of Rock'),
        ('Best_of_HipHop', 'Best of Hip Hop')

    )

    VIDEO_CHOICES = (

        ('Music_Video', 'Music Video'),
        ('Programme' , 'Programme'),
        ('Promo', 'Promo'),
        ('Opener', 'Opener')

    )
   
    programme_types     = forms.ChoiceField(required = False, widget=forms.Select,choices=VIDEO_CHOICES, label = "TYpe of Programme")
    artist_name         = forms.CharField(label = "Artist Name", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Artist name'}) )
    video_name          = forms.CharField(label = "Video Name", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Video name'}) )
    language            = forms.ChoiceField(required = False, widget=forms.Select,choices=LANGUAGE_OPTIONS, label = "List of Language")
    genre               = forms.ChoiceField(required = False, choices=GENRE_OPTIONS, label="List of Genre")
    artist_type         = forms.CharField(label = "Artist Type" , widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Artist type'}) )
    bm_1 			    = forms.CharField(label='Band Member 1',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm_1_role 		    = forms.CharField(label='Band Member 1 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm_2 			    = forms.CharField(label='Band Member 2',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm_2_role 		    = forms.CharField(label='Band Member 2 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm_3 			    = forms.CharField(label='Band Member 3',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm_3_role 		    = forms.CharField(label='Band Member 3 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm_4 			    = forms.CharField(label='Band Member 4',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    bm_4_role 		    = forms.CharField(label='Band Member 4 Role',widget=forms.TextInput(attrs={'class':'form-control',}),required=False)
    profile_english     = forms.CharField(label = "Profile Description in English(max length:115)", widget=forms.Textarea(attrs={'class':'form-control',}),required=False,max_length=115)
    profile_hindi       = forms.CharField(label = "Profile Description in Hindi(max length:115)", widget=forms.Textarea(attrs={'class':'form-control',}),required=False,max_length=115)
    spotlight_english   = forms.CharField(label = "Spotlight Description in English(max length:115)", widget=forms.Textarea(attrs={'class':'form-control',}),required=False,max_length=115)
    spotlight_hindi     = forms.CharField(label = "Spotlight Description in Hindi(max length:115)", widget=forms.Textarea(attrs={'class':'form-control',}),required=False,max_length=115)
    youtube_url         = forms.CharField(label='Youtube Url',widget=forms.TextInput(attrs={'class':'form-control'}))
    songdew_url         = forms.CharField(label='Songdew Url',widget=forms.TextInput(attrs={'class':'form-control'}))
    popularity_tag      = forms.ChoiceField(required=False, widget=forms.Select,choices=POPULARITY_CHOICES, label = "Popularity")
    video_quality_tag = forms.ChoiceField(required=False, widget=forms.Select,choices=QUALITY_CHOICES, label = "Video Quality")
    video_mood_tag    = forms.ChoiceField(required=False, widget=forms.Select,choices=MOOD_CHOICES, label = "Mood")
    video_themes       = forms.ChoiceField(required=False, widget=forms.Select,choices=THEME_CHOICES, label = "Theme")
    video_type_tag     = forms.ChoiceField(required=False, widget=forms.Select,choices=TYPE_CHOICES, label = "Video Type")
    gender_video_tag    = forms.ChoiceField(required=False, widget=forms.Select,choices=GENDER_CHOICES, label = "Led By")
    debut_video_tag         = forms.ChoiceField(required=False, widget=forms.Select,choices=DEBUT_CHOICES, label = "Debut/Not")
    # video_year_release  = forms.DateField(widget=forms.SelectDateWidget(years=[y for y in range(1930,2050)]),required=False)
    video_year_release  = forms.DateTimeField(required = False, widget=AdminDateWidget())
    # drive_link          = forms.CharField(required=True, label='Drive Link',widget=forms.TextInput(attrs={'class':'form-control'}))         

    # status_check        = forms.ChoiceField(required=False, widget=forms.Select,choices=META_STATUS_CHOICES, label = "Broadcast Status Check")
    profile_image       = forms.ImageField(label="Profile Image", required = False)
    playlist_inclusion  = forms.ChoiceField(required=False, widget=forms.Select,choices=PROGRAM_CHOICES, label = "Playlist Incluison")
    territory           = forms.CharField(label = "Territory", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Agreement Territory'}))
    duration_start      = forms.DateTimeField(required = False, widget=AdminDateWidget())
    duration_end        = forms.DateTimeField(required = False, widget=AdminDateWidget())
    track_1             = forms.CharField(label=' Track 1',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Top Tracks 1'}),required=False)
    track_2             = forms.CharField(label='Track 2',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Top Tracks 2'}),required=False)
    track_3             = forms.CharField(label='Track 3',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Top Tracks 3'}),required=False)
    track_4             = forms.CharField(label='Track 4',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Top Tracks 4'}),required=False)
    screenshot_upload   = forms.ImageField(label="Screenshot for Card", required = True)
    # epk                 = forms.CharField(label = "Epk Profile", widget=forms.TextInput(attrs={'class':'form-control','value':10}))
    ticket_id = forms.ModelChoiceField(
         queryset=Ticket.objects.all(),  

         widget=forms.Select(attrs={'class': 'your-css-class'}),  
     )
    drive_link    = forms.CharField(required=True, label='Drive Link',widget=forms.TextInput(attrs={'class':'form-control'})) 
    


    class Meta:
        model = Meta_Data_Lisiting
        fields = ('programme_types', 'video_name', 'artist_name', 'songdew_url', 'territory', 'duration_start' ,
                'duration_end', 'genre', 'language', 'youtube_url', 'profile_image', 'artist_type', 'bm_1', 'bm_1_role',
                'bm_2', 'bm_2_role', 'bm_3', 'bm_3_role', 'bm_4', 'bm_4_role', 'track_1', 'track_2', 'track_3', 'track_4',
                'profile_english', 'profile_hindi', 'spotlight_english', 'spotlight_hindi', 'video_quality_tag', 
                'gender_video_tag', 'video_type_tag', 'video_year_release',  'video_mood_tag', 
                'video_themes', 'screenshot_upload', 'playlist_inclusion','ticket_id', 'broadcast_ready','drive_link')
    






        


