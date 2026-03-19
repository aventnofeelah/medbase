from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from .forms import LoginForm, SearchUserForm
from .models import UserHealth, Surgery, Disease, Vaccination, Visit, Drugs, Test, TestFiles, Action, MedCenter
from .forms import AddSurgeryForm, ConfirmCodeForm, AddAllergyForm, AddDiseaseForm, AddVaccinationForm, AddVisitForm, AddDrugForm, AddTestFileForm, AddTestForm
from django.core.cache import cache
import os, random
from django.db.models import Q
from django.utils import timezone

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
    user = get_object_or_404(UserHealth, user=user_id)
    test = get_object_or_404(Test, user=user, id=test_id)
    tests = Test.objects.filter(user=user)

    files = TestFiles.objects.filter(test=test)
    for f in files:
        f.extension = os.path.splitext(f.file.name)[1]
    return render(request, 'overview/test.html', {'test' : test,
                                                  'tests' : tests,
                                                  'files' : files})

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
                "date": timezone.now()
            }, timeout=300)

            return redirect('confirm_surgery', user_id=user.id)
    else:
        form = AddSurgeryForm()
    return render(request, 'add/surgery_add.html', {'form' : form,
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
                surgery=surgery
            )
            cache.delete(f"surgery_code_{user_id}")
            cache.delete(f"surgery_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_surgery.html', {'form' : form,
                                                            'data' : data,
                                                            'user' : user})

def codes_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_authenticated or request.user != user:
        return redirect('home')
    return render(request, 'codes.html')

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
                "desc": form.cleaned_data['desc'],
            }, timeout=300)

            return redirect('confirm_allergy', user_id=user.id)
    else:
        form = AddAllergyForm()
    return render(request, 'add/allergy_add.html', {'form' : form,
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
            allergy = Disease.objects.create(
                user = userh,
                name = data["name"],
                icd_code = data["icd_code"],
                type_origin = data["type_origin"],
                type_localization = data["type_localization"],
                type_process = data["type_process"],
                type_stimulant = 'allergic',
                desc = data["desc"]
            )
            Action.objects.create(
                name=data["name"],
                user=request.user,
                patient=user,
                medcenter=request.user.medcenter,
                allergy=allergy
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
                "desc": form.cleaned_data['desc'],
            }, timeout=300)

            return redirect('confirm_disease', user_id=user.id)
    else:
        form = AddDiseaseForm()
    return render(request, 'add/disease_add.html', {'form' : form,
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
                disease=disease
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
                "date": form.cleaned_data['date']
            }, timeout=300)

            return redirect('confirm_vaccination', user_id=user.id)
    else:
        form = AddVaccinationForm()
    return render(request, 'add/vaccination_add.html', {'form' : form,
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
                "desc": form.cleaned_data['desc']
            }, timeout=300)

            return redirect('confirm_visit', user_id=user.id)
    else:
        form = AddVisitForm()
    return render(request, 'add/visit_add.html', {'form' : form,
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
                visit=visit
            )
            cache.delete(f"visit_code_{user_id}")
            cache.delete(f"visit_data_{user_id}")
            return redirect('profile', user_id=user.id)
    else:
        form = ConfirmCodeForm()
    return render(request, 'confirm/confirm_visit.html', {'form' : form,
                                                          'data' : data,
                                                          'user' : user})

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
                "desc" : form.cleaned_data['desc']
            }, timeout=300)

            return redirect('confirm_drug', user_id=user.id)
    else:
        form = AddDrugForm()
    return render(request, 'add/drug_add.html', {'form' : form,
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
                drug=drug
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

def test_add_view(request, user_id):
    if not request.user.is_authenticated or request.user.role != 'doc':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AddTestForm(request.POST)
        form_file = AddTestFileForm(request.POST, request.FILES)
        if form.is_valid() and form_file.is_valid():
            code = str(random.randint(100000, 999999))
            cache.set(f"test_code_{user.id}", code, timeout=300)
            cache.set(f"test_data_{user_id}", {
                "name": form.cleaned_data['name'],
                "type": form.cleaned_data['type'],
                "desc" : form.cleaned_data['desc'],

                "files": form_file.cleaned_data['files'],
            }, timeout=300)

            return redirect('confirm_test', user_id=user.id)
    else:
        form = AddTestForm()
        form_file = AddTestFileForm()
    return render(request, 'add/test_add.html', {'form' : form,
                                                 'form_file' : form_file,
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
            test = Test.objects.create(
                user = userh,
                name = data["name"],
                medcenter=request.user.medcenter,
                type  = data["type"],
                desc = data["desc"]
            )
            files = data['files']
            for f in files:
                TestFiles.objects.create(
                    test=test,
                    file=f
                )
            Action.objects.create(
                name=data["name"],
                user=request.user,
                patient=user,
                medcenter=request.user.medcenter,
                test=test
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
    return render(request, 'codes/test_code.html', {'code' : code,
                                                    'data' : data})

def medcenter_view(request, medcenter_id):
    medcenter = get_object_or_404(MedCenter, id=medcenter_id)
    return render(request, 'overview/medcenter.html', {'medcenter' : medcenter,
                                                       'name' : medcenter.name})

def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')
