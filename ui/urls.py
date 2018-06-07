from django.urls import path

from . import views

urlpatterns = [

   # ex: a request to ui
    path('', views.index, name='index'),

    # ex: /ui/machine/2/
    path( 'machine/<str:machine_id>/', views.machine_detail, name='machine-detail-view'),


# ex: /ui/person_from_prox_card/00087654/ what person is associated with this prox card number? 
    #  TO RETREIVE A MACHINE ASSOCIATED WITH AN INTERLOCK MAC ADDRESS
    path('person_from_prox_card/<str:proxcard_str>', 
    	views.person_from_prox_card, 
    	name='PERSON-FROM-PROX-CARD'),
    
    
 	# ex: /ui/get_machine_lab_from_mac/34:45:34:35:98/ what machine is connected to this interlock MAC? 
    #  TO RETREIVE A MACHINE ASSOCIATED WITH AN INTERLOCK MAC ADDRESS
    path('get_machine_lab_from_mac/<str:mac>', 
    	views.get_machine_lab_from_mac, 
    	name='MACHINE-FROM-INTERLOCK-MAC'),
    
    # ex: /iu/machine_users/1234/17 is this user OK for this machine? 
    path('machine_users/<str:person_id>/<str:machine_id>/',
    	views.machine_users,
    	 name='USER-LIST-RESULTS'),

    # ex: /iu/machine_supervisors/1234/17  is this supervisor OK for this machine? 
    path('machine_supervisors/<str:person_id>/<str:machine_id>/',
    	views.machine_supervisors,
    	 name='SUPER-LIST-RESULTS'),

    
    # ex /ui/first_swipe_access/00894567/34:45:34:35:98 
    path('first_swipe_access/<str:proxcardid1>/<str:maccad>',
    	views.first_swipe_access,
    	 name='First-swipe-access-results'),


    # ex /ui/second_swipe_access/00894567/0876567/34:45:34:35:98 
    path('second_swipe_access/<str:proxcardid1>/<str:proxcardid2>/<str:maccad>',
    	views.second_swipe_access,
    	 name='Second-swipe-access-results'),
 
]