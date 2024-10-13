from django.contrib import admin
from main.models import *



admin.site.register(Project)
admin.site.register(Requirement)
admin.site.register(RequirementCheck)
admin.site.register(StoredFile)