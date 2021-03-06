from django.conf.urls import patterns, include, url

from django.contrib import admin
from core.rest import router, PackageView


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/packages/(?P<code>.+)/$', PackageView.as_view(), name='jobspec-detail'),
    url(r'^api/v1/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('frontend.urls')),
)
