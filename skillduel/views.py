from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models as db_models
from .models import UserProfile, Question, Duel, DuelQuestion, Answer
from .utils import fetch_questions_from_api
import random


# ── 1. Register ───────────────────────────────────────────────
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# ── 2. Login ──────────────────────────────────────────────────
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


# ── 3. Logout ─────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect("/login")


# ── 4. Home ───────────────────────────────────────────────────
@login_required
def home_view(request):
    recent_duels = Duel.objects.filter(
        db_models.Q(challenger=request.user) | db_models.Q(opponent=request.user)
    ).order_by("-created_at")[:5]

    # Get or create profile safely
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return render(
        request,
        "skillduel/home.html",
        {
            "recent_duels": recent_duels,
            "profile": profile,
        },
    )


# ── Pending duels inbox ───────────────────────────────────────
@login_required
def inbox_view(request):
    # Duels where I am the opponent and haven't started yet
    pending = Duel.objects.filter(opponent=request.user, status="pending").order_by(
        "-created_at"
    )

    # Duels where I am challenger and opponent hasn't joined
    sent = Duel.objects.filter(challenger=request.user, status="pending").order_by(
        "-created_at"
    )

    # Active duels I still need to finish
    active = Duel.objects.filter(
        db_models.Q(challenger=request.user) | db_models.Q(opponent=request.user),
        status="active",
    ).order_by("-created_at")

    return render(
        request,
        "skillduel/inbox.html",
        {
            "pending": pending,
            "sent": sent,
            "active": active,
        },
    )


# ── Profile page ──────────────────────────────────────────────
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)

    # Last 10 duels for this user
    duels = Duel.objects.filter(
        db_models.Q(challenger=profile_user) | db_models.Q(opponent=profile_user),
        status="finished",
    ).order_by("-created_at")[:10]

    return render(
        request,
        "skillduel/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "duels": duels,
        },
    )


# ── 5. finish_duel — MUST be before duel_arena_view ──────────
def finish_duel(duel):
    def score(user):
        return Answer.objects.filter(duel=duel, player=user, is_correct=True).count()

    c_score = score(duel.challenger)
    o_score = score(duel.opponent)

    if c_score > o_score:
        winner = duel.challenger
        loser = duel.opponent
    elif o_score > c_score:
        winner = duel.opponent
        loser = duel.challenger
    else:
        winner = None
        loser = None

    duel.winner = winner
    duel.status = "finished"
    duel.save()

    if winner and loser:
        # get_or_create prevents the DoesNotExist crash
        winner_profile, _ = UserProfile.objects.get_or_create(user=winner)
        loser_profile, _ = UserProfile.objects.get_or_create(user=loser)

        winner_profile.wins += 1
        loser_profile.losses += 1

        def get_rank(wins):
            if wins >= 20:
                return "legend"
            if wins >= 10:
                return "platinum"
            if wins >= 5:
                return "gold"
            if wins >= 2:
                return "silver"
            return "bronze"

        winner_profile.rank = get_rank(winner_profile.wins)
        winner_profile.save()
        loser_profile.save()


# ── 6. Create duel ────────────────────────────────────────────
@login_required
def create_duel_view(request):
    users = User.objects.exclude(id=request.user.id)

    if request.method == "POST":
        opponent_id = request.POST.get("opponent")
        category = request.POST.get("category")

        # Validate category
        if category not in ["coding", "math"]:
            return render(
                request,
                "skillduel/create_duel.html",
                {"users": users, "error": "Invalid category selected."},
            )

        opponent = get_object_or_404(User, id=opponent_id)

        # Fetch fresh questions from OpenTDB API
        api_questions = fetch_questions_from_api(category, amount=5)

        # Fallback to DB if API fails
        if not api_questions:
            db_questions = list(Question.objects.filter(category=category))
            if len(db_questions) < 5:
                return render(
                    request,
                    "skillduel/create_duel.html",
                    {
                        "users": users,
                        "error": "Could not load questions right now. Please try again in a moment.",
                    },
                )
            import random

            selected = random.sample(db_questions, 5)
            api_questions = [
                {
                    "text": q.text,
                    "category": q.category,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "correct": q.correct,
                }
                for q in selected
            ]

        # Create duel
        duel = Duel.objects.create(
            challenger=request.user,
            opponent=opponent,
            category=category,
            status="pending",
        )

        # Save questions and link to duel
        for i, q_data in enumerate(api_questions, start=1):
            question = Question.objects.create(
                text=q_data["text"],
                category=q_data["category"],
                option_a=q_data["option_a"],
                option_b=q_data["option_b"],
                option_c=q_data["option_c"],
                option_d=q_data["option_d"],
                correct=q_data["correct"],
            )
            DuelQuestion.objects.create(duel=duel, question=question, order=i)

        return redirect(f"/skillduel/{duel.id}")

    # GET request — just show the form
    return render(request, "skillduel/create_duel.html", {"users": users})


# ── 7. Duel arena ─────────────────────────────────────────────
@login_required
def duel_arena_view(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)

    if request.user not in [duel.challenger, duel.opponent]:
        return redirect('/')

    if duel.status == 'finished':
        return redirect(f'/skillduel/{duel.id}/result')

    if duel.status == 'pending' and request.user == duel.opponent:
        duel.status = 'active'
        duel.save()

    duel_questions = duel.duel_questions.all()
    answered_ids   = Answer.objects.filter(
        duel=duel, player=request.user
    ).values_list('question_id', flat=True)

    # Find first unanswered question
    current_dq = None
    for dq in duel_questions:
        if dq.question.id not in answered_ids:
            current_dq = dq
            break

    # Player finished all 5
    if current_dq is None:
        opponent = duel.opponent if request.user == duel.challenger else duel.challenger
        opp_answers = Answer.objects.filter(duel=duel, player=opponent).count()
        if opp_answers == 5:
            finish_duel(duel)
            return redirect(f'/skillduel/{duel.id}/result')
        return render(request, 'skillduel/waiting.html', {'duel': duel})

    if request.method == 'POST':
        chosen   = request.POST.get('answer')
        question = current_dq.question

        already = Answer.objects.filter(
            duel=duel, player=request.user, question=question
        ).exists()

        if not already and chosen:
            is_correct = (chosen == question.correct)
            Answer.objects.create(
                duel       = duel,
                player     = request.user,
                question   = question,
                chosen     = chosen,
                is_correct = is_correct
            )

        return redirect(f'/skillduel/{duel.id}')

    progress = len(answered_ids) + 1

    return render(request, 'skillduel/arena.html', {
        'duel':     duel,
        'duel_q':   current_dq,
        'progress': progress,
    })


# ── 8. Duel result ────────────────────────────────────────────
@login_required
def duel_result_view(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)

    # Get all questions for this duel in order
    duel_questions = duel.duel_questions.select_related('question').all()

    # Get answers for both players
    c_answers = Answer.objects.filter(duel=duel, player=duel.challenger)
    o_answers = Answer.objects.filter(duel=duel, player=duel.opponent)

    c_score = c_answers.filter(is_correct=True).count()
    o_score = o_answers.filter(is_correct=True).count()

    # Build question breakdown for current user
    my_answers = Answer.objects.filter(
        duel=duel, player=request.user
    ).select_related('question')

    # Map question_id → answer for quick lookup
    my_answer_map = {a.question_id: a for a in my_answers}

    breakdown = []
    for i, dq in enumerate(duel_questions, start=1):
        q       = dq.question
        my_ans  = my_answer_map.get(q.id)
        breakdown.append({
            'number':     i,
            'text':       q.text,
            'option_a':   q.option_a,
            'option_b':   q.option_b,
            'option_c':   q.option_c,
            'option_d':   q.option_d,
            'correct':    q.correct,
            'chosen':     my_ans.chosen if my_ans else None,
            'is_correct': my_ans.is_correct if my_ans else False,
        })

    return render(request, 'skillduel/result.html', {
        'duel':      duel,
        'c_score':   c_score,
        'o_score':   o_score,
        'breakdown': breakdown,
    })


# ── 9. Leaderboard ────────────────────────────────────────────
@login_required
def leaderboard_view(request):
    # Ensure every user has a profile before showing leaderboard
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

    profiles = UserProfile.objects.select_related("user").order_by("-wins")
    return render(request, "skillduel/leaderboard.html", {"profiles": profiles})
