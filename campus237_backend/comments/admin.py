from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('etablissement', 'auteur', 'note', 'statut', 'date_publication')
    list_filter = ('statut', 'note', 'date_publication')
    search_fields = ('contenu', 'auteur__email', 'etablissement__nom')
    readonly_fields = ('date_publication', 'date_mise_a_jour')
