from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Country, Status
from unittest.mock import patch, MagicMock
import requests

@patch('requests.get')
class CountryAPITests(APITestCase):

    def setUp(self):
        self.status_obj = Status.objects.create(total_countries=0)

    def test_refresh_countries(self, mock_get):
        mock_countries_data = [
            {
                "name": "Test Country",
                "capital": "Test Capital",
                "region": "Test Region",
                "population": 1000000,
                "currencies": [{"code": "TC"}],
                "flag": "https://flag.co/test.svg"
            }
        ]
        mock_exchange_rates_data = {
            "rates": {
                "TC": 1.5
            }
        }

        mock_get.side_effect = [
            self.mock_response(json_data=mock_countries_data),
            self.mock_response(json_data=mock_exchange_rates_data)
        ]

        url = reverse('country-refresh')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Country.objects.count(), 1)
        self.assertEqual(Status.objects.first().total_countries, 1)

    def test_get_countries(self, mock_get):
        Country.objects.create(name="Country A", region="Region A", currency_code="CURA", population=100, estimated_gdp=1000)
        Country.objects.create(name="Country B", region="Region B", currency_code="CURB", population=200, estimated_gdp=2000)

        url = reverse('country-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_countries_with_filters(self, mock_get):
        Country.objects.create(name="Country A", region="Region A", currency_code="CURA", population=100, estimated_gdp=1000)
        Country.objects.create(name="Country B", region="Region B", currency_code="CURB", population=200, estimated_gdp=2000)

        url = reverse('country-list')
        response = self.client.get(url, {'region': 'Region A'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Country A')

    def test_get_country_detail(self, mock_get):
        country = Country.objects.create(name="Test Country", population=100)
        url = reverse('country-detail', kwargs={'name': 'Test Country'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Country')

    def test_delete_country(self, mock_get):
        country = Country.objects.create(name="Test Country", population=100)
        url = reverse('country-detail', kwargs={'name': 'Test Country'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Country.objects.count(), 0)

    def test_get_status(self, mock_get):
        self.status_obj.total_countries = 5
        self.status_obj.save()
        url = reverse('status-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_countries'], 5)

    def test_get_summary_image(self, mock_get):
        # Create a dummy image for testing
        from PIL import Image
        import os
        if not os.path.exists('cache'):
            os.makedirs('cache')
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save("cache/summary.png")

        url = reverse('summary-image')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/png')

    def mock_response(self, status_code=200, json_data=None, content=None):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        if json_data:
            mock_resp.json.return_value = json_data
        if content:
            mock_resp.content = content
        
        def raise_for_status():
            if status_code >= 400:
                raise requests.exceptions.HTTPError(f"HTTP Error {status_code}")
        mock_resp.raise_for_status = raise_for_status
        return mock_resp