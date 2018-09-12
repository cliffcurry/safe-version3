from django.db import models
from datetime import date

#from netaddr import EUI, mac_bare

#from macaddress import format_mac
from macaddress.fields import MACAddressField

# Create your models here.
class Interlock(models.Model):
   mac=models.CharField(max_length=17,primary_key=True)
   #mac=MACAddressField(primary_key=True,integer=False)
   manufacturing_date=models.DateField(auto_now=False, auto_now_add=False,blank=True)   
   controller_serial_number=models.IntegerField(blank=True)
   relay_box_serial_number=models.IntegerField(blank=True)
   def __str__(self):
        return (str(self.mac)+" = #"+
          str(self.controller_serial_number))


        
  
class Lab(models.Model):
   name = models.CharField(max_length=30,primary_key=True)  # the human readable name of the lab
   room = models.CharField(max_length=30, blank=True) # room and building of this lab ..ex '105 SC' 
   start_time = models.CharField(max_length=30)  # lab opens at this time
   end_time = models.CharField(max_length=30)   # lab closes at this time
   def __str__(self):
        return self.name+', in '+self.room      

class Person(models.Model):
   UNDERGRADUATE = 'undergraduate'
   GRADSTUDENT = 'two students'
   TA = 'ta'
   STAFF= 'staff'
   FACULTY= 'faculty'
   GRANTED_ALL_ACCESS= 'all access'
   KIND_OF_PERSON=( 
    (UNDERGRADUATE ,'undergraduate'),
    (GRADSTUDENT,'gradstudent'),
    (TA ,'ta'),
    (STAFF, 'staff'),
    (FACULTY, 'faculty'),
    (GRANTED_ALL_ACCESS, 'all access')
   )
   university_id = models.CharField(max_length=30,primary_key=True)  # unique university ID for this person
   name = models.CharField(max_length=80)  # name of person
   kind_of_person = models.CharField(max_length=30,choices=KIND_OF_PERSON,default=UNDERGRADUATE)  # student, ta, faculty, staff, all-access?
   start_date = models.DateField()  # day the person is allowed to use all devices 
   end_date = models.DateField()  # day the person is no longer allowed to use any devices
   start_time = models.CharField(max_length=30)  # timeof day this person is allowed to use stuff
   end_time = models.CharField(max_length=30)   # timeof day this person is no longer allowed to use stuff
   def __str__(self):
        return (str(self.university_id)+' ,'+self.name)


class Machine(models.Model):
   SINGLE = 'single'
   TWO_STUDENTS = 'two students'
   SUPERVISOR = 'supervisor'
   KIND_OF_SWIPE=( 
      (SINGLE,'single'),
      (TWO_STUDENTS,'two students'),
      (SUPERVISOR,'supervisor')
   )
   university_inventory_number=models.CharField(max_length=30,blank=True) # tax number used for depreciation
   manufacturer_serial_number = models.CharField(max_length=30,blank=True)  # here is the machine that is connected to a particular interlock   
   name = models.CharField(max_length=30)   # human readable machine description
   supervisor_list=models.ManyToManyField(Person,db_table='MachineSupervisorPersonJoinTable',related_name='supervisors') 
   user_list=models.ManyToManyField(Person,db_table='MachineUserPersonJoinTable',related_name='users') 
   lab_containing_machine = models.ForeignKey(Lab,null=True,on_delete=models.SET_NULL) # what lab is this machine in?
   kind_of_swipe_needed = models.CharField(max_length=30,choices=KIND_OF_SWIPE,default=SINGLE)   # wheather a supervisor or two swipes are needed for this machine
   start_time     = models.CharField(max_length=30)   # earliest time allowed to use this machine
   end_time   = models.CharField(max_length=30)  # latest time allowed for this machine
   minutes_enabled = models.CharField(max_length=30)  # how long access is granted for a swipe
   uses_estop = models.BooleanField()  # does this machine use an e-stop?
   def __str__(self):
        return (self.name)
  
      
class InterlockLookup(models.Model):
   id = models.AutoField(primary_key=True,null=False)
   interlock=models.OneToOneField(Interlock,on_delete=models.SET_NULL,null=True)
   machine=models.OneToOneField(Machine,on_delete=models.SET_NULL,null=True)
   def __str__(self):
        return (str(self.interlock)+" <--> "+str(self.machine.name)) 

    