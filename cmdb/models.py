# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# from django.utils.timezone import now, localdate
from datetime import datetime, timedelta

from django.core.cache import cache
from django import template
from django.contrib.auth.models import User, Group
import traceback
from Crypto.Cipher import AES
import base64
import paramiko
import docker
import os
import urlparse


class Docker(models.Model):
    # 容器宿主机、物理机，必需已开启监听端口(swarm)，用于cmdb连接远程API
    # CMDB不使用swarm、docker service功能，因网络只能为overlay无法自定义配置

    name = models.CharField(max_length=100, verbose_name=u"标识名称")
    """
    host = models.CharField(verbose_name='宿主机', max_length=50, default='.docker.sdj',
        help_text='Docker容器宿主机、物理机域名，比如xxx.docker.sdj，<br/>\
        如果未开启tls证书验证，则可直接填写IP，否则请填写域名<br/>\
        因ssl证书使用IP时，需每台Docker物理机都配置生成相应IP证书，<br/>\
        为简化配置处理，统一使用泛域名*.docker.sdj SSL证书<br/>')
    """
    ip = models.GenericIPAddressField(u"宿主机IP", max_length=15)
    port = models.IntegerField(verbose_name='Docker端口', default=2375)
    tls = models.BooleanField(verbose_name='TLS', default=True, help_text='Docker-API不会进行安全验证，任意接入的客户端都能进行所有操作<br/>为安全需配置TLS，客户端使用证书访问API接口')
    # ver = models.CharField(max_length=20, verbose_name=u"Docker版本", help_text='Docker服务端版本', null=True, blank=True)
    text = models.TextField(u"备注信息", default='', null=True, blank=True)

    class Meta:
        verbose_name = '容器宿主机'

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.ip)

    def ip2host(self):
        # 将IP转换为虚拟构造的域名，用于泛域名*.docker.sdj SSL证书验证
        return '%s.docker.sdj' % self.ip.replace('.', '_')

    @property
    def client(self):
        tls = 1 if self.tls else ''  # docker.utils.utils.kwargs_from_env
        try:
            cli = docker.from_env(
                timeout=10,
                environment={
                    'DOCKER_HOST': 'tcp://%s:%d' % (self.ip2host(), self.port),
                    'DOCKER_TLS_VERIFY': tls
                }
            )
        except docker.errors.TLSParameterError as e:
            print 'SSL证书不存在？', 'DOCKER_TLS_VERIFY:', tls
            raise e

        cli.docker = self
        return cli

