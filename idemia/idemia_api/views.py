""" Views for Idemia API """
import logging
import uuid
import requests
from django.conf import settings
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import EnrollmentRecord
from .serializers import EnrollmentRecordSerializer


def log_transaction():
    """
    Log a transaction to the transaction logging microservice.
    Returns True if the logging attempt was successful.
    """
    logging.info("Logging a transaction to /transaction")
    if settings.DEBUG:
        logging.debug("Skipping transaction logging while in debug mode")
        return True  # Skip sending a transaction log in debug mode

    service_url = "https://identity-give-transaction-log.app.cloud.gov"
    transaction_url = f"{service_url}/transaction/"
    payload = {
        "service_type": "PROOFING SERVICE",
        "customer": "test_customer",
        "csp": "test_csp",
        "cost": 0,
        "result": "test_result",
    }

    try:
        response = requests.post(transaction_url, data=payload)
        response.raise_for_status()  # Raises HTTPError, if one occurred.
        return True
    except requests.exceptions.RequestException as error:
        logging.error("Request raised exception: %s", error)

    return False


class EnrollmentRecordCreate(CreateAPIView):
    """ Create EnrollmentRecord objects """

    queryset = EnrollmentRecord.objects.all()
    serializer_class = EnrollmentRecordSerializer

    def create(self, request, *args, **kwargs):
        """ Create an enrollment record. POST to idemia /pre-enrollments endpoint """
        if log_transaction():
            response = super().create(request, *args, **kwargs)
            if response.status_code == status.HTTP_201_CREATED:
                logging.info("Record Created -- POST to idemia /pre-enrollments")
        else:
            response = Response(
                {"message": "Transaction logging failed. Aborting.."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return response


class EnrollmentRecordDetail(RetrieveUpdateDestroyAPIView):
    """ Perform read, update, delete operations on EnrollmentRecord objects """

    queryset = EnrollmentRecord.objects.all()
    serializer_class = EnrollmentRecordSerializer

    def retrieve(self, request, *args, **kwargs):
        """ Retrieve an enrollment record with the specified uuid """
        response = super().retrieve(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            logging.info("Record Retrieved - GET on idemia /pre-enrollments/UEID")
            logging.info("Call update() if status has changed")
        return response

    def update(self, request, *args, **kwargs):
        """ Update an enrollment record """
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            logging.info("Record Updated")
        return response

    def destroy(self, request, *args, **kwargs):
        """ Delete an enrollment record """
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logging.info("Record Deleted")
        return response


@api_view(http_method_names=["GET"])
def location_view(_request, zipcode):
    """ Exposes the /locations idemia UEP endpoint """
    logging.info("Calling Idemia /locations endpoint with zipcode: %s", zipcode)

    # Dummy location info (taken from idemia api response documentation)
    location_list = [
        {
            "externalId": "5300155",
            "name": "Abilene, TX-Pine St",
            "phoneNumber": None,
            "timeZone": "America/Chicago",
            "address": {
                "building": "IdentoGO",
                "city": "Abilene",
                "addressLine2": None,
                "postalCode": "79601-5911",
            },
            "details": "",
            "geocode": {"latitude": 32.4509, "longitude": -99.73221},
            "hours": "",
            "programAvailability": [],
        },
        {
            "externalId": "5300173",
            "name": "Abilene, TX-S Willis St",
            "phoneNumber": None,
            "timeZone": "America/Chicago",
            "address": {
                "building": "IdentoGO",
                "city": "Abilene",
                "addressLine2": None,
                "postalCode": "79605-1734",
            },
            "details": "",
            "geocode": {"latitude": 32.45019, "longitude": -99.76409},
            "hours": "",
            "programAvailability": [],
        },
    ]
    return Response(location_list)
