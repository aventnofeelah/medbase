from django.contrib import admin
from .models import User, UserHealth, MedCenter, Disease, Visit, Surgery, Vaccination, Drugs, Test, TestFiles, Insurance, Action
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("iin", "first_name", "last_name", "role", "medcenter")
    search_fields = ['iin']
class MedCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "address", "link", "city")
    search_fields = ['name', 'type', 'address']
class UserHealthAdmin(admin.ModelAdmin):
    list_display = ("user", "sex", "blood_group", "rhesus_factor", "bad_habits", "psychoneurological_dispensary", "rehab")
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "icd_code", "type_origin", "type_localization", "type_stimulant", "type_process", "desc")
    search_fields = ['name', 'icd_code', 'desc']
class VisitAdmin(admin.ModelAdmin):
    list_display = ("user", "medcenter", "doctor", "cause", "desc", "date")
    search_fields = ['medcenter', 'doctor', 'cause', 'desc', 'date']
class SurgeryAdmin(admin.ModelAdmin):
    list_display = ("user", "disease", "name", "desc")
    search_fields = ['user', 'disease', 'name', 'desc']
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "vac_name", "desc")
    search_fields = ['user', 'name', 'vac_name']
class DrugsAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "disease")
    search_fields = ['user', 'name', 'disease']
class TestAdmin(admin.ModelAdmin):
    list_display = ("user", "medcenter", "name", "type", "desc")
    search_fields = ['medcenter', 'name', 'type']
class TestFilesAdmin(admin.ModelAdmin):
    list_display = ("test", "file")
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ("policy_number", "insurance_company", "insurance_type", "issue_date", "expiry_date", "coverage_amount")
    search_fields = ['insurance_company', 'policy_number', 'insurance_type']
class ActionAdmin(admin.ModelAdmin):
    list_display = ("user", "patient", "name", "surgery", "allergy", "disease", "vaccination", "visit", "drug", "test")
    search_fields = ['user', 'patient']
admin.site.register(User, UserAdmin)
admin.site.register(UserHealth, UserHealthAdmin)
admin.site.register(MedCenter, MedCenterAdmin)
admin.site.register(Disease, DiseaseAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Surgery, SurgeryAdmin)
admin.site.register(Vaccination, VaccinationAdmin)
admin.site.register(Drugs, DrugsAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(TestFiles, TestFilesAdmin)
admin.site.register(Insurance, InsuranceAdmin)
admin.site.register(Action, ActionAdmin)