from django.shortcuts import render, redirect
from s3 import AudioTranscriptionService
from model import gemini_model
from django.core.files.storage import FileSystemStorage
import os
from django.http import JsonResponse
# Create your views here.
def main(request):
    return render(request,'index.html',{})

def loading(request):
    if request.method == 'POST':
        phone_no = request.POST.get('phone')
        audio_file = request.FILES['recording']
        return processing(request, phone_no, audio_file)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

def processing(request,phone_no,audio_file):
    file_extension = os.path.splitext(audio_file.name)[-1].lower().strip('.')
    valid_formats = ['amr', 'flac', 'wav', 'ogg', 'mp3', 'mp4', 'webm', 'm4a']

    if file_extension not in valid_formats:
        return JsonResponse({"status": "error", "message": "Invalid file format."}, status=400)
        
        # fs = FileSystemStorage()  # Default: MEDIA_ROOT
        # filename = fs.save(audio_file.name, audio_file)
        # audio_file_url = fs.url(filename)

    ats = AudioTranscriptionService()
            
    transcript = ats.process_audio_file(audio_file,file_extension)
    label, risk = gemini_model(transcript)
    request.session['risk'] = risk
    if label == 0:
        return JsonResponse({"status": "success", "result_type": "safe"})
    elif label == 1:
        return JsonResponse({"status": "success", "result_type": "spam"})
    else:
        return JsonResponse({"status": "error", "message": "unexe."}, status=400)


def result(request, result_type):
    risk = None
    if request.method == 'POST':  # Handle the button form redirect
        return redirect('home')  # Redirect to home
    if result_type == 'safe':
        risk = request.session.get('risk')
        phone = request.session.get('stored_phone', 'No number provided.')
        return render(request, 'safe_result.html', {'phone':phone})
    elif result_type == 'spam':
        risk = request.session.get('risk')
        phone = request.session.get('stored_phone', 'No number provided.')
        return render(request, 'spam_result.html', {'phone':phone})
    return redirect('home')


def error(request):
    return render(request, 'error.html', {})