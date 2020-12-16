import os

from django import forms
from django.utils.translation import ugettext as _



class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=255,min_length=2,required=True,widget=forms.TextInput(attrs={'placeholder':_('Username or Email'),'autocomplete':'off','class': 'form-control form-control-solid placeholder-no-fix',}))
    password = forms.CharField(max_length=255,required=True,widget=forms.PasswordInput(attrs={'placeholder':_('Password'),'autocomplete':'off','class': 'form-control form-control-solid placeholder-no-fix',}))
    remember_me = forms.BooleanField(required=False)



class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=255,min_length=2,required=True,widget=forms.PasswordInput(attrs={'placeholder':_('Old Password'),'autocomplete':'off','class': 'form-control',}))
    new_password = forms.CharField(max_length=255,min_length=8,required=True,widget=forms.PasswordInput(attrs={'placeholder':_('New Password'),'autocomplete':'off','class': 'form-control',}))
    repeat_password = forms.CharField(max_length=255,min_length=8,required=True,widget=forms.PasswordInput(attrs={'placeholder':_('Repeat Password'),'autocomplete':'off','class': 'form-control',}))
    def clean(self):
        cleaned_data = self.cleaned_data
        new_password = cleaned_data.get('new_password')
        repeat_password = cleaned_data.get('repeat_password')
        # user = kwargs.pop('user', None)
        if len(new_password) <=7:
            self._errors['new_password'] = _("Password greater than 7")
            raise forms.ValidationError(_("Password greater than 7"))
        if len(repeat_password) <=7:
            self._errors['repeat_password'] = _("Password greater than 7")
            raise forms.ValidationError(_("Password greater than 7"))
        if new_password != repeat_password:
            self._errors['repeat_password'] = _('Passwords not same')
            raise forms.ValidationError(_("Passwords not same")
            )
        return cleaned_data



# class ExcelReadForm(forms.Form):
IMPORT_FILE_TYPES = ['.xls','.xlsx', ]

class ExcelDocumentForm(forms.Form):
    excelfile = forms.FileField(label='Select a file')

def clean(self):
    data = super(ExcelDocumentForm, self).clean()

    if 'excelfile' not in data:
        raise forms.ValidationError(_('The Excel file is required to proceed'))

    excelfile = data['excelfile']
    extension = os.path.splitext(excelfile.name)[1]
    if not (extension in IMPORT_FILE_TYPES):
        raise forms.ValidationError(_("This file is not a valid Excel file. Please make sure your input file is an Excel file )"))

    return data
