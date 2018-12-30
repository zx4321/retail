from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from retail import models
from retail.models import Feedback_Stat, OrderGood, sale_manage
from retail.views import custom_view, customer_view

admin.site.site_header = '零售商品管理系统'


class CustomAdmin(admin.ModelAdmin):
    list_per_page = 50


class BillSubInline(admin.TabularInline):
    model = models.OrderGood
    extra = 1 #默认显示条目的数量


@admin.register(models.Order)
class OrderAdmin(CustomAdmin):
    list_display = ('customer', 'colored_status', 'comment', 'time', 'price', 'profit', "confirmation")
    inlines = [BillSubInline, ]
    list_filter = ['status']
    search_fields = ['customer__name']
    date_hierarchy = 'time'

    def changelist_view(self, request, extra_context=None):
        user = request.user
        if user.is_superuser:
            self.list_display = ('customer', 'colored_status', 'comment', 'time', 'price', 'profit', "confirmation")
            self.list_editable = ['confirmation']
            self.list_filter = ['status','confirmation']
        else:
            self.list_display = ('customer', 'colored_status', 'comment', 'time', 'price', 'profit')
        return super(OrderAdmin, self).changelist_view(request, extra_context=None)

    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        if request.user.is_superuser:
            self.readonly_fields = []
        else:
            self.readonly_fields = ['confirmation']
        return self.readonly_fields

    # def save_model(self, request, obj, form, change):
        # from django.shortcuts import render
        # return render(request, '403.html')
        # if request.user.is_superuser:
        #     print(1)
        # super().save_model(request, obj, form, change)
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     return qs.filter(customer=request.user)


@admin.register(models.Repository)
class RepositoryAdmin(CustomAdmin):
    list_display = ('name', 'colored_location')


@admin.register(models.Provider)
class ProviderAdmin(CustomAdmin):
    list_display = ('name', 'gender', 'telephone')
    search_fields = ['name']


@admin.register(models.Product)
class ProductAdmin(CustomAdmin):
    list_display = ('name','in_price','wholesale_price', 'retail_price', 'category', 'amount', 'total_money')
    list_filter = ['category']
    search_fields = ['name']

@admin.register(models.Customer)
class CustomerAdmin(CustomAdmin):
    list_display = ('name', 'gender', 'telephone', 'level', 'location')
    list_filter = ['level']
    search_fields = ['name']


# @admin.register(models.Inventory)
# class InventoryAdmin(CustomAdmin):
#     list_display = ('product', 'repository', 'amount')


@admin.register(models.InLog)
class InLogAdmin(CustomAdmin):
    list_display = ('product', 'repository', 'time', 'amount', 'provider')
    search_fields = ['provider__name']
    date_hierarchy = 'time'


@admin.register(models.OutLog)
class OutLogAdmin(CustomAdmin):
    list_display = ('ordergood', 'time')
    date_hierarchy = 'time'


@admin.register(models.TransferLog)
class TransferLogAdmin(CustomAdmin):
    list_display = ('product', 'amount','from_repository', 'to_repository', 'time')
    date_hierarchy = 'time'
    list_filter = ['from_repository','to_repository']
    # list_display = ('from_repository', 'to_repository', 'time')
    # fk_fields = ('product',)

# admin.site.register(models.UserProfile, UserAdmin)
@admin.register(models.UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('id', 'username', 'roles')
    list_editable = ['roles']
    list_filter = ['roles']


@admin.register(Feedback_Stat)
class FeedbackStatsAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_content=None):
        return custom_view(request)


# @admin.register(sale_manage)
# class saleManageAdmin(admin.ModelAdmin):
#     def changelist_view(self, request, extra_content=None):
#         return customer_view(request)
