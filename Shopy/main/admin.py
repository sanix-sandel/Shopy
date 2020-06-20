from django.contrib import admin
from .models import Product, ProductTag, ProductImage
from django.utils.html import format_html

class ProductAdmin(admin.ModelAdmin):
    list_display=('name', 'slug', 'in_stock', 'price')
    list_filter=('active', 'in_stock', 'date_update')
    list_editable=('in_stock',)
    search_fields=('name',)
    prepopulated_fields={"slug":("name",)}
admin.site.register(Product, ProductAdmin)



class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('products',)
admin.site.register(ProductTag, ProductTagAdmin)



class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', 'product_name')
    readonly_fields = ('thumbnail',)
    search_fields = ('product__name',)
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="%s"/>' % obj.thumbnail.url
            )
        return "-"
    thumbnail_tag.short_description = "Thumbnail"
    def product_name(self, obj):
        return obj.product.name
admin.site.register(ProductImage, ProductImageAdmin)
