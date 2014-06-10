from django.conf.urls import patterns, include, url
from semantic import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'skillExtraction.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^search/', views.search, name='search'),
    url(r'^autocheck/', views.autocheck, name='autocheck'),
    url(r'^admin/', include(admin.site.urls)),
)

