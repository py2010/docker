# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response, redirect, HttpResponse, get_object_or_404
from django.core.exceptions import PermissionDenied

from cmdb.models import Docker, docker

import json

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from requests import ConnectionError
import time
import datetime
from .forms import ContainerAddForm

from urllib3.util import connection
old_connection = connection.create_connection


def host2ip(address, *args, **kwargs):
    # 将docker虚拟域名转为IP
    host, port = address
    if host.endswith('.docker.sdj'):
        # 比如192_168_80_238.docker.sdj转为192.168.80.238
        host = host.replace('.docker.sdj', '').replace('_', '.')
        # print host, '!!!!!!!!'
    address = host, port

    return old_connection(address, *args, **kwargs)

'''
1.重写urllib3函数，使虚拟构造的xxx_xxx_xxx_xxx.docker.sdj域名socker连接时使用其对应IP。
2.使用构造域名是为支持TLS验证，因ssl证书使用IP时，需每台Docker物理机都配置生成相应IP证书，
3.为简化配置处理，统一使用泛域名*.docker.sdj SSL证书，为避免增加/etc/hosts解析，所以重写函数
4.CA证书验证不支持自定义headers设置Host域：headers={"Host" : "1.docker.sdj:2375"}，
所以无法直接使用IP进行泛域名SSL证书验证，最终选择当前方案使虚拟域名对CMDB用户透明。
'''
connection.create_connection = host2ip


class DockerList(LoginRequiredMixin, ListView):
    template_name = "dockerlist.html"
    model = Docker

    def get_context_data(self, **kwargs):
        return super(self.__class__, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        if not self.request.user.has_perm('cmdb.view_docker'):
            raise PermissionDenied
        return super(self.__class__, self).get(request, *args, **kwargs)


def docker_client(request, pk):
    # docker.DockerClient，docker模块版本2.7.0
    if not request.user.has_perm('cmdb.change_docker'):
        raise PermissionDenied
    dk = get_object_or_404(Docker, id=pk)
    return dk.client


def get_client_method(client, func, *args, **kwargs):
    # 用于异常处理， docker.DockerClient.xxx.xxx...
    p = client
    for m in func.split('.'):
        p = getattr(p, m)
    try:
        res = p(*args, **kwargs)
    except ConnectionError as e:
        res = '连接失败：%s' % str(e)
    except Exception as e:
        res = '出错：%s' % str(e)
    # print res, 2323232
    return res


def beijin(timestr):
    # 容器时间+8转换为北京时间
    try:
        t = time.strptime(timestr, '%Y-%m-%d %H:%M')
        d = datetime.datetime(*t[:5]) + datetime.timedelta(hours=8)
        return d.strftime("%Y-%m-%d %H:%M")
    except:
        # import ipdb; ipdb.set_trace()
        return timestr


def info(request, pk):
    # docker info
    # import ipdb;import ipdb; ipdb.set_trace()
    client = docker_client(request, pk)
    dk = client.docker
    text = get_client_method(client, 'info')
    try:
        text = json.dumps(text)
    except:
        pass
    return render(request, 'docker_info.html', locals())


def image(request, pk=0):
    # docker images 镜像管理
    dockers = Docker.objects.all()
    if pk:
        client = docker_client(request, pk)
        images = get_client_method(client, 'images.list')
        if type(images) != list:
            # docker宿主机连接失败或未知错误
            error = images
        else:
            imgs = []
            for image in images:
                img = {}
                if image.tags:
                    img['name'], img['ver'] = image.tags[0].split(':')
                    # print image.tags[0].split(':'), 888888888

                if 'name' not in img:
                    try:
                        img['name'] = image.attrs['RepoDigests'][0].split('@')[0]
                    except:
                        pass

                img['time'] = beijin(image.attrs['Created'][:16].replace('T', ' '))
                img['size'] = image.attrs['Size']
                img['id'] = image.id
                imgs.append(img)
            # imgs.sort(cmp=None, key=lambda s: s['name'], reverse=False)
    return render(request, 'docker_image.html', locals())


def image_rm(request, pk):
    # 删除镜像
    imgid = request.GET.get('img')
    client = docker_client(request, pk)
    try:
        res = get_client_method(client, 'images.remove', imgid, force=True)
        if res:
            msg = {"error": str(res)}
        else:
            msg = {"image remove": "ok."}
    except Exception as e:
        msg = {"error": str(e)}

    return HttpResponse(json.dumps(msg))


def image_info(request, pk):
    # 镜像信息
    imgid = request.GET.get('img')
    info = request.GET.get('info')
    client = docker_client(request, pk)
    try:
        img = get_client_method(client, 'images.get', imgid)
        # print img, 8888
        if isinstance(img, docker.models.images.Image):
            msg = getattr(img, info)
            if info == 'history':
                msg = msg()
        else:
            msg = {"error": str(img)}
        # print msg, 99999
    except Exception as e:
        msg = str(e)
    try:
        msg = json.dumps(msg)
    except:
        msg = json.dumps({"error": str(msg)})
    return HttpResponse(msg)


def container(request, pk=0):
    # docker ps -a 容器管理
    dockers = Docker.objects.all()
    if pk:
        client = docker_client(request, pk)
        containers = get_client_method(client, 'containers.list', all=1)
        if type(containers) != list:
            # docker宿主机连接失败或未知错误
            error = containers
        else:
            cons = []
            for container in containers:
                con = {}
                con['name'] = container.name
                # print container.name, 777
                try:
                    con['image'] = container.image.tags[0].split(':')[0].split('/')[-1]
                except:
                    con['image'] = ''

                con['ip'] = ''
                try:
                    ip = container.attrs['NetworkSettings']['IPAddress']
                    if not ip:
                        ips = set()
                        for net in container.attrs['NetworkSettings']['Networks']:
                            ips.add(container.attrs['NetworkSettings']['Networks'][net]['IPAddress'])
                        # print ips, 33333333
                        ip = ', '.join(ips)
                    con['ip'] = ip

                except Exception as e:
                    # import ipdb; ipdb.set_trace()
                    print e, 898989

                con['status'] = container.status
                con['time'] = beijin(container.attrs['Created'][:16].replace('T', ' '))
                con['runtime'] = container.attrs['State']['StartedAt'][:16].replace('T', ' ')
                con['id'] = container.id
                cons.append(con)
            # cons.sort(cmp=None, key=lambda s: s['name'], reverse=False)
    return render(request, 'docker_container.html', locals())


def container_rm(request, pk):
    # 删除容器
    conids = request.GET.get('id').strip(',').split(',')
    client = docker_client(request, pk)
    msg = {"container remove": "ok."}
    try:
        for conid in conids:
            container = get_client_method(client, 'containers.get', conid)
            if type(container) in (unicode, str):
                msg = {"error": str(container)}
            else:
                print container.remove(force=True)
    except Exception as e:
        msg = {"error": str(e)}

    return HttpResponse(json.dumps(msg))


def container_info(request, pk):
    # 容器信息、操作
    conid = request.GET.get('id')
    info = request.GET.get('info')
    client = docker_client(request, pk)
    try:
        img = get_client_method(client, 'containers.get', conid)
        # print img, 8888
        if isinstance(img, docker.models.containers.Container):
            msg = getattr(img, info)
            if info != 'attrs':
                msg = msg()
                if not msg:
                    msg = {info: "ok."}
                # print msg, 9999
        else:
            msg = {"error": str(img)}
        # print msg, 99999
    except Exception as e:
        msg = str(e)
    if info != 'logs':
        try:
            msg = json.dumps(msg)
        except:
            msg = json.dumps({"error": str(msg)})
    return HttpResponse(msg)


def container_add(request, pk):
    # 容器添加
    # 由于docker_client.containers.run未封装支持设置IP、挂载
    # 所以使用底层模块docker_client.api.create_container
    client = docker_client(request, pk)

    if request.method == 'POST':
        # print request.POST, 7777777
        form = ContainerAddForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name', None)
            image = form.cleaned_data.get('image', None)
            network = form.cleaned_data.get('network', None)
            ip = form.cleaned_data.get('ip', None)
            volumes = form.cleaned_data.get('volumes', '')
            command = form.cleaned_data.get('command', None)
            start = form.cleaned_data.get('start')

            kwargs = {'name': name, 'image': image, 'command': command, 'detach': 1}

            host_config = {'NetworkMode': network}
            vs = [volume.strip() for volume in volumes.split(',') if volume.strip()]
            if vs:
                # print vs, 888888
                host_config.update({'Binds': vs})

            kwargs.update({'host_config': host_config})

            networking_config = {
                'EndpointsConfig': {
                    network: {'IPAMConfig': {'IPv4Address': ip}}
                }
            } if ip else {network: None}

            kwargs.update({'networking_config': networking_config})

            # print kwargs, 3444444
            try:
                res = client.api.create_container(**kwargs)

                if start == 'on':
                    # 启动容器
                    container = client.containers.get(res['Id'])
                    container.start()
                    success_url = reverse_lazy('cmdb:dockercontainer', kwargs={'pk': pk})
                    return redirect(success_url)
            except Exception as e:
                form.errors.update({'错误': str(e)})

        # else:
        #     import ipdb;import ipdb; ipdb.set_trace()

    # 打开表单页面
    images = get_client_method(client, 'images.list')
    imgs = []
    for image in images:
        if image.tags:
            img = {'name': image.tags[0].split(':')[0]}
            imgs.append(img)
    imgs.sort(cmp=None, key=lambda s: s['name'], reverse=False)

    networks = get_client_method(client, 'networks.list')
    nets = []
    for network in networks:
        driver = network.attrs['Driver']
        if driver in ('macvlan', 'bridge'):
            net = {'type': driver, 'name': network.name, 'subnet': network.attrs['IPAM']['Config'][0]['Subnet']}
            nets.append(net)
    nets.sort(cmp=None, key=lambda s: s['type'], reverse=False)

    return render(request, 'docker_container_add.html', locals())
