from django.db import models
from django.contrib.auth.models import AbstractUser
import random
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from datetime import date

# Create your models here.

MEDCENTER_TYPES = [
    # Терапевтическое направление
    ("therapy", "Терапия"),
    ("pediatrics", "Педиатрия"),
    ("family", "Семейная медицина"),
    ("geriatrics", "Гериатрия (для пожилых)"),

    # Узкие специалисты
    ("stomatology", "Стоматология"),
    ("ophthalmo", "Офтальмология (глазная клиника)"),
    ("otolaryngology", "ЛОР (Отоларингология)"),
    ("derm", "Дерматология"),
    ("allergy", "Аллергология"),
    ("endocrinology", "Эндокринология"),
    ("cardio", "Кардиология"),
    ("gastro", "Гастроэнтерология"),
    ("pulmo", "Пульмонология"),
    ("neuro", "Неврология"),
    ("psycho", "Психиатрия / Психология"),
    ("urology", "Урология"),
    ("gynecology", "Гинеколог"),
    ("andrology", "Андрология"),
    ("rheumatology", "Ревматология"),
    ("infectious", "Инфекционные заболевания"),
    ("oncology", "Онкология"),
    ("hematology", "Гематология"),
    ("nephrology", "Нефрология"),

    # Хирургическое направление
    ("surgery", "Хирургия"),
    ("trauma", "Травматология / Ортопедия"),
    ("plastic", "Пластическая хирургия"),
    ("vascular", "Сосудистая хирургия"),

    # Диагностика и реабилитация
    ("diagnostics", "Диагностика / Анализы"),
    ("radiology", "Радиология (КТ, МРТ, рентген)"),
    ("rehab", "Реабилитация / ЛФК / Физиотерапия"),
    ("sports", "Спортивная медицина"),

    # Прочие
    ("cosmetology", "Косметология"),
    ("dentistry", "Зубопротезирование / Имплантология"),
    ("pain", "Клиника боли"),
    ("emergency", "Неотложная помощь"),
    ("multidisciplinary", "Многопрофильный медцентр"),

    #Страховая компания
    ("insurance", "Страховая компания")
]
BLOOD_GROUPS = [
    ("0", "O (I)"),
    ("A", "A (II)"),
    ("B", "B (III)"),
    ("AB", "AB (IV)"),
]
RHESUS = [
    ("+", "Положительный"),
    ("-", "Отрицательный"),
]
ROLES = [
    ("doc", "Врач"),
    ("user", "Пользователь")
]
DISEASE_ORIGIN = [
    ("infection", "Инфекционное"),                  # вызвано бактериями, вирусами и т.п.
    ("hereditary", "Наследственное"),               # передаётся по генам
    ("congenital", "Врожденное"),                   # связано с аномалиями развития
    ("physiological", "Физиологическое"),           # нарушение функций организма
    ("traumatic", "Травматическое"),                # результат травм, повреждений
    ("malignant", "Злокачественное"),               # опухоли, рак
    ("deficit", "Дефицитное"),                      # нехватка витаминов/минералов
    ("autoimmune", "Аутоиммунное"),                 # сбой иммунитета (например, СКВ)
    ("endocrine", "Эндокринное"),                   # нарушения гормональной системы
    ("metabolic", "Метаболическое"),                # сбой обмена веществ (например, диабет)
    ("degenerative", "Дегенеративное"),             # возрастные изменения, разрушение тканей
    ("mental", "Психическое/Нервное"),              # депрессия, шизофрения и т.п.
    ("unknown", "Неизвестное/Идиопатическое"),      # причина не установлена
]
DISEASE_LOCALIZATION = [
    ("eye", "Глазные болезни"),
    ("ear_nose_throat", "Болезни уха, горла и носа"),
    ("skin", "Кожные болезни"),
    ("teeth_mouth", "Стоматологические болезни"),
    
    ("heart_vascular", "Болезни сердца и сосудов"),
    ("respiratory", "Болезни органов дыхания"),
    ("digestive", "Болезни органов пищеварения"),
    ("urinary", "Болезни мочевыделительной системы"),
    ("reproductive", "Болезни половой системы"),

    ("nervous", "Заболевания нервной системы"),
    ("mental", "Психические расстройства"),
    ("endocrine", "Эндокринные заболевания"),
    ("immune", "Аутоиммунные и иммунные нарушения"),
    ("musculoskeletal", "Болезни костей, суставов и мышц"),

    ("infectious_general", "Общие инфекционные болезни"),
    ("oncology", "Онкологические болезни"),
    ("blood", "Заболевания крови и кроветворных органов"),
    ("congenital", "Врожденные аномалии"),
    ("metabolic", "Нарушения обмена веществ"),
]
DISEASE_STIMULANT = [
    ("bacterial", "Бактериальные"),
    ("viral", "Вирусные"),
    ("fungal", "Грибковые"),
    ("parasitic", "Паразитарные"),

    ("toxic", "Токсические (ядовитые вещества, химия)"),
    ("radiation", "Радиация и излучение"),
    ("allergic", "Аллергические реакции"),
    ("traumatic", "Травматические факторы (физическое воздействие)"),

    ("autoimmune", "Аутоиммунные"),
    ("genetic", "Генетические мутации"),
    ("metabolic", "Метаболические нарушения"),
    ("degenerative", "Дегенеративные процессы (старение, разрушение тканей)"),
    ("neoplastic", "Опухолевые (онкологические)"),
    ("unknown", "Неизвестная причина / идиопатические"),
]
ANALYSIS_TYPES = [
    ("cbc", "Общий анализ крови (ОАК)"),
    ("biochemistry", "Биохимический анализ крови"),
    ("coagulogram", "Коагулограмма (анализ на свертываемость)"),
    ("urinalysis", "Общий анализ мочи (ОАМ)"),
    ("stool", "Копрограмма (анализ кала)"),
    ("hormones", "Гормональные исследования"),
    ("allergy", "Аллергопробы"),
    ("immunology", "Иммунологические исследования"),
    ("microbiology", "Микробиологические посевы"),
    ("pcr", "ПЦР-анализ (ДНК/РНК диагностика)"),
    ("serology", "Серологические тесты (антитела)"),
    ("oncomarkers", "Анализ на онкомаркеры"),
    ("vitamins", "Анализ на витамины и микроэлементы"),
    ("genetic", "Генетические тесты"),
    ("functional", "Функциональные тесты (глюкозотолерантный, дыхательный)"),
    ("toxicology", "Токсикологические анализы"),
    ("infectious", "Анализы на инфекции (ВИЧ, гепатиты, сифилис)"),
    ("covid", "Анализ на COVID-19"),
    ("pregnancy", "Тест на беременность (ХГЧ)"),

    ("xray", "Рентгенография"),
    ("fluorography", "Флюорография"),
    ("ct", "Компьютерная томография (КТ)"),
    ("mri", "Магнитно-резонансная томография (МРТ)"),
    ("ultrasound", "Ультразвуковое исследование (УЗИ)"),
    ("echocardiography", "Эхокардиография (ЭхоКГ)"),
    ("doppler", "Допплерография"),
    ("angiography", "Ангиография"),
    ("densitometry", "Денситометрия (плотность костей)"),

    ("ecg", "Электрокардиография (ЭКГ)"),
    ("holter", "Холтеровское мониторирование"),
    ("spirography", "Спирография"),
    ("eef", "Электроэнцефалография (ЭЭГ)"),

    ("other", "Другое"),
]
DISEASE_PROCESS = [
    ("treatment", "В процессе лечения"),
    ("cured", "Вылечена")
]
GENDER = [
    ("male", "Мужчина"),
    ("female", "Женщина")
]

class CustomUserManager(BaseUserManager):
    def create_user(self, iin, password=None, **extra_fields):
        if not iin:
            raise ValueError("Пользователь должен иметь ИИН")
        extra_fields.setdefault("is_active", True)
        user = self.model(iin=iin, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, iin, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(iin, password, **extra_fields)
    
class MedCenter(models.Model):
    name = models.CharField(max_length=100, null=False, verbose_name="Медцентр/клиника")
    type = models.CharField(max_length=100, null=False, choices=MEDCENTER_TYPES, verbose_name="Тип медцентра")
    address = models.CharField(max_length=255, null=False, verbose_name="Адрес")
    link = models.CharField(max_length=255, null=True, verbose_name="Ссылка")
    city = models.CharField(max_length=100, null=False, verbose_name="Город")

    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not MedCenter.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.get_type_display()}" 

    class Meta:
        verbose_name = "Медцентр"
        verbose_name_plural = "Медцентры"

class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=50, blank=False, verbose_name="Имя")
    last_name = models.CharField(max_length=50, blank=False, verbose_name="Фамилия")
    email = models.EmailField(unique=True, null=True, verbose_name="Почта")
    phone = models.CharField(max_length=20, null=False, unique=True, blank=False, verbose_name="Номер телефона")
    iin = models.CharField(max_length=12, unique=True, verbose_name="ИИН")
    birth = models.DateField(verbose_name="Дата рождения")
    city = models.CharField(max_length=100, null=False, verbose_name="Город")
    role = models.CharField(max_length=10, choices=ROLES, verbose_name="Тип пользователя")
    medcenter = models.ForeignKey(MedCenter, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = "iin"
    
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_age(self):
        today = date.today()
        age = today.year - self.birth.year - (
        (today.month, today.day) < (self.birth.month, self.birth.day)
        )
        return age
    
    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            self.set_password(self.password)
            
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not User.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class UserHealth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField(max_length=10, choices=GENDER, verbose_name="Пол")
    blood_group = models.CharField(max_length=50, choices=BLOOD_GROUPS, verbose_name="Группа крови")
    rhesus_factor = models.CharField(max_length=1, choices=RHESUS, verbose_name="Резус-фактор")
    bad_habits = models.TextField(max_length=500, blank=True, verbose_name="Вредные привычки")
    psychoneurological_dispensary = models.ForeignKey(MedCenter, null=True, blank=True, on_delete=models.CASCADE, related_name='pnd')
    rehab = models.ForeignKey(MedCenter, null=True, blank=True, on_delete=models.CASCADE, related_name='rehabs')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Пользователь(данные)"
        verbose_name_plural = "Пользователи(данные)"

class Disease(models.Model):
    user = models.ForeignKey(UserHealth, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Название болезни")
    medcenter = models.ForeignKey(MedCenter, on_delete=models.CASCADE)
    icd_code = models.CharField(max_length=20, blank=True, null=True, help_text="Код по МКБ-10/11", verbose_name="Код по МКБ-10/11")
    type_origin = models.CharField(max_length=100, choices=DISEASE_ORIGIN, verbose_name="Происхождение и природа")
    type_localization = models.CharField(max_length=100, choices=DISEASE_LOCALIZATION, verbose_name="Локализация болезни")
    type_stimulant = models.CharField(max_length=100, choices=DISEASE_STIMULANT, verbose_name="Возбудитель")
    type_process = models.CharField(max_length=20, choices=DISEASE_PROCESS, verbose_name="Лечение")
    desc = models.TextField(max_length=500, verbose_name="Описание")

    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not Disease.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} | {self.icd_code}"

    class Meta:
        verbose_name = "Болезнь"
        verbose_name_plural = "Болезни"

class Visit(models.Model):
    user = models.ForeignKey(UserHealth, on_delete=models.CASCADE)
    medcenter = models.ForeignKey(MedCenter, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    cause = models.CharField(max_length=255, verbose_name="Причина визита")
    desc = models.TextField(max_length=500, verbose_name="Описание")
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата посещения")

    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not Visit.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Посещение"
        verbose_name_plural = "Посещения"

class Surgery(models.Model):
    user = models.ForeignKey(UserHealth, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Название операции")
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    medcenter = models.ForeignKey(MedCenter, on_delete=models.CASCADE)
    desc = models.TextField(max_length=1000, verbose_name="Описание/Информация")
    date = models.DateTimeField(blank=False, default=timezone.now, verbose_name="Дата проведения")

    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not Surgery.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} | {self.medcenter.name}"

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"

class Vaccination(models.Model):
    user = models.ForeignKey(UserHealth, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Название вакцинации")
    medcenter = models.ForeignKey(MedCenter, on_delete=models.CASCADE)
    vac_name = models.CharField(max_length=100, verbose_name="Производитель вакцины")
    desc = models.TextField(max_length=500, verbose_name="Описание")
    date = models.DateField(blank=False, default=timezone.now, verbose_name="Дата вакцинации")

    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not Vaccination.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} | {self.vac_name}"
    
    class Meta:
        verbose_name = "Вакцинация"
        verbose_name_plural = "Вакцинации"

class Drugs(models.Model):
    user = models.ForeignKey(UserHealth, on_delete=models.CASCADE)
    medcenter = models.ForeignKey(MedCenter, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Имя препарата")
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    desc = models.TextField(max_length=500, verbose_name="Примечания")

    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not Drugs.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Препарат"
        verbose_name_plural = "Препараты"

class Test(models.Model):
    user = models.ForeignKey(UserHealth, on_delete=models.CASCADE)
    medcenter = models.ForeignKey(MedCenter, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, verbose_name="Название анализа")
    type = models.CharField(max_length=60, choices=ANALYSIS_TYPES, verbose_name="Тип анализа")
    desc = models.TextField(max_length=1000, verbose_name="Описание/Информация")

    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not Test.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Анализ"
        verbose_name_plural = "Анализы"

class TestFiles(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    file = models.FileField(upload_to='tests/', null=True, verbose_name="Файл")
    
    def file_size(self):
        size = self.file.size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 ** 2):.1f} MB"
    
    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

class Insurance(models.Model):
    user = models.OneToOneField(UserHealth, on_delete=models.CASCADE, verbose_name="Пользователь")
    
    policy_number = models.CharField(max_length=50, unique=True, verbose_name="Номер полиса")
    insurance_company = models.ForeignKey(MedCenter, on_delete=models.CASCADE)
    insurance_type = models.CharField(
        max_length=30,
        choices=[
            ("mandatory", "Обязательное медицинское страхование (ОМС)"),
            ("voluntary", "Добровольное медицинское страхование (ДМС)"),
        ],
        verbose_name="Тип страховки",
    )
    
    issue_date = models.DateField(verbose_name="Дата выдачи")
    expiry_date = models.DateField(verbose_name="Дата окончания действия")
    
    coverage_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Сумма покрытия (₸)"
    )
    conditions = models.TextField(blank=True, verbose_name="Условия страховки")
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления")

    def __str__(self):
        return f"{self.insurance_company} — {self.policy_number}"

    class Meta:
        verbose_name = "Медицинская страховка"
        verbose_name_plural = "Медицинские страховки"
    
class Action(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название действия")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_actions')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_actions')
    medcenter = models.ForeignKey(MedCenter, on_delete=models.CASCADE, related_name='medcenter_actions')
    surgery = models.ForeignKey(Surgery, null=True, blank=True, on_delete=models.SET_NULL, related_name='surgery_actions')
    allergy = models.ForeignKey(Disease, null=True, blank=True, on_delete=models.SET_NULL, related_name='allergy_actions')
    disease = models.ForeignKey(Disease, null=True, blank=True, on_delete=models.SET_NULL, related_name='disease_actions')
    vaccination = models.ForeignKey(Vaccination, null=True, blank=True, on_delete=models.SET_NULL, related_name='vaccination_actions')
    visit = models.ForeignKey(Visit, null=True, blank=True, on_delete=models.SET_NULL, related_name='visit_actions')
    drug = models.ForeignKey(Drugs, null=True, blank=True, on_delete=models.SET_NULL, related_name='drug_actions')
    test = models.ForeignKey(Test, null=True, blank=True, on_delete=models.SET_NULL, related_name='test_actions')
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления")

    #change to 100000 -> 100001
    #ALTER SEQUENCE appname_action_id_seq RESTART WITH 100000;
    #!!!
    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                nums = '1234567890'
                self.id = ''.join(random.choices(nums, k=8))
                if not Action.objects.all().filter(id=self.id).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Действие"
        verbose_name_plural = "Действия"







