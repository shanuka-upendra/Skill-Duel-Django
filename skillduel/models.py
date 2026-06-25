from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# UserProfile
class UserProfile(models.Model):
    RANK_CHOICES = [
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
        ("legend", "Legend"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    rank = models.CharField(max_length=10, choices=RANK_CHOICES, default="bronze")

    def win_rate(self):
        total = self.wins + self.losses
        if total == 0:
            return 0
        return round((self.wins / total) * 100, 1)

# Question
class Question(models.Model):
    CATEGORY_CHOICES = [
        ("coding", "Coding"),
        ("math", "Math & Logic"),
    ]
    
    ANSWER_CHOICES = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
    ]
    
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    
    def __str__(self):
        return f"[{self.category}] {self.text[:60]}"
    
# Duel
class Duel(models.Model):
    CATEGORY_CHOICES = [
        ("coding", "Coding"),
        ("math", "Math & Logic"),
    ]
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]
    
    challenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name="duels_started")
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="duels_received")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="duels_won")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.challenger.username} vs {self.opponent.username} [{self.status}]"

# DuelQuestion
class DuelQuestion(models.Model):
    duel = models.ForeignKey(Duel, on_delete=models.CASCADE, related_name="duel_questions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"Duel {self.duel.id} - Q{self.order}"
    
# Answer
class Answer(models.Model):
    duel = models.ForeignKey(Duel, on_delete=models.CASCADE, related_name="answers")
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen = models.CharField(max_length=1, choices=Question.ANSWER_CHOICES)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.player.username} - Q{self.question.id} - {'✓' if self.is_correct else '✗'}"