# Create your views here.
from django.http import JsonResponse
from django.core.mail import send_mail

from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2

from ai_models.detector import PersonDetector
from ai_models.fence_logic import is_near_fence
from ai_models.recorder import VideoRecorder

camera = cv2.VideoCapture(0)
detector = PersonDetector()
recorder = VideoRecorder()
alert_shown = False
intrusion_active = False


def gen_frames():
    global alert_shown, intrusion_active

    while True:
        success, frame = camera.read()
        if not success:
            continue

        persons = detector.detect(frame)
        intrusion = False

        for box in persons:
            if is_near_fence(box):
                intrusion = True
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        intrusion_active = intrusion


        # Start 5-sec recording
        if intrusion and not recorder.recording:
            recorder.start(frame)

        #  Continue recording
        if recorder.recording:
            recorder.update(frame)

        # 📡 STREAM FRAME TO BROWSER
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

def send_intrusion_email():
    send_mail(
        subject='🚨 Fence Intrusion Alert',
        message='An intrusion has been detected near the fence. A 5-second video has been recorded.',
        from_email='salihualiyu438@gmail.com',
        recipient_list=['salihuabdulkareem353@gmail.com'],
        fail_silently=True
    )
    if intrusion and not alert_shown:
            send_intrusion_email()
            alert_shown = True

    if not intrusion:
            alert_shown = False

def index(request):
    return render(request, 'fenceapp/index.html')

def video_feed(request):
    return StreamingHttpResponse(gen_frames(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def intrusion_status(request):
    return JsonResponse({
        "intrusion": intrusion_active
    })
