from django.contrib import admin
from .models import UserProfile, Question, Duel, DuelQuestion, Answer

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Question)
admin.site.register(Duel)
admin.site.register(DuelQuestion)
admin.site.register(Answer)

