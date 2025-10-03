from django.db import models
from accounts.models import Account


class System(models.Model):
    # system_id は PostgreSQL のシーケンスで管理（4000001 から開始）
    system_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='ユーザーID')
    system_name = models.CharField(max_length=100, verbose_name='システム名')
    system_description = models.TextField(blank=True, null=True, verbose_name='システム種類')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'system'
        verbose_name = 'システム'
        verbose_name_plural = 'システム'

    def __str__(self):
        return f"{self.system_name} (ID: {self.system_id})"


class Algorithm(models.Model):
    # algorithm_id は PostgreSQL のシーケンスで管理（5000001 から開始）
    algorithm_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='ユーザーID')
    algorithm_name = models.CharField(max_length=100, verbose_name='アルゴリズム名')
    algorithm_description = models.TextField(blank=True, null=True, verbose_name='アルゴリズム概要')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'algorithm'
        verbose_name = 'アルゴリズム'
        verbose_name_plural = 'アルゴリズム'

    def __str__(self):
        return f"{self.algorithm_name} (ID: {self.algorithm_id})"


class Checklist(models.Model):
    # checklist_id は PostgreSQL のシーケンスで管理（6000001 から開始）
    checklist_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='ユーザーID')
    checklist_name = models.CharField(max_length=100, verbose_name='チェックリスト名')
    checklist_description = models.TextField(blank=True, null=True, verbose_name='チェックリスト概要')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'checklist'
        verbose_name = 'チェックリスト'
        verbose_name_plural = 'チェックリスト'

    def __str__(self):
        return f"{self.checklist_name} (ID: {self.checklist_id})"


class Group(models.Model):
    # group_id は PostgreSQL のシーケンスで管理（7000001 から開始）
    group_id = models.BigAutoField(primary_key=True)
    group_name = models.CharField(max_length=50, verbose_name='グループ名')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='ユーザーID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'group'
        verbose_name = 'グループ'
        verbose_name_plural = 'グループ'

    def __str__(self):
        return f"{self.group_name} (ID: {self.group_id})"
