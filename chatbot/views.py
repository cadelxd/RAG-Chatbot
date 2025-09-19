from django.shortcuts import render

# Create your views here.
# core/views.py
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import process_document, get_answer

class DocumentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        if not file_obj:
            return Response({'error': 'No file was submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save file temporarily
        temp_dir = 'temp_docs'
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file_obj.name)

        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        success = process_document(file_path)
        os.remove(file_path)

        if success:
            request.session['document_processed'] = True
            return Response({'message': 'Document processed successfully.'}, status=status.HTTP_200_OK)
        else:
            request.session['document_processed'] = False
            return Response({'error': 'Failed to process document.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatbotView(APIView):
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')
        if not request.session.get('document_processed'):
            return Response({'error': 'Please upload a document first.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_message:
            return Response({'error': 'No message provided.'}, status=status.HTTP_400_BAD_REQUEST)

        bot_response = get_answer(user_message)
        return Response({'bot_response': bot_response}, status=status.HTTP_200_OK)