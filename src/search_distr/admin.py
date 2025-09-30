from django.contrib import admin

from search_distr.models import Distribution, File, ManagerAccess, Month, Person, Region, Settlement

admin.site.register(Person)
admin.site.register(Region)
admin.site.register(Settlement)
admin.site.register(Distribution)
admin.site.register(Month)
admin.site.register(File)
admin.site.register(ManagerAccess)
