from django.conf import settings

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection

from huawei_lte_api.api.Sms import Sms
from huawei_lte_api.enums.sms import BoxTypeEnum


from .serializers import SMSSerializer

def get_sms_list(sms_provider, box_type = "INBOX"):

    if box_type == "INBOX":
        LOCAL_sms_list   = sms_provider.get_sms_list(box_type=BoxTypeEnum.LOCAL_INBOX)
        SIM_sms_list     = sms_provider.get_sms_list(box_type=BoxTypeEnum.SIM_INBOX)
    elif box_type == "SENTBOX":
        LOCAL_sms_list   = sms_provider.get_sms_list(box_type=BoxTypeEnum.LOCAL_SENT)
        SIM_sms_list     = sms_provider.get_sms_list(box_type=BoxTypeEnum.SIM_SENT)
    elif box_type == "DRAFTBOX":
        LOCAL_sms_list   = sms_provider.get_sms_list(box_type=BoxTypeEnum.LOCAL_DRAFT)
        SIM_sms_list     = sms_provider.get_sms_list(box_type=BoxTypeEnum.SIM_DRAFT)


    LOCAL_sms_list_details = LOCAL_sms_list['Messages']['Message'] if LOCAL_sms_list['Count'] != str(0) else {}
    SIM_sms_list_details   = SIM_sms_list['Messages']['Message'] if SIM_sms_list['Count'] != str(0) else {}

    data     = {}
    status_code  =  HTTP_200_OK            

    if (int(LOCAL_sms_list['Count']) + int(SIM_sms_list['Count'])) <= 2  :
        if (int(LOCAL_sms_list['Count']) + int(SIM_sms_list['Count'])) == 2:
            data[LOCAL_sms_list_details["Index"]] = LOCAL_sms_list_details
            data[SIM_sms_list_details["Index"]]   = SIM_sms_list_details
        elif int(LOCAL_sms_list['Count'])  == 1:
            data.update(LOCAL_sms_list_details)
        else:
            data.update(SIM_sms_list_details)   

    elif (int(LOCAL_sms_list['Count']) + int(SIM_sms_list['Count'])) > 2 :

        if int(LOCAL_sms_list['Count']) > 1:
            for LOCAL_messages in LOCAL_sms_list_details:
                data[LOCAL_messages["Index"]] = LOCAL_messages

        if int(SIM_sms_list['Count']) > 1:
            for SIM_messages in SIM_sms_list_details:
                data[SIM_messages["Index"]] = SIM_messages
    else:
        data     = {'results': False} 
        status_code  = HTTP_400_BAD_REQUEST

    return data, status_code


# curl -X POST -d "phone=xxxxxxxxxxxx&content=test" "http://192.168.1.110:8050/sender/send-sms/"
class send_sms(APIView):

    serializer_class = SMSSerializer

    def post(self, request, *args, **kwargs):

        ser_data = request.data

        serializer = SMSSerializer(data=ser_data)

        if serializer.is_valid(raise_exception=True):

            # Connection
            connection = AuthorizedConnection(settings.HUAWEI_LTE_API_URL)

            # sms api
            sms_provider = Sms(connection)

            data = serializer.data

            # get data
            phone_number_list = ["+" + str(data["phone"]),]

            sms_content       = data["content"]

            # Send sms
            Status = sms_provider.send_sms(phone_number_list, sms_content)

            # create response
            # TODO: check delevry rapport or check draft if not sent
            DRAFTBOX_data, status_code = get_sms_list(sms_provider, box_type = "DRAFTBOX")

            data         = {'results': True, 'Status': Status}
            status_code  =  HTTP_200_OK 

        else:
            data     = {'results': False} 
            status_code  = HTTP_400_BAD_REQUEST 

        return Response(data, status=status_code)

class sms_inbox(APIView):

    permissions = [AllowAny]

    def get(self, request, *args, **kwargs):

        # Connection
        connection = AuthorizedConnection(settings.HUAWEI_LTE_API_URL)

        sms_provider = Sms(connection)

        data, status_code = get_sms_list(sms_provider, box_type = "INBOX")

        return Response(data, status=status_code)

class sms_outbox(APIView):

    permissions = [AllowAny]

    def get(self, request, *args, **kwargs):

        # Connection
        connection = AuthorizedConnection(settings.HUAWEI_LTE_API_URL)

        sms_provider = Sms(connection)

        data, status_code = get_sms_list(sms_provider, box_type = "SENTBOX") 

        return Response(data, status=status_code)

class sms_draftbox(APIView):

    permissions = [AllowAny]

    def get(self, request, *args, **kwargs):

        # Connection
        connection = AuthorizedConnection(settings.HUAWEI_LTE_API_URL)

        sms_provider = Sms(connection)

        data, status_code = get_sms_list(sms_provider, box_type = "DRAFTBOX") 

        return Response(data, status=status_code)
