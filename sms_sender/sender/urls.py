from django.urls import path
from .views import send_sms, sms_inbox, sms_outbox, sms_draftbox

app_name = "sender"

urlpatterns = [
    path(r'send-sms/', send_sms.as_view(), name ='send-sms'),
    path(r'sms-inbox/', sms_inbox.as_view(), name ='sms-inbox'),
    path(r'sms-outbox/', sms_outbox.as_view(), name ='sms-outbox'),
    path(r'sms-draftbox/', sms_draftbox.as_view(), name ='sms-draftbox'),
    
]