from django import forms
from .models import User, Surgery, Disease, Vaccination, Visit, Drugs, Test, TestFiles
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms.widgets import FileInput

class LoginForm(forms.Form):
    iin_or_phone = forms.CharField(label='ИИН или номер телефона:')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'password'}), label='Пароль:')

    def clean(self):
        cleaned_data = super().clean()
        iin_or_phone = cleaned_data.get('iin_or_phone')
        password = cleaned_data.get('password')
        user = authenticate(username=iin_or_phone, password=password)

        if user is None:
            raise forms.ValidationError("Неверные данные для входа.")
        self.user = user
        return cleaned_data
    
class SearchUserForm(forms.Form):
    iin = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder' : 'Введите ИИН пользователя'}))

class ConfirmCodeForm(forms.Form):
    code = forms.CharField(label='Введите код от пользователя')
    
class AddSurgeryForm(forms.ModelForm):
    class Meta:
        model = Surgery
        fields = ['name', 'disease', 'desc']
        labels = {'name' : 'Название операции', 'disease' : 'Выберите болезнь', 'desc' : 'Описание'}

class AddAllergyForm(forms.ModelForm):
    class Meta:
        model = Disease
        fields = ['name', 'icd_code', 'type_origin', 'type_localization', 'type_process', 'desc']
        labels = {'name' : 'Название аллергии', 'icd_code' : 'Код по МКБ-10/11', 'type_origin' : 'Происхождение и природа', 'type_localiztion' : 'Локализация болезни', 'type_process' : 'Лечение', 'desc' : 'Описание'}

class AddDiseaseForm(forms.ModelForm):
    class Meta:
        model = Disease
        fields = ['name', 'icd_code', 'type_origin', 'type_localization', 'type_stimulant', 'type_process', 'desc']
        labels = {'name' : 'Название болезни', 'icd_code' : 'Код по МКБ-10/11', 'type_origin' : 'Происхождение и природа', 'type_localization' : 'Локализация болезни', 'type_stimulant' : 'Возбудитель', 'type_process' : 'Лечение', 'desc' : 'Описание'}

class AddVaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ['name', 'vac_name', 'desc', 'date']
        labels = {'name' : 'Название вакцинации', 'vac_name' : 'Название вакцины', 'desc' : 'Описание', 'date' : 'Дата'}
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            )
        }

class AddVisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['cause', 'desc']
        labels = {'cause' : 'Причина посещения', 'desc' : 'Описание'}

class AddDrugForm(forms.ModelForm):
    class Meta:
        model = Drugs
        fields = ['name', 'disease', 'desc']
        labels = {'name' : 'Название препарата', 'disease' : 'Болезнь', 'desc' : 'Примечания'}

class AddTestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'type', 'desc']
        labels = {'name' : 'Название анализа/исследования', 'type' : 'Тип анализа/исследования', 'desc' : 'Описание'}

class MultipleFileInput(FileInput):
    allow_multiple_selected = True

class AddTestFileForm(forms.Form):
    files = forms.FileField(
        widget=MultipleFileInput(),
        required=False,
        label='Выберите файл(-ы):'
    )
    
    def clean(self):
        cleaned_data = super().clean()

        files = self.files.getlist('files')

        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',

            'image/jpeg',
            'image/png',
            'image/webp',
            'image/tiff',

            'application/zip',
            'application/x-zip-compressed',
            'application/x-rar-compressed',
            'application/x-7z-compressed',

            'application/dicom',
            'application/dicom+json',
            'application/octet-stream',

            'application/octet-stream'
        ]

        for f in files:
            if f.content_type not in allowed_types:
                raise ValidationError(
                    f"Недопустимый файл: {f.name} ({f.content_type})"
                )

        return cleaned_data