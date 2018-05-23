# coding=utf-8
#

from django.conf.urls import url

from host import *  # host, a10

from dk import *


urlpatterns = [


    url(r'^docker/info/(?P<pk>\d+)/', info, name="dockerinfo"),
    url(r'^docker/image/(?P<pk>\d+)/info/', image_info, name="docker_image_info"),
    url(r'^docker/image/(?P<pk>\d+)/rm/', image_rm, name="docker_image_rm"),
    url(r'^docker/image/(?P<pk>\d+)/', image, name="dockerimage"),
    url(r'^docker/image/', image, name="dockerimage"),
    url(r'^docker/container/(?P<pk>\d+)/info/', container_info, name="docker_container_info"),
    url(r'^docker/container/(?P<pk>\d+)/rm/', container_rm, name="docker_container_rm"),
    url(r'^docker/container/(?P<pk>\d+)/add/', container_add, name="docker_container_add"),
    url(r'^docker/container/(?P<pk>\d+)/', container, name="dockercontainer"),
    url(r'^docker/container/', container, name="dockercontainer"),
    url(r'^docker', DockerList.as_view(), name="dockerlist"),


]
