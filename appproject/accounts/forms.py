from django import forms
from .models import Account
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import os


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


class ProfileEditForm(forms.ModelForm):
    """プロフィール編集フォーム（アイコン設定を含む）"""
    delete_avatar = forms.BooleanField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Account
        fields = ['user_name', 'email', 'age', 'avatar']
        labels = {
            'user_name': '氏名',
            'email': 'メールアドレス',
            'age': '年齢',
            'avatar': 'アバター画像',
        }
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
        }
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # ファイルサイズチェック (5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('ファイルサイズは5MB以下にしてください')
            
            # 拡張子チェック
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                raise ValidationError('画像ファイルは .jpg, .jpeg, .png, .gif のみ対応しています')
        
        return avatar
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # アバター削除フラグが立っている場合
        if self.cleaned_data.get('delete_avatar'):
            if instance.avatar:
                instance.avatar.delete(save=False)
                instance.avatar = None
        
        if commit:
            instance.save()
        return instance