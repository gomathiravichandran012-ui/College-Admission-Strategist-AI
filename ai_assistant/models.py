from django.db import models
from students.models import StudentProfile


class ChatHistory(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='chat_history'
    )

    user_message = models.TextField()

    ai_response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat - {self.student.full_name}"