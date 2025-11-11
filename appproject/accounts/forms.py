from django import forms
from .models import Account
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password


class TeacherSignupForm(forms.ModelForm):
    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    password2 = forms.CharField(label='パスワード（確認）', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['user_name', 'email', 'age']
        labels = {
            'user_name': '氏名',
            'email': 'メールアドレス',
            'age': '年齢',
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
        # ハッシュ化して保存
        instance.password = make_password(self.cleaned_data.get('password1'))
        # デフォルト値を設定
        instance.account_type = 'teacher'
        if commit:
            instance.save()
        return instance


class StudentSignupForm(forms.ModelForm):
    """生徒用のサインアップフォーム。年齢をモデルへ保存する。"""
    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    password2 = forms.CharField(label='パスワード（確認）', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['user_name', 'email', 'age']
        labels = {
            'user_name': '氏名',
            'email': 'メールアドレス',
            'age': '年齢',
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
        # ハッシュ化して保存
        instance.password = make_password(self.cleaned_data.get('password1'))
        # 生徒アカウントとして設定
        instance.account_type = 'student'
        if commit:
            instance.save()
        return instance