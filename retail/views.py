import hashlib
import time

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.utils import json

from .serializers import *
from .models import *


class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class InLogPagination(PageNumberPagination):
    page_size = 12
    # 向后台要多少条
    page_size_query_param = 'page_size'
    # 定制多少页的参数
    page_query_param = "page"
    max_page_size = 100


class InLogViewSet(viewsets.ModelViewSet):
    queryset = InLog.objects.all()
    serializer_class = InLogSerializer
    # pagination_class = InLogPagination


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


@staff_member_required
def customer_view(request):
    return render(request, 'customer_view.html', {'theads': ["仓库", "产品", "数量", "供货商", "时间"], 'trows': [["仓库", "产品", "数量", "供货商", "时间"]]})


@staff_member_required
def custom_view(request):


    # . . . create objects of MyModel . . .
    # . . . call their processing methods . . .
    # . . . store in context variable . . .
    # trows = []
    # All_Products = Product.objects.all()
    # # print(All_Products)
    # for One_Product in All_Products:
    #     print(One_Product)
    #     One_Product_InLogs = InLog.objects.filter( product=One_Product )
    #     # print(One_Product_InLogs)
    #     for One_Product_InLog in One_Product_InLogs:
    #         One_Product_InLog_info = [One_Product_InLog.product, One_Product_InLog.repository,
    #                                   One_Product_InLog.amount,One_Product_InLog.provider, One_Product_InLog.time]
    #         trows.append(One_Product_InLog_info)
    # print(trows)
    # return render(request, 'custom_view.html',{'theads': ["产品","仓库","数量","供货商","时间"], 'trows':trows})
    # r = render_to_response('custom_view.html')
    # return HttpResponse(r)
    # 获取一个仓库的所有商品信息
    trows = []
    All_Repositorys = Repository.objects.all()
    for One_Repository in All_Repositorys:
        temp_trows = []
        One_Repository_InLogs = InLog.objects.filter(repository=One_Repository)
        # 进货数量
        for One_Repository_InLog in One_Repository_InLogs:
            One_Repository_InLog_info = [One_Repository_InLog.repository, One_Repository_InLog.product,
                                         One_Repository_InLog.amount, One_Repository_InLog.provider,
                                         One_Repository_InLog.time]
            temp_trows.append(One_Repository_InLog_info)

        # print(temp_trows)
        for trow in temp_trows:
            # 减去商品的出货记录
            for i in OutLog.objects.filter(ordergood__product=trow[1]):
                trow[2] -= i.ordergood.amount
            # 加上调货进库数量
            for i in TransferLog.objects.filter(Q(product=trow[1]) & Q(to_repository=trow[0])):
                trow[2] += i.amount
            # 减去调货出库数量
            # print(1111111111111)
            # print(trow)
            for i in TransferLog.objects.filter(Q(product=trow[1]) & Q(from_repository=trow[0])):
                # print(i)
                # print(i.amount)
                trow[2] -= i.amount
        trows += temp_trows
    # print(trows)
    return render(request, 'custom_view.html', {'theads': ["仓库", "产品", "数量", "供货商", "时间"], 'trows': trows})


def miniappOrder(request):
    resp = {'errorcode': 100, 'detail': 'Get success'}
    return HttpResponse(json.dumps(resp), content_type="application/json")


class Login(View):
    def get(self, request):
        resp = {'errorcode': 100, 'detail': 'Get success'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    def post(self, request):
        print(request.POST)
        customer1 = Customer.objects.all()[0]
        print(customer1)
        order = Order.objects.create(
            customer_id=customer1.id,
            comment='手机小程序订单',
            status='1',
            confirmation=False,
        )
        order.save()
        print(request.POST.get('data'))
        all_goods = json.loads(request.POST.get('data'))
        for goods in all_goods:
            print(goods)
            myOrderGood = OrderGood.objects.create(
                order_id=order.id,
                product_id=goods['id'],
                repository_id=1,
                amount=goods['num'],
            )
            myOrderGood.save()
        return HttpResponse('OK11')
