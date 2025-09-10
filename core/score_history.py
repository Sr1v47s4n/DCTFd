from django.db import models
from django.utils import timezone
from challenges.models import Challenge
from teams.models import Team
from django.contrib.auth import get_user_model

User = get_user_model()

class ScoreHistory(models.Model):
    """
    Model to track score changes over time for teams and users.
    This enables accurate scoreboard graphs.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  # Score for this submission
    cumulative_score = models.IntegerField(default=0)  # Total score at this point
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Score History"
        ordering = ['timestamp']
        
    def __str__(self):
        if self.team:
            return f"{self.team.name} - {self.challenge.name} - {self.score} points"
        else:
            return f"{self.user.username} - {self.challenge.name} - {self.score} points"
