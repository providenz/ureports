from django.contrib import admin
from search_distr.models import Person, Region, Settlement, Distribution, Month, File, ManagerAccess


admin.site.register(Person)
admin.site.register(Region)
admin.site.register(Settlement)
admin.site.register(Distribution)
admin.site.register(Month)
admin.site.register(File)
admin.site.register(ManagerAccess)