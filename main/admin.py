from django.contrib import admin
from .models import BlackList, AttackType, Events, Configs
import os

from django.contrib.auth.models import Group

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
    list_display = ('url', 'method', 'reg', 'location', 'type', 'ip', 'date')
    icon_name = 'error'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Configs)
class ConfigsAdmin(admin.ModelAdmin):
    readonly_fields = ('daemon_status',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        admin.site.site_url = gen_url(obj.port, obj.https)
        cmd = "sudo systemctl restart simple-waf.service"
        obj.daemon_status = os.system(cmd)
        #  TODO здесь будет рестарт сервиса waf
        super().save_model(request, obj, form, change)

# admin.site.register(AttackType)
