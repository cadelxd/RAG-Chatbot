from django.urls import path
from .views import DocumentUploadView, ChatbotView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('chat/', ChatbotView.as_view(), name='chatbot_chat'),
]