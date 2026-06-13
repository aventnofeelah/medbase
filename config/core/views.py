import os, random

from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File
from django.views.decorators.http import require_POST

from .forms import (LoginForm, 
                    SearchUserForm, 
                    EditSurgeryForm, 
                    EditDiseaseForm, 
                    EditVaccinationForm, 
                    EditVisitForm,
                    EditAllergyForm,
                    EditTestForm,)

from .models import (UserHealth, 
                     Surgery, 
                     Disease, 
                     Vaccination, 
                     Visit, 
                     Drugs, 
                     Test, 
                     TestFiles, 
                     Action, 
                     MedCenter)

from .forms import (AddSurgeryForm, 
                    ConfirmCodeForm, 
                    AddAllergyForm, 
                    AddDiseaseForm, 
                    AddVaccinationForm, 
                    AddVisitForm, 
                    AddDrugForm, 
                    AddTestFileForm, 
                    AddTestForm,
                    EditDrugForm)

# Create your views here.s

User = get_user_model()

def home_view(request):
    form = SearchUserForm(request.GET or None)
    found = None
    if form.is_valid():
        query_text = form.cleaned_data["iin"]
        user = User.objects.filter(iin=query_text).first()
        if user:
            return redirect('profile', user_id=user.id)
        else:
            found = False
    else:
        query_text = ''
    actions = None
    if request.user.is_authenticated:
        actions = Action.objects.filter(
            Q(user=request.user) | Q(patient=request.user)
        ).order_by('-created_at')
    doc_count = User.objects.filter(role='doc').count()
    user_count = User.objects.filter(role='user').count()
    med_count = MedCenter.objects.count()
    rec_count = Disease.objects.count() + Visit.objects.count() + Surgery.objects.count() + Vaccination.objects.count() + Drugs.objects.count() + Test.objects.count()
    return render(request, 'home.html', {'form' : form,
                                         'found' : found,
                                         'actions' : actions,
                                         "doc_count": doc_count,
                                         "user_count": user_count,
                                         "med_count": med_count,
                                         'rec_count' : rec_count})
                                         

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form' : form})

def logout_view(request):
    logout(request)
    return redirect('home')

def profile_view(request, user_id):
    if (not request.user.is_authenticated or request.user.role != 'doc') and request.user.id != user_id:
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    surgeries = Surgery.objects.all().filter(user=userh)
    allergies = Disease.objects.all().filter(user=userh, type_stimulant='allergic')
    diseases = Disease.objects.all().filter(user=userh).exclude(type_stimulant='allergic')
    vaccinations = Vaccination.objects.all().filter(user=userh)
    visits = Visit.objects.all().filter(user=userh)
    drugs = Drugs.objects.all().filter(user=userh)
    tests = Test.objects.all().filter(user=userh)
    insurance = getattr(userh, "insurance", None)
    return render(request, 'profile.html', {'user' : user,
                                            'userh' : userh,
                                            'surgeries' : surgeries,
                                            'allergies' : allergies,
                                            'diseases' : diseases,
                                            'vaccinations' : vaccinations,
                                            'visits' : visits,
                                            'drugs' : drugs,
                                            'tests' : tests,
                                            'insurance' : insurance})

def medcenter_view(request, medcenter_id):
    medcenter = get_object_or_404(MedCenter, id=medcenter_id)
    return render(request, 'overview/medcenter.html', {'medcenter' : medcenter,
                                                       'name' : medcenter.name})

def surgery_view(request, user_id, surgery_id):
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    surgery = get_object_or_404(Surgery, user=userh, id=surgery_id)
    surgeries = Surgery.objects.filter(user=userh)
    return render(request, 'overview/surgery.html', {'surgery' : surgery,
                                                     'surgeries' : surgeries,
                                                     'user' : user})

def allergy_view(request, user_id, allergy_id):
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    allergy = get_object_or_404(Disease, user=userh, id=allergy_id)
    drugs = Drugs.objects.filter(disease=allergy)
    allergies = Disease.objects.filter(user=userh, type_stimulant='allergic')
    return render(request, 'overview/allergy.html', {'allergy' : allergy,
                                                     'drugs' : drugs,
                                                     'allergies' : allergies,
                                                     'user' : user})

def disease_view(request, user_id, disease_id):
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    disease = get_object_or_404(Disease, user=userh, id=disease_id)
    drugs = Drugs.objects.filter(disease=disease)
    diseases = Disease.objects.filter(user=userh).exclude(type_stimulant='allergic')
    return render(request, 'overview/disease.html', {'disease' : disease,
                                                     'drugs' : drugs,
                                                     'diseases' : diseases,
                                                     'user' : user})

def vaccination_view(request, user_id, vaccination_id):
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    vaccination = get_object_or_404(Vaccination, user=userh, id=vaccination_id)
    vaccinations = Vaccination.objects.filter(user=userh)
    return render(request, 'overview/vaccination.html', {'vaccination' : vaccination,
                                                         'vaccinations' : vaccinations,
                                                         'user' : user})

def visit_view(request, user_id, visit_id):
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    visit = get_object_or_404(Visit, user=userh, id=visit_id)
    visits = Visit.objects.filter(user=userh)
    return render(request, 'overview/visit.html', {'visit' : visit,
                                                   'visits' : visits,
                                                   'user' : user})

def drug_view(request, user_id, drug_id):
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    drug = get_object_or_404(Drugs, user=userh, id=drug_id)
    drugs = Drugs.objects.filter(user=userh)

    diseases = Disease.objects.filter(user=userh)
    diseases_list = []
    for x in diseases:
        if drug.disease.name == x.name:
            diseases_list.append(x)
    return render(request, 'overview/drug.html', {'drug' : drug,
                                                  'drugs' : drugs,
                                                  'diseases_list' : diseases_list,
                                                  'user' : user})

def test_view(request, user_id, test_id):
    user = get_object_or_404(User, id=user_id)
    userh = get_object_or_404(UserHealth, user=user)
    test = get_object_or_404(Test, user=userh, id=test_id)
    tests = Test.objects.filter(user=userh)

    files = TestFiles.objects.filter(test=test)
    if files:
        for f in files:
            f.extension = os.path.splitext(f.file.name)[1]
    if request.method == "POST":
        form = AddTestFileForm(request.POST, request.FILES)
        if form.is_valid():
            form_files = form.cleaned_data.get('files') or []
            log_messages = []
            for f in form_files:
                log_messages.append(f"Добавление файла: {f.name}")
                instance = TestFiles(test=test, file=f)
                instance.save()
                final_string = "; ".join(log_messages) + "."
                Action.objects.create(
                    name="Добавление файла(-ов)",
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    test=test,
                    files=final_string
                )

            return HttpResponseRedirect(request.path)
    else:
        form = AddTestFileForm()
    return render(request, 'overview/test.html', {'test' : test,
                                                  'tests' : tests,
                                                  'files' : files,
                                                  'user' : user,
                                                  'form': form})

@require_POST
def delete_file_view(request, file_id):
    file_obj = get_object_or_404(TestFiles, id=file_id)
    
    filename = file_obj.filename
    test = file_obj.test
    patient = test.user.user
    
    if file_obj.file:
        file_obj.file.delete(save=False)
    
    file_obj.delete()
    
    Action.objects.create(
        name="Удаление файла",
        user=request.user,
        patient=patient,
        medcenter=request.user.medcenter,
        test=test,
        files=f"Удален файл: {filename}."
    )
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

def codes_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    return render(request, 'codes.html')

#ADD/EDIT SURGERY
def surgery_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddSurgeryForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"surgery_code_{user.id}", code, timeout=300)
            cache.set(f"surgery_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "disease": form.cleaned_data['disease'],
                "medcenter": request.user.medcenter,
                "desc": form.cleaned_data['desc'],
                "ac_type": "add",
                "date": timezone.now()
            }, timeout=300)

            return redirect('confirm_surgery', user_id=user.id)
    else:
        form = AddSurgeryForm()
    return render(request, 'add/surgery_add.html', {'form' : form,
                                                    'user' : user})
def surgery_edit_view(request, user_id, surgery_id):
    surgery = get_object_or_404(Surgery, id=surgery_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = EditSurgeryForm(request.POST, instance=surgery)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"surgery_code_{user.id}", code, timeout=300)
            cache.set(f"surgery_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "disease": form.cleaned_data['disease'],
                "medcenter": request.user.medcenter,
                "desc": form.cleaned_data['desc'],
                "ac_type": "edit",
                "surgery_id": surgery.id,
                "date": timezone.now()
            }, timeout=300)
            return redirect('confirm_surgery', user_id=user.id)
    else:
        form = EditSurgeryForm(instance=surgery)
    
    return render(request, 'edit/surgery_edit.html', {'form' : form,
                                                      'user' : user})

def confirm_surgery_view(request, user_id):
    if not request.user.medcenter or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    data = cache.get(f"surgery_data_{user_id}")
    if not data:    
        error = "Нет данных для подтверждения"
        form = ConfirmCodeForm()
        return render(request, 'confirm/confirm_surgery.html', {'form' : form,
                                                                'data' : data,
                                                                'user' : user,
                                                                'error' : error})
    if request.method == "POST":
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f"surgery_code_{user_id}")

            if not cached_code:
                error = "Код не найден или истек"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_surgery.html', {'form' : form,
                                                                        'data' : data,
                                                                        'user' : user,
                                                                        'error' : error})
            if cached_code != code:
                error = "Неверный код"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_surgery.html', {'form' : form,
                                                                        'data' : data,
                                                                        'user' : user,
                                                                        'error' : error})
            userh = get_object_or_404(UserHealth, user=user)
            if data["ac_type"] == "add":
                surgery = Surgery.objects.create(
                    user=userh,
                    name=data["name"],
                    disease=data["disease"],
                    desc=data["desc"],
                    medcenter=request.user.medcenter
                )
                Action.objects.create(
                    user=request.user,
                    name=data["name"],
                    patient=user,
                    medcenter=request.user.medcenter,
                    surgery=surgery,
                    ac_type=data["ac_type"]
                )
            else:
                surgery = Surgery.objects.get(id=data["surgery_id"])
                surgery.name = data["name"]
                surgery.disease = data["disease"]
                surgery.desc = data["desc"]
                surgery.save()

                Action.objects.create(
                    user=request.user,
                    name=data["name"],
                    patient=user,
                    medcenter=request.user.medcenter,
                    surgery=surgery,
                    ac_type=data["ac_type"]
                )
            cache.delete(f"surgery_code_{user_id}")
            cache.delete(f"surgery_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_surgery.html', {'form' : form,
                                                            'data' : data,
                                                            'user' : user})

def surgery_code_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    code = cache.get(f"surgery_code_{user_id}")
    data = cache.get(f"surgery_data_{user_id}")
    return render(request, 'codes/surgery_code.html', {'code' : code,
                                                       'data' : data})

def action_view(request, user_id, action_id):
    user = get_object_or_404(User, id=user_id)
    action = get_object_or_404(Action, id=action_id)
    actions = Action.objects.filter(
            Q(user=user) | Q(patient=user)
        ).order_by('-created_at')
    return render(request, 'overview/action.html', {'user' : user,
                                                    'action' : action,
                                                    'actions' : actions})

#ALLERGY ADD/EDIT
def allergy_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddAllergyForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"allergy_code_{user.id}", code, timeout=300)
            cache.set(f"allergy_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "icd_code": form.cleaned_data['icd_code'],
                "type_origin": form.cleaned_data['type_origin'],
                "type_localization": form.cleaned_data['type_localization'],
                "type_process": form.cleaned_data['type_process'],
                "medcenter": request.user.medcenter,
                "ac_type": "add",
                "desc": form.cleaned_data['desc'],
                "date": timezone.now()
            }, timeout=300)

            return redirect('confirm_allergy', user_id=user.id)
    else:
        form = AddAllergyForm()
    return render(request, 'add/allergy_add.html', {'form' : form,
                                                    'user' : user})

def allergy_edit_view(request, user_id, allergy_id):
    allergy = get_object_or_404(Disease, id=allergy_id, type_stimulant="allergic")
    print(allergy)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = EditAllergyForm(request.POST, instance=allergy)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"allergy_code_{user.id}", code, timeout=300)
            cache.set(f"allergy_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "icd_code": form.cleaned_data['icd_code'],
                "type_origin": form.cleaned_data['type_origin'],
                "type_localization": form.cleaned_data['type_localization'],
                "type_process": form.cleaned_data['type_process'],
                "medcenter": request.user.medcenter,
                "desc": form.cleaned_data['desc'],
                "ac_type": "edit",
                "allergy_id": allergy.id,
                "date": timezone.now()
            }, timeout=300)
            return redirect('confirm_allergy', user_id=user.id)
    else:
        form = EditAllergyForm(instance=allergy)
    
    return render(request, 'edit/allergy_edit.html', {'form' : form,
                                                      'user' : user})

def confirm_allergy_view(request, user_id):
    if not request.user.medcenter or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    data = cache.get(f"allergy_data_{user_id}")
    if not data:    
        error = "Нет данных для подтверждения"
        form = ConfirmCodeForm()
        return render(request, 'confirm/confirm_allergy.html', {'form' : form,
                                                                'data' : data,
                                                                'error' : error,
                                                                'user' : user})
    if request.method == "POST":
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f"allergy_code_{user_id}")

            if not cached_code:
                error = "Код не найден или истек"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_allergy.html', {'form' : form,
                                                                        'data' : data,
                                                                        'user' : user,
                                                                        'error' : error})
            if cached_code != code:
                error = "Неверный код"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_allergy.html', {'form' : form,
                                                                        'data' : data,
                                                                        'user' : user,
                                                                        'error' : error})
            
            userh = get_object_or_404(UserHealth, user=user)
            if data["ac_type"] == "add":
                allergy = Disease.objects.create(
                    user = userh,
                    name = data["name"],
                    icd_code = data["icd_code"],
                    type_origin = data["type_origin"],
                    type_localization = data["type_localization"],
                    type_process = data["type_process"],
                    type_stimulant = 'allergic',
                    desc = data["desc"],
                )
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    allergy=allergy,
                    ac_type="add"
                )
            else:
                allergy = Disease.objects.get(id=data["allergy_id"])
                allergy.name = data["name"]
                allergy.icd_code = data["icd_code"]
                allergy.type_localization = data["type_localization"]
                allergy.type_origin = data["type_origin"]
                allergy.type_process = data["type_process"]
                allergy.desc = data["desc"]
                allergy.save() 
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    allergy=allergy,
                    ac_type="edit"
                )
            cache.delete(f"allergy_code_{user_id}")
            cache.delete(f"allergy_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_allergy.html', {'form' : form,
                                                            'data' : data,
                                                            'user' : user})

def allergy_code_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    code = cache.get(f"allergy_code_{user_id}")
    data = cache.get(f"allergy_data_{user_id}")
    return render(request, 'codes/allergy_code.html', {'code' : code,
                                                       'data' : data})
#ADD/EDIT DISEASE
def disease_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddDiseaseForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"disease_code_{user.id}", code, timeout=300)
            cache.set(f"disease_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "icd_code": form.cleaned_data['icd_code'],
                "type_origin": form.cleaned_data['type_origin'],
                "type_localization": form.cleaned_data['type_localization'],
                "type_process": form.cleaned_data['type_process'],
                "type_stimulant": form.cleaned_data['type_stimulant'],
                "medcenter": request.user.medcenter,
                "ac_type": "add",
                "desc": form.cleaned_data['desc'],
            }, timeout=300)

            return redirect('confirm_disease', user_id=user.id)
    else:
        form = AddDiseaseForm()
    return render(request, 'add/disease_add.html', {'form' : form,
                                                    'user' : user})
def disease_edit_view(request, user_id, disease_id):
    disease = get_object_or_404(Disease, id=disease_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = EditDiseaseForm(request.POST, instance=disease)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"disease_code_{user.id}", code, timeout=300)
            cache.set(f"disease_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "icd_code": form.cleaned_data['icd_code'],
                "type_origin": form.cleaned_data['type_origin'],
                "type_localization": form.cleaned_data['type_localization'],
                "type_process": form.cleaned_data['type_process'],
                "type_stimulant": form.cleaned_data['type_stimulant'],
                "medcenter": request.user.medcenter,
                "desc": form.cleaned_data['desc'],
                "ac_type": "edit",
                "disease_id": disease.id,
                "date": timezone.now()
            }, timeout=300)
            return redirect('confirm_disease', user_id=user.id)
    else:
        form = EditDiseaseForm(instance=disease)
    
    return render(request, 'edit/disease_edit.html', {'form' : form,
                                                      'user' : user})

def confirm_disease_view(request, user_id):
    if not request.user.medcenter or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    data = cache.get(f"disease_data_{user_id}")
    if not data:    
        error = "Нет данных для подтверждения"
        form = ConfirmCodeForm()
        return render(request, 'confirm/confirm_disease.html', {'form' : form,
                                                                'data' : data,
                                                                'error' : error,
                                                                'user' : user})
    if request.method == "POST":
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f"disease_code_{user_id}")

            if not cached_code:
                error = "Код не найден или истек"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_disease.html', {'form' : form,
                                                                        'data' : data,
                                                                        'user' : user,
                                                                        'error' : error})
            if cached_code != code:
                error = "Неверный код"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_disease.html', {'form' : form,
                                                                        'data' : data,
                                                                        'user' : user,
                                                                        'error' : error})
            
            userh = get_object_or_404(UserHealth, user=user)
            if data["ac_type"] == "add":
                disease = Disease.objects.create(
                    user = userh,
                    name = data["name"],
                    icd_code = data["icd_code"],
                    type_origin = data["type_origin"],
                    type_localization = data["type_localization"],
                    type_process = data["type_process"],
                    type_stimulant = data['type_stimulant'],
                    desc = data["desc"]
                )
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    disease=disease,
                    ac_type=data["ac_type"]
                )
            else:
                disease = Disease.objects.get(id=data["disease_id"])
                disease.name = data["name"]
                disease.icd_code = data["icd_code"]
                disease.type_localization = data["type_localization"]
                disease.type_origin = data["type_origin"]
                disease.type_stimulant = data["type_stimulant"]
                disease.type_process = data["type_process"]
                disease.desc = data["desc"]
                disease.save()

                Action.objects.create(
                    user=request.user,
                    name=data["name"],
                    patient=user,
                    medcenter=request.user.medcenter,
                    disease=disease,
                    ac_type=data["ac_type"]
                )
            cache.delete(f"disease_code_{user_id}")
            cache.delete(f"disease_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_disease.html', {'form' : form,
                                                            'data' : data,
                                                            'user' : user})

def disease_code_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    code = cache.get(f"disease_code_{user_id}")
    data = cache.get(f"disease_data_{user_id}")
    return render(request, 'codes/disease_code.html', {'code' : code,
                                                       'data' : data})

#ADD/EDIT VACCINATION
def vaccination_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddVaccinationForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"vaccination_code_{user.id}", code, timeout=300)
            cache.set(f"vaccination_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "vac_name": form.cleaned_data['vac_name'],
                "desc": form.cleaned_data['desc'],
                "date": form.cleaned_data['date'],
                "ac_type": "add"
            }, timeout=300)

            return redirect('confirm_vaccination', user_id=user.id)
    else:
        form = AddVaccinationForm()
    return render(request, 'add/vaccination_add.html', {'form' : form,
                                                        'user' : user})

def vaccination_edit_view(request, user_id, vaccination_id):
    vaccination = get_object_or_404(Vaccination, id=vaccination_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = EditVaccinationForm(request.POST, instance=vaccination)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"vaccination_code_{user.id}", code, timeout=300)
            cache.set(f"vaccination_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "vac_name": form.cleaned_data['vac_name'],
                "medcenter": request.user.medcenter,
                "desc": form.cleaned_data['desc'],
                "ac_type": "edit",
                "vaccination_id": vaccination.id,
                "date": timezone.now()
            }, timeout=300)
            return redirect('confirm_vaccination', user_id=user.id)
    else:
        form = EditVaccinationForm(instance=vaccination)
    
    return render(request, 'edit/vaccination_edit.html', {'form' : form,
                                                          'user' : user})

def confirm_vaccination_view(request, user_id):
    if not request.user.medcenter or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    data = cache.get(f"vaccination_data_{user_id}")
    if not data:    
        error = "Нет данных для подтверждения"
        form = ConfirmCodeForm()
        return render(request, 'confirm/confirm_vaccination.html', {'form' : form,
                                                                    'data' : data,
                                                                    'error' : error,
                                                                    'user' : user})
    if request.method == "POST":
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f"vaccination_code_{user_id}")

            if not cached_code:
                error = "Код не найден или истек"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_vaccination.html', {'form' : form,
                                                                            'data' : data,
                                                                            'user' : user,
                                                                            'error' : error})
            if cached_code != code:
                error = "Неверный код"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_vaccination.html', {'form' : form,
                                                                            'data' : data,
                                                                            'user' : user,
                                                                            'error' : error})
            userh = get_object_or_404(UserHealth, user=user)
            if data["ac_type"] == "add":
                vaccination = Vaccination.objects.create(
                    user = userh,
                    name = data["name"],
                    vac_name = data["vac_name"],
                    medcenter=request.user.medcenter,
                    desc = data["desc"],
                    date = data["date"]
                )
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    ac_type=data["ac_type"],
                    vaccination=vaccination
                )
            else:
                vaccination = Vaccination.objects.get(id=data["vaccination_id"])
                vaccination.name = data["name"]
                vaccination.vac_name = data["vac_name"]
                vaccination.desc = data["desc"]
                vaccination.save()
                
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    ac_type=data["ac_type"],
                    vaccination=vaccination
                )
            cache.delete(f"vaccination_code_{user_id}")
            cache.delete(f"vaccination_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_vaccination.html', {'form' : form,
                                                                'data' : data,
                                                                'user' : user})

def vaccination_code_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    code = cache.get(f"vaccination_code_{user_id}")
    data = cache.get(f"vaccination_data_{user_id}")
    return render(request, 'codes/vaccination_code.html', {'code' : code,
                                                           'data' : data})

#ADD/EDIT VISIT
def visit_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddVisitForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"visit_code_{user.id}", code, timeout=300)
            cache.set(f"visit_data_{user_id}", {
                "cause": form.cleaned_data['cause'],
                "desc": form.cleaned_data['desc'],
                "ac_type": "add"
            }, timeout=300)

            return redirect('confirm_visit', user_id=user.id)
    else:
        form = AddVisitForm()
    return render(request, 'add/visit_add.html', {'form' : form,
                                                  'user' : user})

def visit_edit_view(request, user_id, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = EditVisitForm(request.POST, instance=visit)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"visit_code_{user.id}", code, timeout=300)
            cache.set(f"visit_data_{user_id}", {
                "cause": form.cleaned_data['cause'],
                "desc": form.cleaned_data['desc'],
                "medcenter": request.user.medcenter,
                "ac_type": "edit",
                "visit_id": visit.id,
                "date": timezone.now()
            }, timeout=300)
            return redirect('confirm_visit', user_id=user.id)
    else:
        form = EditVisitForm(instance=visit)
    
    return render(request, 'edit/visit_edit.html', {'form' : form,
                                                    'user' : user})

def confirm_visit_view(request, user_id):
    if not request.user.medcenter or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    data = cache.get(f"visit_data_{user_id}")
    if not data:    
        error = "Нет данных для подтверждения"
        form = ConfirmCodeForm()
        return render(request, 'confirm/confirm_visit.html', {'form' : form,
                                                              'data' : data,
                                                              'error' : error,
                                                              'user' : user})
    if request.method == "POST":
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f"visit_code_{user_id}")

            if not cached_code:
                error = "Код не найден или истек"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_visit.html', {'form' : form,
                                                                      'data' : data,
                                                                      'user' : user,
                                                                      'error' : error})
            if cached_code != code:
                error = "Неверный код"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_visit.html', {'form' : form,
                                                                      'data' : data,
                                                                      'user' : user,
                                                                      'error' : error})
            
            userh = get_object_or_404(UserHealth, user=user)
            if data["ac_type"] == "add":
                visit = Visit.objects.create(
                    user = userh,
                    medcenter=request.user.medcenter,
                    doctor = request.user,
                    desc = data["desc"],
                    cause = data["cause"]
                )
                Action.objects.create(
                    name=data["cause"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    visit=visit,
                    ac_type=data["ac_type"]
                )
            else:
                visit = Visit.objects.get(id=data["visit_id"])
                visit.cause = data["cause"]
                visit.desc = data["desc"]
                visit.save()
                
                Action.objects.create(
                    name=data["cause"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    visit=visit,
                    ac_type=data["ac_type"]
                )
            cache.delete(f"visit_code_{user_id}")
            cache.delete(f"visit_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_visit.html', {'form' : form,
                                                          'data' : data,
                                                          'user' : user})
#ADD/EDIT DRUG
def visit_code_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    code = cache.get(f"visit_code_{user_id}")
    data = cache.get(f"visit_data_{user_id}")
    return render(request, 'codes/visit_code.html', {'code' : code,
                                                     'data' : data})

def drug_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddDrugForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"drug_code_{user.id}", code, timeout=300)
            cache.set(f"drug_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "disease": form.cleaned_data['disease'],
                "ac_type": "add",
                "desc" : form.cleaned_data['desc']
            }, timeout=300)

            return redirect('confirm_drug', user_id=user.id)
    else:
        form = AddDrugForm()
    return render(request, 'add/drug_add.html', {'form' : form,
                                                 'user' : user})

def drug_edit_view(request, user_id, drug_id):
    drug = get_object_or_404(Drugs, id=drug_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        form = EditDrugForm(request.POST, instance=drug)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"drug_code_{user.id}", code, timeout=300)
            cache.set(f"drug_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "disease": form.cleaned_data['disease'],
                "desc": form.cleaned_data['desc'],
                "medcenter": request.user.medcenter,
                "ac_type": "edit",
                "drug_id": drug.id,
                "date": timezone.now()
            }, timeout=300)
            return redirect('confirm_drug', user_id=user.id)
    else:
        form = EditDrugForm(instance=drug)
    return render(request, 'edit/drug_edit.html', {'form' : form,
                                                   'user' : user})

def confirm_drug_view(request, user_id):
    if not request.user.medcenter or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    data = cache.get(f"drug_data_{user_id}")
    if not data:    
        error = "Нет данных для подтверждения"
        form = ConfirmCodeForm()
        return render(request, 'confirm/confirm_drug.html', {'form' : form,
                                                             'data' : data,
                                                             'error' : error,
                                                             'user' : user})
    if request.method == "POST":
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f"drug_code_{user_id}")

            if not cached_code:
                error = "Код не найден или истек"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_drug.html', {'form' : form,
                                                                     'data' : data,
                                                                     'user' : user,
                                                                     'error' : error})
            if cached_code != code:
                error = "Неверный код"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_drug.html', {'form' : form,
                                                                     'data' : data,
                                                                     'user' : user,
                                                                     'error' : error})
            
            userh = get_object_or_404(UserHealth, user=user)
            if data["ac_type"] == "add":
                drug = Drugs.objects.create(
                    user = userh,
                    name = data["name"],
                    disease  = data["disease"],
                    desc = data["desc"]
                )
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    drug=drug,
                    ac_type=data["ac_type"]
                )
            else:
                drug = Drugs.objects.get(id=data["drug_id"])
                drug.name = data["name"]
                drug.disease = data["disease"]
                drug.desc = data["desc"]
                drug.save()
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    drug=drug,
                    ac_type=data["ac_type"]
                )
            cache.delete(f"drug_code_{user_id}")
            cache.delete(f"drug_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_drug.html', {'form' : form,
                                                         'data' : data,
                                                         'user' : user})

def drug_code_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    code = cache.get(f"drug_code_{user_id}")
    data = cache.get(f"drug_data_{user_id}")
    return render(request, 'codes/drug_code.html', {'code' : code,
                                                    'data' : data})

#ADD/EDIT TEST
def test_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddTestForm(request.POST)
        form_file = AddTestFileForm(request.POST, request.FILES)
        if form.is_valid() and form_file.is_valid():
            files_list = form_file.cleaned_data['files']
            saved_paths = []
            for f in files_list:
                filename = f"tmp/{user_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}_{f.name}"
                path = default_storage.save(filename, ContentFile(f.read()))
                saved_paths.append(path)

            code = str(random.randint(100000, 999999))
            cache.set(f"test_code_{user.id}", code, timeout=300)
            cache.set(f"test_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "type": form.cleaned_data['type'],
                "medcenter": request.user.medcenter,
                "desc" : form.cleaned_data['desc'],
                "ac_type": "add",
                "date": timezone.now(),
                "file_paths": saved_paths
            }, timeout=300)

            return redirect('confirm_test', user_id=user.id)
    else:
        form = AddTestForm()
        form_file = AddTestFileForm()
    return render(request, 'add/test_add.html', {'form' : form,
                                                 'form_file' : form_file,
                                                 'user' : user})

def test_edit_view(request, user_id, test_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    
    test = get_object_or_404(Test, id=test_id)
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = EditTestForm(request.POST, instance=test)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"test_code_{user.id}", code, timeout=300)
            cache.set(f"test_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "type": form.cleaned_data['type'],
                "desc" : form.cleaned_data['desc'],
                "medcenter": request.user.medcenter,
                "ac_type": "edit",
                "test_id": test.id,
                "date": timezone.now()
            }, timeout=300)
            return redirect('confirm_test', user_id=user.id)
    else:
        form = EditTestForm(instance=test)
    return render(request, 'edit/test_edit.html', {'form' : form,
                                                   'user' : user})

def confirm_test_view(request, user_id):
    if not request.user.medcenter or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    data = cache.get(f"test_data_{user_id}")
    if not data:    
        error = "Нет данных для подтверждения"
        form = ConfirmCodeForm()
        return render(request, 'confirm/confirm_test.html', {'form' : form,
                                                             'data' : data,
                                                             'error' : error,
                                                             'user' : user})
    if request.method == "POST":
        form = ConfirmCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f"test_code_{user_id}")

            if not cached_code:
                error = "Код не найден или истек"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_test.html', {'form' : form,
                                                                     'data' : data,
                                                                     'user' : user,
                                                                     'error' : error})
            if cached_code != code:
                error = "Неверный код"
                form = ConfirmCodeForm()
                return render(request, 'confirm/confirm_test.html', {'form' : form,
                                                                     'data' : data,
                                                                     'user' : user,
                                                                     'error' : error})
            
            userh = get_object_or_404(UserHealth, user=user)
            if data["ac_type"] == "add":
                test = Test.objects.create(
                    user = userh,
                    name = data["name"],
                    medcenter=request.user.medcenter,
                    type  = data["type"],
                    desc = data["desc"]
                )
                file_paths = data.get("file_paths", [])
                #async with huey
                for path in file_paths:
                    if default_storage.exists(path):
                        with default_storage.open(path) as f:
                            clean_name = os.path.basename(path)
                            TestFiles.objects.create(
                                test=test,
                                file=File(f, name=clean_name)
                            )
                        default_storage.delete(path)
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    test=test,
                    ac_type=data["ac_type"]
                )
            else:
                test = Test.objects.get(id=data["test_id"])
                test.name = data["name"]
                test.type = data["type"]
                test.desc = data["desc"]
                test.save()
                Action.objects.create(
                    name=data["name"],
                    user=request.user,
                    patient=user,
                    medcenter=request.user.medcenter,
                    test=test,
                    ac_type=data["ac_type"]
                )
            cache.delete(f"test_code_{user_id}")
            cache.delete(f"test_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_test.html', {'form' : form,
                                                         'data' : data,
                                                         'user' : user})

def test_code_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    code = cache.get(f"test_code_{user_id}")
    data = cache.get(f"test_data_{user_id}")
    print("CODE", code)
    print("DATA:", data)
    return render(request, 'codes/test_code.html', {'code' : code,
                                                    'data' : data})

#Privacy policy, FAQ, support
def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')
