"""
実績システム用のビュー関数
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.models import Account
from .achievement_utils import get_user_achievements_progress, grant_achievement_rewards
from .models import Achievement, UserAchievement, UserStats


def session_login_required(view_func):
    """セッションベースの認証デコレータ（再利用）"""
    from functools import wraps
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_account_authenticated'):
            return redirect('accounts:student_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@session_login_required
def achievements_view(request):
    """実績一覧ページ"""
    user_id = request.session.get('account_user_id')
    user = get_object_or_404(Account, user_id=user_id)
    
    # 実績進捗を取得
    progress = get_user_achievements_progress(user)
    
    # ユーザー統計を取得
    stats, _ = UserStats.objects.get_or_create(user=user)
    
    # 未受取の報酬がある実績を取得
    unclaimed_achievements = UserAchievement.objects.filter(
        user=user,
        is_achieved=True,
        is_rewarded=False
    ).select_related('achievement')
    
    # 新規達成実績をモーダル表示用に準備
    new_achievements = []
    total_new_coins = 0
    if unclaimed_achievements.exists():
        for ua in unclaimed_achievements:
            new_achievements.append({
                'name': ua.achievement.name,
                'description': ua.achievement.description,
                'icon': ua.achievement.icon,
                'tier': ua.achievement.get_tier_display() if ua.achievement.tier else '',
                'reward': ua.achievement.reward_coins,
            })
            total_new_coins += ua.achievement.reward_coins
    
    context = {
        'progress': progress,
        'stats': stats,
        'unclaimed_achievements': unclaimed_achievements,
        'unclaimed_count': unclaimed_achievements.count(),
        'new_achievements': new_achievements,
        'total_new_coins': total_new_coins,
    }
    
    return render(request, 'codemon/achievements.html', context)


@session_login_required
@require_POST
def claim_achievement_reward(request, achievement_id):
    """実績報酬を受け取る"""
    user_id = request.session.get('account_user_id')
    user = get_object_or_404(Account, user_id=user_id)
    
    achievement = get_object_or_404(Achievement, achievement_id=achievement_id)
    
    # 実績達成済みかチェック
    try:
        user_achievement = UserAchievement.objects.get(
            user=user,
            achievement=achievement,
            is_achieved=True,
            is_rewarded=False
        )
    except UserAchievement.DoesNotExist:
        messages.error(request, '受け取れる報酬がありません。')
        return redirect('codemon:achievements')
    
    # 報酬を付与
    coins = grant_achievement_rewards(user, [achievement])
    
    if coins > 0:
        # セッションに通知フラグを設定（トースト表示用）
        if 'achievement_notifications' not in request.session:
            request.session['achievement_notifications'] = []
        
        request.session['achievement_notifications'].append({
            'name': achievement.name,
            'icon': achievement.icon,
            'reward': coins,
        })
        request.session.modified = True
        
        messages.success(request, f'🎉 {achievement.name} の報酬 {coins}コイン を受け取りました！')
    
    return redirect('codemon:achievements')


@require_POST
@session_login_required
def clear_achievement_notifications(request):
    """トースト通知表示後にセッションから削除"""
    if 'achievement_notifications' in request.session:
        del request.session['achievement_notifications']
        request.session.modified = True
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})
