from django import forms
from .models import Account
from django.core.exceptions import ValidationError


class TeacherSignupForm(forms.ModelForm):
    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    password2 = forms.CharField(label='パスワード（確認）', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['user_name', 'email']
        labels = {
            'user_name': '氏名',
            'email': 'メールアドレス',
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('パスワードが一致しません')
        return p2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise ValidationError('このメールアドレスは既に使用されています')
        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        # パスワードのハッシュ化はビュー側で Django の make_password を使うためここでは保留
        instance.password = self.cleaned_data.get('password1')
        # デフォルト値を設定
        instance.account_type = 'teacher'
        instance.type = '教員'
        if commit:
            instance.save()
        return instance
