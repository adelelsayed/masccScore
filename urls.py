from django.conf.urls import url

from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from masccIndex.views import *

app_name = 'masccIndex'

#router = DefaultRouter()
#router.register('HTNRisk',views.TheView, base_name = 'HTNRisk')

urlpatterns = [

    url(r'^masccIndex/(?P<patient>\d+)/$', TheView.as_view({'get':'view'}), name = 'ESCHTNRISK'),



    ]
