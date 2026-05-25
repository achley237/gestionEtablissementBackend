from django.contrib import admin

from .models import Establishment


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'type', 'statut', 'directeur', 'date_creation')
    list_filter = ('statut', 'type', 'ville', 'region')
    search_fields = ('nom', 'ville', 'region', 'directeur__email')
    readonly_fields = ('date_creation', 'date_mise_a_jour')
