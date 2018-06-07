import json
from django.shortcuts import render
import ui.proxlookup   ### get_hawkID comes from here
# Create your views here.

from django.http import HttpResponse

from .models import (Interlock,   Lab,    
    Machine,InterlockLookup,
    Person)

#from django.template import loader
from django.shortcuts import render

def index(request):
    machine_list=Machine.objects.all()
    #print(machine_list)
    #template=loader.get_template('ui/index.html')
    context={
        'machine_list': machine_list,
    }
    #return HttpResponse(template.render(context, request))
    return render(request,'ui/index.html',context)
    
def machine_detail(request, machine_id):
    m=Machine.objects.get(pk=machine_id)
    return HttpResponse("These are the detailsfor machine  %s, the %s. "  %  (m.id, m.name))

def get_machine_lab_from_mac(request, mac):
    inter=Interlock.objects.get(mac=mac)
    lookup=InterlockLookup.objects.get(interlock=inter)   
    mach=lookup.machine
    lab=mach.lab_containing_machine
    dicout=dict( 
    manufacturing_date= str(inter.manufacturing_date),
    controller_serial_number=inter.controller_serial_number,
    relay_box_serial_number=inter.relay_box_serial_number,
    machine_id=mach.id,
    university_inventory_number=mach.university_inventory_number,
    manufacturer_serial_number = mach.manufacturer_serial_number,
    name = mach.name,
    lab_containing_machine =mach.lab_containing_machine.name,
    kind_of_swipe_needed =mach.kind_of_swipe_needed,
    start_time     = mach.start_time,
    end_time   = mach.end_time,
    minutes_enabled = mach.minutes_enabled,
    uses_estop = mach.uses_estop,
    lab_name = lab.name,
    lab_room =  lab.room,
    lab_start_time = lab.start_time,
    lab_end_time = lab.end_time
    )
    return HttpResponse(json.dumps(dicout))
    


def person_from_prox_card(request, proxcard_str):
    hawkid=ui.proxlookup.get_hawkID(proxcard_str)
    pers=Person.objects.get(university_id=hawkid)
    dicout=dict(
    university_id=pers.university_id,name=pers.name, 
    kind_of_person=pers.kind_of_person,
    start_date =str(pers.start_date),
    end_date =str(pers.end_date),
    start_time = pers.start_time,
    end_time = pers.end_time
    )
    return HttpResponse(json.dumps(dicout))
    
def  machine_users(request,person_id,machine_id):
    # return HttpResponse("This stub will answer is person %s on user list of machine %s" %   (person_id ,machine_id)) 
    queryset1=Machine.objects.filter(pk=machine_id)
    actual_machine=queryset1[0]
    queryset2=actual_machine.user_list
    parperson=Person.objects.get(university_id=person_id)
    if queryset2.filter(university_id=parperson.university_id).exists():
        return  HttpResponse("Yes, person %s IS on user list of machine %s" %   (person_id ,machine_id))
    else:
        return  HttpResponse("No, person %s IS NOT on user list of machine %s" %   (person_id ,machine_id)) 

def  machine_supervisors(request,person_id,machine_id):
    # return HttpResponse("This stub will answer is person %s on user list of machine %s" %   (person_id ,machine_id)) 
    queryset1=Machine.objects.filter(pk=machine_id)
    actual_machine=queryset1[0]
    queryset2=actual_machine.supervisor_list
    parperson=Person.objects.get(university_id=person_id)
    if queryset2.filter(university_id=parperson.university_id).exists():
        return  HttpResponse("YES, person %s IS on supervisor list of machine %s" %   (person_id ,machine_id))
    else:
        return  HttpResponse("NO, person %s IS NOT on supervisor list of machine %s" %   (person_id ,machine_id)) 

import datetime


def first_swipe_access(request,proxcardid1,maccad):

    (OK,reason)=first_swipe_aux(proxcardid1,maccad)
    if OK:
        return  HttpResponse("GRANTED, %s" % reason)
    else:
        return  HttpResponse("DENIED, %s" % reason)


def first_swipe_aux(proxcardid1,maccad):
    def to_minutes(x):
        if isinstance(x,str):
            partuple=x.partition(':')
            hrs=int(partuple[0])
            mins=int(partuple[2])
            return (mins+60*hrs)
        else:
            print('ERROR IN TO-MINUTES')
            return(30)    



    OK=True; reason="None"    
    #### VALIDATE THE INPUT PARAMETERS
    # get the person from the proxcard number
    hawkid=ui.proxlookup.get_hawkID(proxcardid1)
    if  hawkid==None:
        #reason= 'Proxcard %s is not in the database.' % proxcardid1
        reason='Unknown proxcard'
        OK=False
    else:
        actual_person=Person.objects.get(university_id=hawkid)
        # get the machine from the mac address of the controller
        if not Interlock.objects.filter(mac=maccad).exists():
            #reason=('This interlock %s is not in the database.' % maccad)
            reason='Unknown interlock'
            OK=False
    ####  input parameters are OK         
        else: 
            actual_interlock=Interlock.objects.get(mac=maccad) 
            if not InterlockLookup.objects.filter(interlock=actual_interlock).exists():
                #reason=('This interlock references a machine that is not in the database.')
                reason='Unknown machine in db'
                OK=False;
            else:
                associated_lookup=InterlockLookup.objects.get(interlock=actual_interlock)   
                actual_machine=associated_lookup.machine
                
    #### second level of validation is finished
                # check if this person is all-access
                if actual_person.kind_of_person=='all access':
                    #reason=('%s is all access.'% actual_person.name)
                    reason='Is all access'
                    OK=True
                else:
                    # get the lab
                    lab_machine_is_in=actual_machine.lab_containing_machine
                    # check the times 
                    now=(datetime.datetime.now())
                    minutesnow=now.minute+60*now.hour
                    if minutesnow<to_minutes(actual_machine.start_time):
                        OK=False; 
                        #reason=' Machine %s start time=%s, time now=%d:%d' % (actual_machine.name,actual_machine.start_time,now.hour,now.minute)
                        reason='Machine not open yet'
                    else:
                        if minutesnow<to_minutes(actual_person.start_time):
                            OK=False; 
                            #reason='User %s start time=%s, time now=%d:%d'% (actual_person.name,actual_person.start_time,now.hour,now.minute)
                            reason='Too early for you'
                        else: 
                            if minutesnow<to_minutes(lab_machine_is_in.start_time):
                                OK=False; 
                                #reason="Lab %s start time is %s, time now=%d:%d" % (lab_machine_is_in.name,lab_machine_is_in.start_time,now.hour,now.minute)
                                reason='Lab not open yet'
                            else:
                                if minutesnow>to_minutes(actual_machine.end_time):
                                    OK=False; 
                                    #reason=' Machine %s end time=%s, time now=%d:%d' % (actual_machine.name,actual_machine.end_time,now.hour,now.minute)
                                    reason='Machine closed'
                                else:
                                    if minutesnow>to_minutes(actual_person.end_time):
                                        OK=False; 
                                        #reason='User %s end time=%s, time now=%d:%d' % (actual_person.name,actual_person.end_time,now.hour,now.minute)
                                        reason='Too late for you'
                                    else:
                                        if minutesnow<to_minutes(lab_machine_is_in.start_time):
                                            OK=False; 
                                            #reason="Lab %s end time is %s, time now=%d:%d" % (lab_machine_is_in.name,lab_machine_is_in.end_time,now.hour,now.minute)
                                            reason="Lab closed" 
                                        else:
                                            # is this person on the machine supervisor list? 
                                            manager1=actual_machine.supervisor_list # the manager of the many to many relation
                                            if manager1.filter(university_id=actual_person.university_id).exists():
                                                OK=True; reason=("Person %s is actually on the supervisor list of machine %s." %   (actual_person.name ,actual_machine.name)) 
                                            else: # person is not on machine supervisor list, check to see if on machine user list                                     
                                                # is this person on the machine user list? 
                                                manager2=actual_machine.user_list # the manager of the many to many relation
                                                if not manager2.filter(university_id=actual_person.university_id).exists():
                                                    OK=False; 
                                                    #reason=("Person %s IS NOT on user or supervisor  list of machine %s." %   (actual_person.name ,actual_machine.name)) 
                                                    reason='Not on user list'
                                                else:
                                                    if actual_machine.kind_of_swipe_needed=='single':
                                                        OK=True; reason=("Person %s IS on user list of machine %s." %   (actual_person.name,actual_machine.name))
                                                    else:
                                                        OK=False; reason=('Second swipe needed.')    
    return(OK,reason)



def second_swipe_access(request,proxcardid1,proxcardid2,maccad):
    (OK,reason)=first_swipe_aux(proxcardid1,maccad)
    if OK:
        return  HttpResponse("GRANTED, first swipe, %s" % reason)
    else:
        if reason.lstrip()=='Second swipe needed.':
            (OK,reason)=second_swipe_aux(proxcardid1,proxcardid2,maccad)
            if OK:
                return  HttpResponse("GRANTED, %s" % reason)
            else:
                return  HttpResponse("DENIED, %s" % reason)
        else:
            return  HttpResponse("DENIED, %s" % reason)        




def  second_swipe_aux(proxcardid1,proxcardid2,maccad):
    # get the second person from the proxcard number
    hawkid=ui.proxlookup.get_hawkID(proxcardid2)
    if hawkid==None:
        reason= 'Proxcard %s is not in the database.' % proxcardid2
        reason='Unknown proxcard'
        OK=False
    else:
        actual_second_person=Person.objects.get(university_id=hawkid)
        # check if this person is all-access
        if actual_second_person.kind_of_person=='all access':
            #reason=('2nd person %s is all access.'% actual_second_person.name)
            reason='Is all access'
            OK=True
        else:
            actual_interlock=Interlock.objects.get(mac=maccad) 
            associated_lookup=InterlockLookup.objects.get(interlock=actual_interlock)   
            actual_machine=associated_lookup.machine
            if actual_machine.kind_of_swipe_needed=='supervisor':
                # is this person on the machine supervisor list? 
                manager1=actual_machine.supervisor_list # the manager of the many to many relation
                if manager1.filter(university_id=actual_second_person.university_id).exists():
                    reason=("2nd person as supervisor %s IS on the Supervisor list of machine %s." %   (actual_second_person.name,actual_machine.name))
                    reason='On supervisor list'
                    OK=True
                else:
                    reason=("2nd person as supervisor %s IS NOT on the Supervisor list of machine %s." %   (actual_second_person.name ,actual_machine.name)) 
                    reason='Not on supervisor list'
                    OK=False
            else: 
                if actual_machine.kind_of_swipe_needed=='two students':  # two student situation
                    # is this swipe the same as the first one?
                    if proxcardid1==proxcardid2:
                        OK=False
                        reason='Different swipe required' 
                    else:   
                        # is this person on the supervisor list? 
                        manager3=actual_machine.supervisor_list # the manager of the many to many relation
                        if manager3.filter(university_id=actual_second_person.university_id).exists():
                            OK=True; 
                            reason='Is a supervisor'
                        else:
                            # is this person on the machine user list? 
                            manager2=actual_machine.user_list # the manager of the many to many relation
                            if not manager2.filter(university_id=actual_second_person.university_id).exists():
                                OK=False; reason=("2nd person as student %s IS NOT on user list of machine %s." %   (actual_second_person.name ,actual_machine.name)) 
                                reason='Not on user list'
                            else:
                                OK=True; reason=("2nd person as student %s IS on user list of machine %s." %   (actual_second_person.name,actual_machine.name))                
                                reason='On user list'
    return(OK,reason)


    
