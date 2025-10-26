from .renderers import PNGRenderer
import random
from django.utils import timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Country, Status
from .serializers import CountrySerializer, StatusSerializer
from PIL import Image, ImageDraw, ImageFont
import os

class CountryRefresh(APIView):
    def post(self, request):
        try:
            countries_url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
            exchange_rates_url = "https://open.er-api.com/v6/latest/USD"

            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retries)
            http = requests.Session()
            http.mount("https://", adapter)

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            countries_response = http.get(countries_url, timeout=10, headers=headers)
            countries_response.raise_for_status()
            countries_data = countries_response.json()

            exchange_rates_response = http.get(exchange_rates_url, timeout=10, headers=headers)
            exchange_rates_response.raise_for_status()
            exchange_rates_data = exchange_rates_response.json()['rates']

            for country_data in countries_data:
                currency_code = None
                if 'currencies' in country_data and country_data['currencies']:
                    currency_code = country_data['currencies'][0].get('code')

                exchange_rate = None
                if currency_code and currency_code in exchange_rates_data:
                    exchange_rate = exchange_rates_data[currency_code]

                estimated_gdp = 0
                if country_data.get('population') and exchange_rate:
                    estimated_gdp = country_data.get('population') * random.randint(1000, 2000) / exchange_rate

                country, created = Country.objects.update_or_create(
                    name=country_data['name'],
                    defaults={
                        'capital': country_data.get('capital'),
                        'region': country_data.get('region'),
                        'population': country_data.get('population'),
                        'currency_code': currency_code,
                        'exchange_rate': exchange_rate,
                        'estimated_gdp': estimated_gdp,
                        'flag_url': country_data.get('flag'),
                    }
                )

            status_obj, created = Status.objects.get_or_create(pk=1)
            status_obj.last_refreshed_at = timezone.now()
            status_obj.total_countries = Country.objects.count()
            status_obj.save()

            self.generate_summary_image()

            return Response({"message": "Countries refreshed successfully"}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": "External data source unavailable", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def generate_summary_image(self):
        if not os.path.exists('cache'):
            os.makedirs('cache')

        status_obj = Status.objects.first()
        top_5_countries = Country.objects.order_by('-estimated_gdp')[:5]

        img = Image.new('RGB', (800, 600), color = 'white')
        d = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        if status_obj:
            d.text((10,10), f"Total Countries: {status_obj.total_countries}", fill=(0,0,0), font=font)
            d.text((10,40), f"Last Refresh: {status_obj.last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S')}", fill=(0,0,0), font=font)
        else:
            d.text((10,10), "Total Countries: N/A", fill=(0,0,0), font=font)
            d.text((10,40), "Last Refresh: N/A", fill=(0,0,0), font=font)

        d.text((10,80), "Top 5 Countries by GDP:", fill=(0,0,0), font=font)

        y_pos = 110
        if top_5_countries:
            for country in top_5_countries:
                d.text((10, y_pos), f"- {country.name}: {country.estimated_gdp:,.2f}", fill=(0,0,0), font=font)
                y_pos += 30
        else:
            d.text((10, y_pos), "- No top countries available.", fill=(0,0,0), font=font)

        img.save("cache/summary.png")

class CountryList(generics.ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = Country.objects.all()
        region = self.request.query_params.get('region')
        currency = self.request.query_params.get('currency')
        sort = self.request.query_params.get('sort')

        if region:
            queryset = queryset.filter(region__iexact=region)
        if currency:
            queryset = queryset.filter(currency_code__iexact=currency)
        if sort == 'gdp_desc':
            queryset = queryset.order_by('-estimated_gdp')

        return queryset

class CountryDetail(generics.RetrieveDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'name'

class StatusDetail(generics.RetrieveAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    def get_object(self):
        obj, created = Status.objects.get_or_create(pk=1)
        return obj

from .renderers import PNGRenderer

class SummaryImage(APIView):
    renderer_classes = [PNGRenderer]

    def get(self, request):
        try:
            with open('cache/summary.png', 'rb') as f:
                return Response(f.read(), content_type='image/png')
        except FileNotFoundError:
            return Response({"error": "Summary image not found"}, status=status.HTTP_404_NOT_FOUND)