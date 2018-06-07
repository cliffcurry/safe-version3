from django.contrib import admin

# Register your models here.

from  .models import (Interlock,   Lab,    
    Machine,InterlockLookup,
     Person
)

class MachineAdmin(admin.ModelAdmin):
    list_display=("name",)
    filter_horizontal = ('user_list','supervisor_list')

class InterlockLookupAdmin(admin.ModelAdmin):
    list_display=("interlock",'machine')
    

admin.site.register(Interlock)
admin.site.register(InterlockLookup,InterlockLookupAdmin)
admin.site.register(Lab)
admin.site.register(Machine,MachineAdmin)
admin.site.register(Person)



