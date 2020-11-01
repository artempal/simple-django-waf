from django.contrib import admin
from .models import BlackList, AttackType, Events, Configs, Proxy

import requests
from django.contrib.auth.models import Group
from django.conf import settings

admin.site.unregister(Group)


def gen_url(port=False, https=False):
    if not port and not https:
        try:
            configs = Configs.objects.get(pk=1)
        except Exception:
            return "http://localhost"
        port = configs.port
        https = configs.https

    if https:
        site_url = "https://"
    else:
        site_url = "http://"
    site_url += "localhost"
    if port != 80:
        site_url += ":" + str(port)
    return site_url


admin.site.site_header = "Artem WAF "
admin.site.site_title = "Artem WAF"
admin.site.site_url = gen_url()
admin.site.index_title = 'Администрирование WAF'


# Register your models here.
@admin.register(BlackList)
class BlackListAdmin(admin.ModelAdmin):
    icon_name = 'do_not_disturb_on'
    list_display = ('reg', 'type', 'head', 'url', 'body', 'args', 'active')
    list_filter = ('active', 'head', 'url', 'body', 'args', 'stable')
    fields = [('reg', 'stable'), ('head', 'url', 'args', 'body'), 'active', 'type']
    search_fields = ['reg']


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('url', 'method', 'reg', 'location', 'ip', 'date')
    icon_name = 'error'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Configs)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ('hostname',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        admin.site.site_url = gen_url(obj.port, obj.https)
        all_proxy = Proxy.objects.all().values_list('hostname', flat=True)
        for proxy in all_proxy:
            try:
                configs = Configs.objects.get(pk=1)
                if configs.https:
                    requests.post('https://{}:{}/{}'.format(proxy, configs.port, 'restart'),
                                  data={'key': settings.SECRET_KEY}, verify=False)
                else:
                    requests.post('http://{}:{}/{}'.format(proxy, configs.port, 'restart'),
                                  data={'key': settings.SECRET_KEY})
            except Exception as e:
                print(e)
        super().save_model(request, obj, form, change)


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    icon_name = 'exit_to_app'
    readonly_fields = ('hostname', 'port')
    list_display = ('hostname', 'port', 'update_at',)

    def has_add_permission(self, request):
        return False
    # admin.site.register(AttackType)
