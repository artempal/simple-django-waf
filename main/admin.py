from django.contrib import admin
from .models import BlackList, AttackType, Events

admin.site.site_header = "Artem WAF "
admin.site.site_title = "Artem WAF"
admin.site.site_url = 'http://localhost:9999/'
admin.site.index_title = 'Администрирование WAF'


# Register your models here.
@admin.register(BlackList)
class BlackListAdmin(admin.ModelAdmin):
    list_display = ('reg', 'type', 'head', 'url', 'body', 'args', 'active')
    list_filter = ('active', 'head', 'url', 'body', 'args', 'stable')
    fields = [('reg', 'stable'), ('head', 'url', 'args', 'body'), 'active', 'type']
    search_fields = ['reg']

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('url', 'method', 'reg', 'location', 'type', 'ip','date')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

#admin.site.register(AttackType)


