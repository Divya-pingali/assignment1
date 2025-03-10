from django.contrib import admin
from .models import Professor, Module, ModuleInstance, ProfessorModuleInstance, Rating

admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(ModuleInstance)
admin.site.register(ProfessorModuleInstance)
admin.site.register(Rating)

