from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models as db_models
from .models import UserProfile, Question, Duel, DuelQuestion, Answer
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
        opponent = get_object_or_404(User, id=opponent_id)

        duel = Duel.objects.create(
            challenger=request.user,
            opponent=opponent,
            category=category,
            status="pending",
        )

        questions = list(Question.objects.filter(category=category))
        if len(questions) < 5:
            needed = 5 - len(questions)
            duel.delete()
            return render(
                request,
                "skillduel/create_duel.html",
                {
                    "users": users,
                    "error": f"Not enough {category} questions. Need {needed} more.",
                },
            )

        selected = random.sample(questions, 5)
        for i, q in enumerate(selected, start=1):
            DuelQuestion.objects.create(duel=duel, question=q, order=i)

        return redirect(f"/skillduel/{duel.id}")

    return render(request, "skillduel/create_duel.html", {"users": users})


# ── 7. Duel arena ─────────────────────────────────────────────
@login_required
def duel_arena_view(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)

    if request.user not in [duel.challenger, duel.opponent]:
        return redirect("/")

    if duel.status == "finished":
        return redirect(f"/skillduel/{duel.id}/result")

    if duel.status == "pending" and request.user == duel.opponent:
        duel.status = "active"
        duel.save()

    duel_questions = duel.duel_questions.all()
    answered_ids = Answer.objects.filter(duel=duel, player=request.user).values_list(
        "question_id", flat=True
    )

    current_dq = None
    for dq in duel_questions:
        if dq.question.id not in answered_ids:
            current_dq = dq
            break

    if current_dq is None:
        return render(request, "skillduel/waiting.html", {"duel": duel})

    if request.method == "POST":
        chosen = request.POST.get("answer")
        question = current_dq.question
        is_correct = chosen == question.correct

        Answer.objects.create(
            duel=duel,
            player=request.user,
            question=question,
            chosen=chosen,
            is_correct=is_correct,
        )

        # total_answers = Answer.objects.filter(duel=duel).count()
        # print(f"DEBUG total_answers={total_answers}")
        # if total_answers == 10:
        #     finish_duel(duel)
        #     return redirect(f"/skillduel/{duel.id}/result")

        # return redirect(f"/skillduel/{duel.id}")

        my_answers = Answer.objects.filter(duel=duel, player=request.user).count()
        if my_answers == 5:
            oppenent = (
                duel.opponent if request.user == duel.challenger else duel.challenger
            )
            opp_answers = Answer.objects.filter(duel=duel, player=oppenent).count()

            if opp_answers == 5:
                finish_duel(duel)
                return redirect(f"/skillduel/{duel.id}/result")
            else:
                return render(request, "skillduel/waiting.html", {"duel": duel})

        return redirect(f"/skillduel/{duel.id}")

    progress = len(answered_ids) + 1

    return render(
        request,
        "skillduel/arena.html",
        {
            "duel": duel,
            "duel_q": current_dq,
            "progress": progress,
        },
    )


# ── 8. Duel result ────────────────────────────────────────────
@login_required
def duel_result_view(request, duel_id):
    duel = get_object_or_404(Duel, id=duel_id)

    c_answers = Answer.objects.filter(duel=duel, player=duel.challenger)
    o_answers = Answer.objects.filter(duel=duel, player=duel.opponent)

    c_score = c_answers.filter(is_correct=True).count()
    o_score = o_answers.filter(is_correct=True).count()

    return render(
        request,
        "skillduel/result.html",
        {
            "duel": duel,
            "c_score": c_score,
            "o_score": o_score,
        },
    )


# ── 9. Leaderboard ────────────────────────────────────────────
@login_required
def leaderboard_view(request):
    # Ensure every user has a profile before showing leaderboard
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

    profiles = UserProfile.objects.select_related("user").order_by("-wins")
    return render(request, "skillduel/leaderboard.html", {"profiles": profiles})
