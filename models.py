from django.db import models
from django.conf import settings
from songdew.config import *
from songdewUser.validators import *
from datetime import datetime
from songdewUser.models import User, UserVideo,UserProfile
from language.models import Language
from genre.models import Genre
from agreement.models import CreatedAgreement
from googletrans import Translator

# Create your models here.

    # def __init__(self, *args):
    # 	if username:
    # 		self.name=username

class Tv_Fpc(models.Model):

    video_id				=	models.CharField(max_length=255)
    artist_id				=	models.CharField(max_length=255,null=True,blank=True)
    scheduled_date			=	models.DateField(blank=True, null=True,default=datetime.now().date())
    status 					= 	models.BooleanField(default=True)
    created_date 			=   models.DateTimeField(auto_now_add=True)
    updated_date 			=   models.DateTimeField(auto_now=True)

    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'Tv_Fpc')

        # permissions = (
        #     ('view_tv_fpc', 'Can view Songdew TV FPC'),
        # )




class Tv_Playoutlist(models.Model):
    video_id				=	models.CharField(max_length=255)
    artist_id				=	models.CharField(max_length=255,null=True,blank=True)
    scheduled_date			=	models.CharField(max_length=255,null=True,blank=True)
    scheduled_time			=	models.CharField(max_length=255,null=True,blank=True)
    scheduled_date_time			=	models.CharField(max_length=255,null=True,blank=True)
    notification 			= 	models.IntegerField(default=0)
    duration 				= 	models.IntegerField(default=0)
    created_date 			=   	models.DateTimeField(auto_now_add=True)
    updated_date 			=   	models.DateTimeField(auto_now=True)
    sms_sent_times			= 	models.IntegerField(default=0)
    sms_sent_datetime			= 	models.CharField(max_length=255,null=True,blank=True)

    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'Tv_Playoutlist')

        # permissions = (
        #     ('view_tv_fpc', 'Can view Songdew TV Playout'),
        # )


class UploadFile(models.Model):

    tv_csv				= models.FileField(upload_to=tv_csv_upload_path, blank=True, null=True)
    uploaded_date 		= models.DateTimeField(auto_now=True)

    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'upload_file_tv')

        # permissions = (
        #     ('view_tv_upload_file', 'Can view Songdew TV FPC'),
        # )

class UploadPlayoutFile(models.Model):

    tv_playout_xls			= models.FileField(upload_to=tv_playout_upload_path, blank=True, null=True)
    uploaded_date 		= models.DateTimeField(auto_now=True)

    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'upload_file_tv_playout')

        # permissions = (
        #     ('view_tv_upload_file', 'Can view Songdew TV Playout'),
        # )

class d2hSingingstar(models.Model):
    user_id					=	models.IntegerField(null=True,blank=True)
    name					=	models.CharField(max_length=255)
    email					=	models.CharField(max_length=255,null=True,blank=True)
    music_url				=	models.CharField(max_length=255,null=True,blank=True)
    music_file				=   models.FileField(upload_to=d2h_file_directory_path)
    mobile 					= 	models.CharField(max_length=14,null=True)
    d2h_registerd_mobile	=   models.CharField(max_length=14,null=True)
    status 					= 	models.BooleanField(default=True)
    created_date 			=   models.DateTimeField(auto_now_add=True)
    updated_date 			=   models.DateTimeField(auto_now=True)
    is_shortlisted 			= models.NullBooleanField()
    is_winner 				= models.NullBooleanField()
    is_rejected 			= models.NullBooleanField()
    is_sms_sent 			= models.NullBooleanField()
    is_mail_sent 			= models.NullBooleanField()
    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'d2hSingingstar')

        # permissions = (
        #     ('view_d2hSingingstar', 'Can view Songdew d2hSingingstar'),
        # )



        # permissions = (
        #     ('view_video_library', 'Can view Songdew video_library'),
        # )


#Himanshu Work
SourceCheck = (
	('1','Website (Upload)'),
	('2','Website (Broadcast)'),
	('3','Offline (ReachOut)'),
    ('4','Offline (Label)'),
    ('5','Offline (Music Release)'),
    ('6','Offline (Others)')

    
	)

TicketStatus = (
	('TO_DO','To Do'),
	# ('IN_PROGRESS','In Progress'),
	# ('IN_REVIEW','In Review'),
	('REJECTED','Rejected'),
	('APPROVED','Approved')
	)
class Ticket(models.Model):
    ticket_id= models.CharField(max_length=100, null=True, blank = True)
    title = models.CharField(max_length=100)
    assignee = models.ForeignKey(User, null=True, blank = True, on_delete=models.SET_NULL)
    videoid = models.ForeignKey(UserVideo, null=True, blank = True, on_delete=models.SET_NULL)
    # artist_name = models.ForeignKey(UserProfile, related_name="artist_name", null=True, blank = True, on_delete=models.SET_NULL)
    youtube_url = models.CharField(max_length=255,blank=True)
    status = models.CharField(max_length=25, choices=TicketStatus, default=TicketStatus[0])
    source = models.CharField(max_length = 200, choices=SourceCheck, default=SourceCheck[0])
    description = models.TextField()
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)
    agreement = models.ForeignKey(CreatedAgreement, null = True, blank = True, on_delete = models.SET_NULL)
    



    #Himanshu Work
    # create source field here and then create choices option like status



    class Meta:
        verbose_name = "Tv Videos Ticket"
        verbose_name_plural = "Tv Videos Ticket"


















popular_tag = (

    ( 'Popular' , 'Popular'),
    ( 'Rising_Star' , 'Rising Star'),
    ('Beginners' , 'Beginners')

)


quality_tag = (

    ( 'A+' , 'A+'),
    ( 'A' , 'A'),
    ('B' , 'B')

)


mood_tag = (

    ( 'Happy' , 'Happy'),
    ( 'Sad' , 'Sad'),
    ('Chill' , 'Chill'),
    ('Funny' , 'Funny'),
    ('Anger' , 'Anger'),
    ('Nostalgic' , 'Nostalgic')

)




theme_tag = (

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


type_tag = (

    ('Live' , 'Live'),
    ('Storyline' , 'Storyline'),
    ('Animation' , 'Animation'),
    ('Performance_Video' , 'Performance Video'),
    ('Lyrics' , 'Lyrics')

)

gender_tag = (

    
    ('Male' , 'Male'),
    ('Female' , 'Female'),
    ('Queer' , 'Queer')

)

debut_tag = (

    ('Yes' , 'Yes'),
    ('No' , 'No')

)


meta_status = (

    ('Broadcast_Ready', 'Broadcast Ready'),
    ('Not-Ready' , 'Not Ready'),
    ('Under_Process' , 'Under Process')

)


programs = (

    ('Best_of_Pop' , 'Best of Pop'),
    ('Best_of_Rock' , 'Best of Rock'),
    ('Best_of_HipHop', 'Best of Hip Hop')
   
    

)

programme_type = (

    ('Music_Video', 'Music Video'),
    ('Programme' , 'Programme'),
    ('Promo', 'Promo'),
    ('Opener', 'Opener')


)

status_meta = (
    ('Yes', 'Yes'),
    ('No', 'No')
)

# class Ticket_Create_agreement(models.Model):
#     ticket_agreement = models.ForeignKey(CreatedAgreement, null = True, blank = True, on_delete = models.SET_NULL)

#     class Meta:

        # db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'Tv_ticket_agreements')


class Program(models.Model):

    status  =   models.CharField(max_length=25, choices=TicketStatus, default=meta_status[0])
    created_at  =   models.DateTimeField('created at', auto_now_add=True)
    updated_at  =   models.DateTimeField('updated_at', auto_now_add = True)
    Program     =   models.CharField(max_length=50, choices = programs, default = programs[0])
    # classic_hiphop  =   models.CharField(max_length=255,null=True,blank=True)
    # classic_rock    =   models.CharField(max_length=255,null=True,blank=True)
    # classic_pop     =   models.CharField(max_length=255,null=True,blank=True)

    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'Tv_Program')









class Meta_Data_Lisiting(models.Model):
    ticket_id           =   models.ForeignKey(Ticket, null = True, blank = True, on_delete = models.SET_NULL)
    artist_name         =   models.CharField(max_length=255,null=True,blank=True)
    video_name          =   models.CharField(max_length=255,null=True,blank=True)
    language            =   models.CharField(max_length=255,null=True,blank=True)
    genre               =   models.CharField(max_length=255,null=True,blank=True)
    bm_1 			    =	models.CharField(max_length=255,null=True,blank=True)
    bm_1_role 		    =	models.CharField(max_length=255,null=True,blank=True)
    bm_2 			    =	models.CharField(max_length=255,null=True,blank=True)
    bm_2_role 		    =	models.CharField(max_length=255,null=True,blank=True)
    bm_3 			    =	models.CharField(max_length=255,null=True,blank=True)
    bm_3_role 		    =	models.CharField(max_length=255,null=True,blank=True)
    bm_4 			    =	models.CharField(max_length=255,null=True,blank=True)
    bm_4_role 		    =	models.CharField(max_length=255,null=True,blank=True)
    profile_english     =   models.TextField(null = True, blank = True)
    profile_hindi       =   models.TextField(null = True, blank = True)
    spotlight_english   =   models.TextField(null = True, blank = True)
    spotlight_hindi     =   models.TextField(null = True, blank = True)
    youtube_url         =   models.CharField(max_length=255,null=True,blank=True)
    songdew_url         =   models.CharField(max_length=255,null=True,blank=True)
    popularity_tag      =   models.CharField(max_length=25, choices = popular_tag, null = True, blank=True)
    video_quality_tag   =   models.CharField(max_length=25, choices = quality_tag, null = True, blank=True)
    video_mood_tag    =   models.CharField(max_length=25, choices = mood_tag, null = True, blank=True)
    video_themes        =   models.CharField(max_length=25, choices = theme_tag, null = True, blank=True)
    video_type_tag      =   models.CharField(max_length=25, choices = type_tag, null = True, blank=True)
    gender_video_tag              =   models.CharField(max_length=25, choices = gender_tag, null = True, blank=True)
    debut_video        =   models.CharField(max_length=25, choices = debut_tag, null = True, blank=True)
    video_year_release  =  models.DateField(null=True,blank=True)
    # ticket_aggrement    =   models.ForeignKey(Ticket_Create_agreement, null = True, blank = True, on_delete = models.SET_NULL)
    status_check        =   models.CharField(max_length=25, choices=status_meta, default=status_meta[0])
    created_date        =   models.DateTimeField('created at', auto_now_add=True)
    updated_date        =   models.DateTimeField('updated at', auto_now=True)
    profile_image	    =	models.ImageField(upload_to=tv_profile_image_path, blank=True, null=True, validators=[validate_image_file_extension])
    playlist_inclusion  =   models.CharField(max_length=50, choices=programs, default= programs[0])
    programme_types     =   models.CharField(max_length = 50, choices = programme_type, default = programme_type[0])
    territory           =   models.CharField(max_length=255,null=True,blank=True)
    duration_start      =   models.DateTimeField('duration start', null = True,blank = True)
    duration_end        =   models.DateTimeField('duration start',null = True,blank = True)
    track_1             =   models.CharField(max_length=255,null=True,blank=True)
    track_2             =   models.CharField(max_length=255,null=True,blank=True)
    track_3             =   models.CharField(max_length=255,null=True,blank=True)
    track_4             =   models.CharField(max_length=255,null=True,blank=True)
    screenshot_upload   =   models.ImageField(upload_to=tv_profile_image_path, blank=True, null=True, validators=[validate_image_file_extension])
    artist_type         =   models.CharField(max_length=255,null=True,blank=True)
    broadcast_ready     =   models.BooleanField(default=False)
    drive_link          =   models.CharField(max_length=255,null=True,blank=True)


    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'Tv_meta_data')



class Tv(models.Model):

    
    video_type				=	models.CharField(max_length=255,default="video")
    asset_id				=	models.IntegerField(default=0)
    category				=	models.CharField(max_length=255,null=True,blank=True)
    name 					=	models.CharField(max_length=255)
    name_hindi					=	models.CharField(max_length=255,null=True,blank=True)
    profile_link			=	models.CharField(max_length=255)
    username				=	models.CharField(max_length=255)
    biography 				= 	models.TextField()
    biography_hindi 			= 	models.TextField(max_length=255,null=True,blank=True)
    achievement				=	models.TextField()
    PE1					=	models.CharField(max_length=50,null=True,blank=True)
    PE2					=	models.CharField(max_length=50,null=True,blank=True)
    PE3					=	models.CharField(max_length=50,null=True,blank=True)
    PE4					=	models.CharField(max_length=50,null=True,blank=True)
    achievement_hindi			=	models.TextField(max_length=255,null=True,blank=True)
    PH1					=	models.CharField(max_length=50,null=True,blank=True)
    PH2					=	models.CharField(max_length=50,null=True,blank=True)
    PH3					=	models.CharField(max_length=50,null=True,blank=True)
    PH4					=	models.CharField(max_length=50,null=True,blank=True)
    checked_out				=	models.IntegerField(default=0)
    sms_code				=	models.CharField(max_length=255,default="012345")
    sd_likes				=	models.CharField(max_length=255,null=True,blank=True)
    top_track1				=	models.CharField(max_length=255,null=True,blank=True)
    top_track2				=	models.CharField(max_length=255,null=True,blank=True)
    top_track3				=	models.CharField(max_length=255,null=True,blank=True)
    top_track4				=	models.CharField(max_length=255,null=True,blank=True)
    top_track5				=	models.CharField(max_length=255,null=True,blank=True)
    title					=	models.CharField(max_length=255,null=True,blank=True)
    social_followers		=	models.CharField(max_length=255,null=True,blank=True)
    sd_plays				=	models.CharField(max_length=255,null=True,blank=True)
    genre					=	models.CharField(max_length=255)
    video_id				=	models.CharField(max_length=10,validators=[validate_video_id],unique=True)
    artist_id				=	models.CharField(max_length=255,null=True,blank=True)
    profile_image			=	models.ImageField(upload_to=tv_profile_image_path, blank=True, null=True, validators=[validate_image_file_extension])
    card_image				=	models.ImageField(upload_to=tv_card_image_path, blank=True, null=True, validators=[validate_image_file_extension])
    band_pic				=	models.CharField(max_length=255,null=True,blank=True)
    video_url				=	models.CharField(max_length=255,null=True,blank=True)
    youtube_url				=	models.CharField(max_length=255,null=True,blank=True)
    bm1 			=	models.CharField(max_length=255,null=True,blank=True)
    bm1_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm2 			=	models.CharField(max_length=255,null=True,blank=True)
    bm2_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm3 			=	models.CharField(max_length=255,null=True,blank=True)
    bm3_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm4 			=	models.CharField(max_length=255,null=True,blank=True)
    bm4_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm5 			=	models.CharField(max_length=255,null=True,blank=True)
    bm5_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm6 			=	models.CharField(max_length=255,null=True,blank=True)
    bm6_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm7 			=	models.CharField(max_length=255,null=True,blank=True)
    bm7_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm8 			=	models.CharField(max_length=255,null=True,blank=True)
    bm8_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm9 			=	models.CharField(max_length=255,null=True,blank=True)
    bm9_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm10 			=	models.CharField(max_length=255,null=True,blank=True)
    bm10_role		=	models.CharField(max_length=255,null=True,blank=True)
    bm11 			=	models.CharField(max_length=255,null=True,blank=True)
    bm11_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm12 			=	models.CharField(max_length=255,null=True,blank=True)
    bm12_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm13 			=	models.CharField(max_length=255,null=True,blank=True)
    bm13_role 		=	models.CharField(max_length=255,null=True,blank=True)
    bm14 			=	models.CharField(max_length=255,null=True,blank=True)
    bm14_role		=	models.CharField(max_length=255,null=True,blank=True)
    bm15 			=	models.CharField(max_length=255,null=True,blank=True)
    bm15_role		=	models.CharField(max_length=255,null=True,blank=True)
    ordering				=	models.CharField(max_length=255,null=True,blank=True,default=0)
    status 					= 	models.BooleanField(default=True) # This is for soft-delete
    is_update 				=	models.BooleanField(default=False)
    is_update_datetime		=	models.CharField(max_length=255,null=True,blank=True)
    created_date 			=   models.DateTimeField(auto_now_add=True)
    updated_time 			=   models.DateTimeField(auto_now=True)
    youtube_likes			=	models.CharField(max_length=255,null=True,blank=True)
    youtube_plays			=	models.CharField(max_length=255,null=True,blank=True)
    meta_tv_id                 =  models.ForeignKey(Meta_Data_Lisiting, null=True, blank = True, on_delete=models.SET_NULL)

    def save(self,*args,**kwargs):


        self.is_update = True
        print("Is_Update on tv ",self.is_update)
        super(Tv, self).save(*args, **kwargs)

    class Meta:

        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'Tv')

        # permissions = (
        #         ('view_tv', 'Can view Songdew TV'),
        #     )
    @property
    def last_update(self):
        return self.is_update_datetime
    """docstring for ClassName"""
    def __str__(self):
        return self.video_id



class video_library(models.Model):
    GRADE = (
        ("A", "A"),
        ("B", "B"),
        ("C","C"),
        ("D","D")
    )
    tv_video = models.ForeignKey(Tv,on_delete=models.CASCADE)
    language = models.CharField(max_length=100)
    program_category = models.CharField(max_length=100)
    duration = models.CharField(max_length=100,blank=True)
    drive_link = models.CharField(max_length=255,blank=True)
    grade = models.CharField(max_length=1,choices=GRADE)
    playlist_name = models.CharField(max_length=255,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default = False)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = '{0}_{1}'.format(settings.DB_TABLE_PREFIX,'video_library')
        verbose_name_plural = "Video Library"
