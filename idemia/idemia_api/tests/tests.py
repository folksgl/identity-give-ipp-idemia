""" Run basic CRUD tests on EnrollmentRecord objects """
import uuid
import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


def generate_enrollment_record_data() -> dict:
    return {"record_uuid": uuid.uuid1(), "first_name": "Bob", "last_name": "Testington"}


def create_enrollment_record(client):
    """
    Perform a POST operation to the enrollment endpoint. This operation will
    serve as the base for many other tests, and will intentionally generate
    failures if the operation results in anything other than a 201 response
    """
    url = reverse("enrollment")
    record_data = generate_enrollment_record_data()
    response = client.post(url, record_data)
    assert response.status_code == status.HTTP_201_CREATED

    return (response, record_data)


class EnrollmentAllowedMethodTest(APITestCase):
    """ Test the allowable HTTP methods on the idemia API endpoints """

    def test_allowed_enrollment_methods(self):
        """ Ensure that only POST operations are allowed on the enrollment endpoint """
        url = reverse("enrollment")
        response = self.client.options(url)
        actions = response.data["actions"]
        allowed_methods = list(actions.keys())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(allowed_methods, ["POST"])


class EnrollmentRecordCRUDTest(APITestCase):
    """ Test crud operations on EnrollmentRecord objects """

    def test_get_enrollment(self):
        """ Create a user, then test the 'get' operation on that user """
        _response, record_data = create_enrollment_record(self.client)

        url = reverse("enrollment-record", args=[record_data["record_uuid"]])
        get_response = self.client.get(url)

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_delete_enrollment(self):
        """ Delete a user that was created """
        _response, record_data = create_enrollment_record(self.client)

        url = reverse("enrollment-record", args=[record_data["record_uuid"]])
        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_enrollment(self):
        """ Modify an existing enrollment record """
        _response, record_data = create_enrollment_record(self.client)
        url = reverse("enrollment-record", args=[record_data["record_uuid"]])

        # Modify the first name of the record data and test for persistence
        new_name = "Bobert"
        record_data["first_name"] = new_name
        put_response = self.client.put(url, record_data)

        get_response = self.client.get(url)

        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["first_name"], new_name)
