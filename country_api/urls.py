from django.urls import path
from .views import (
    CountryRefresh,
    CountryList,
    CountryDetail,
    StatusDetail,
    SummaryImage
)

urlpatterns = [
    path('countries/refresh', CountryRefresh.as_view(), name='country-refresh'),
    path('countries/image', SummaryImage.as_view(), name='summary-image'),
    path('countries', CountryList.as_view(), name='country-list'),
    path('countries/<str:name>', CountryDetail.as_view(), name='country-detail'),
    path('status', StatusDetail.as_view(), name='status-detail'),
]