from django.db import models

# Create your models here.
class Interlock(models.Model):
   interlock_mac=models.CharField(max_length=30,primary_key=True)
   manufacturing_date=models.DateField(auto_now=False, auto_now_add=False)   
   external_serial_number=models.IntegerField()
   relay_box_serial_number=models.IntegerField()
   def __str__(self):
        return (self.interlock_mac+' ,'+self.manufacturing_date+' ,'+
          self.external_serial_number+', '+self.relay_box_serial_number)
  
class Lab(models.Model):
   lab_name = models.CharField(max_length=30,primary_key=True)  # the human readable name of the lab
   lab_room = models.CharField(max_length=30) # room and building of this lab ..ex '105 SC' 
   start_time = models.CharField(max_length=30)  # lab opens at this time
   end_time = models.CharField(max_length=30)   # lab closes at this time
   def __str__(self):
        return self.lab_id+' ,'+self.start_time+' ,'+self.end_time
        
class Machine(models.Model):
   SINGLE = 'single'
   TWO_STUDENTS = 'two students'
   SUPERVISOR = 'supervisor'
   KIND_OF_SWIPE=( 
      (SINGLE,'single'),
      (TWO_STUDENTS,'two students'),
      (SUPERVISOR,'supervisor')
   )
   university_inventory_number=models.CharField(max_length=30) # tax number used for depreciation
   manufacturer_serial = models.CharField(max_length=30)  # here is the machine that is connected to a particular interlock   
   text_description = models.CharField(max_length=30)   # human readable machine description
   lab_containing_machine = models.ForeignKey(Lab,on_delete=models.SET_NULL) # what lab is this machine in?
   kind_of_swipe_needed = models.CharField(max_length=30,choices=KIND_OF_SWIPE,default=SINGLE)   # wheather a supervisor or two swipes are needed for this machine
   start_time     = models.CharField(max_length=30)   # earliest time allowed to use this machine
   end_time   = models.CharField(max_length=30)  # latest time allowed for this machine
   minutes_enabled = models.CharField(max_length=30)  # how long access is granted for a swipe
   uses_Estop = models.BooleanField()  # does this machine use an e-stop?
   def __str__(self):
        return (self.text_description)
        
      
class InterlockLookup(models.Model):
   interlock=models.OneToOneField(Interlock,on_delete=models.CASCADE,primary_key=True)
   machine=models.OneToOneField(Machine,on_delete=models.CASCADE)
   def __str__(self):
        return (self.interlock.external_serial_number+self.machine.text_description) 

class Person(models.Model):
   UNDERGRADUATE = 'undergraduate'
   GRADSTUDENT = 'two students'
   TA = 'ta'
   STAFF= 'staff'
   FACULTY= 'faculty'
   GRANTED_ALL_ACCESS= 'all access'
   KIND_OF_PERSON=( 
    (UNDERGRADUATE ,'undergraduate')
    (GRADSTUDENT,'two students')
    (TA ,'ta')
    (STAFF, 'staff')
    (FACULTY, 'faculty')
    (GRANTED_ALL_ACCESS, 'all access')
   )
   university_id = models.CharField(max_length=30,primary_key=True)  # unique university ID for this person
   person_text_name = models.CharField(max_length=80)  # name of person
   person_class = models.CharField(max_length=30,choices=KIND_OF_PERSON,default=UNDERGRADUATE)  # student, ta, faculty, staff, all-access?
   start_date = models.DateField(default=datetime.date.today())  # day the person is allowed to use all devices 
   end_date = models.DateField()  # day the person is no longer allowed to use any devices
   start_time = models.CharField(max_length=30)  # timeof day this person is allowed to use stuff
   end_time = models.CharField(max_length=30)   # timeof day this person is no longer allowed to use stuff
   def __str__(self):
        return (str(self.university_id)+' ,'+self.person_text_name+', '+
        self.person_class+' ,'+self.start_time+', '+self.end_time)

class PersonLookup(models.Model) :
   proxcard   = models.CharField(max_length=30, primary_key=True)  # the number read from a swipe
   person = models.OneToOneField(Person,on_delete=CASCADE)   # the unique identifier for a university connected individual
   def __str__(self):
        return self.university_id+' ,'+self.person_id
    
class   MachineUserPersonJoinTable(models.Model) :
   machine_id = models.ForeignKey(Machine,on_delete=models.CASCADE)  # machine in question
   person_id =  models.ForeignKey(Person,on_delete=models.CASCADE)  # this person is OK as a user for this machine
   def __str__(self):
        return str(self.machine_id)+' ,'+str(self.person_id) 
        
class   MachineSupervisorPersonJoinTable(models.Model) :
   machine_id = models.ForeignKey(Machine,on_delete=models.CASCADE)  # machine in question
   person_id = models.ForeignKey(Person,on_delete=models.CASCADE)  # this person is OK as supervisor for this machine 
   def __str__(self):
        return str(self.machine_id)+' ,'+str(self.person_id) 

    