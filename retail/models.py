from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.utils import timezone
from django.db import models
from django.utils.html import format_html
from model_utils import FieldTracker


class UserProfile(AbstractUser):
    """
    用户表，新增字段如下
    """
    ROLES_SIZES = (
        ('1', '经理'),
        ('2', '店长'),
        ('3', '店员')
    )
    roles = models.CharField(max_length=1, choices=ROLES_SIZES, verbose_name='角色')

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.roles


class Person(models.Model):
    name = models.CharField(max_length=30, verbose_name='姓名')
    GENDER_SIZES = (
        ('M', '男'),
        ('F', '女'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_SIZES, verbose_name='性别')
    telephone = models.CharField(max_length=20, verbose_name='电话')

    def __str__(self):
        return self.name


class Customer(Person):
    TYPE_SIZES = (
        ('1', '一级代理'),
        ('2', '二级代理'),
        ('3', '普通顾客'),
        ('4', 'vip客户'),
    )
    level = models.CharField(max_length=1, choices=TYPE_SIZES, verbose_name='种类')
    location = models.CharField(max_length=32, verbose_name='收货地址')

    class Meta:
        verbose_name = '顾客'
        verbose_name_plural = verbose_name


class Provider(Person):
    class Meta:
        verbose_name = '供货商'
        verbose_name_plural = verbose_name


class Product(models.Model):
    name = models.CharField(max_length=30, verbose_name='产品名称')
    TYPE_SIZES = (
        ('1', '百货'),
        ('2', '零食'),
        ('3', '电器'),
        ('4', '水果'),
    )
    category = models.CharField(max_length=1, choices=TYPE_SIZES, verbose_name='产品类型')
    in_price = models.IntegerField(verbose_name='进价')
    wholesale_price = models.IntegerField(verbose_name='批发价')
    retail_price = models.IntegerField(verbose_name='零售价')

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def amount(self):
        result = 0
        for i in InLog.objects.filter(product=self):
            result += i.amount
        for i in OutLog.objects.filter(ordergood__product=self):
            result -= i.ordergood.amount

        color = 'green'
        if result == 0:
            color = 'red'
        return format_html(
            '<span style="color: {}"><b>{}</b></span>',
            color,
            result,
        )

    amount.short_description = '库存'

    def total_money(self):
        result = 0
        for i in InLog.objects.filter(product=self):
            result += i.amount
        for i in OutLog.objects.filter(ordergood__product=self):
            result -= i.ordergood.amount
        return format_html(
            '<span style="color: {}"><b>{}</b></span>',
            'red',
            result * self.in_price,
        )

    total_money.short_description = '积压资金额'


class Repository(models.Model):
    name = models.CharField(max_length=30, verbose_name='仓库名称')
    location = models.CharField(max_length=30, verbose_name='仓库地址')

    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = verbose_name

    def colored_location(self):
        color = 'red'
        return format_html(
            '<span style="color: {}"><b>{}</b></span>',
            color,
            self.location,
        )

    def __str__(self):
        return self.name


class Order(models.Model):
    time = models.DateTimeField(verbose_name='日期', default=timezone.now)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='顾客')
    comment = models.CharField(max_length=50, verbose_name='备注', blank=True, null=True)
    STATES = (
        ('1', '未付款'),
        ('2', '出货中'),
        ('3', '退货中'),
        ('4', '已完成'),
    )
    confirmation_STATES = (
        (False, '未审核'),
        (True, '已审核'),
    )
    status = models.CharField(max_length=1, choices=STATES, verbose_name='状态')
    confirmation = models.BooleanField(verbose_name='审核状态', choices=confirmation_STATES, default=False)
    tracker = FieldTracker()

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def profit(self):
        result = 0
        ordergoods = OrderGood.objects.filter(order=self)
        for ordergood in ordergoods:
            if int(self.customer.level) == 1 or int(self.customer.level) == 2:
                result += (ordergood.product.wholesale_price - ordergood.product.in_price) * ordergood.amount
            else:
                result += (ordergood.product.retail_price - ordergood.product.in_price) * ordergood.amount
        return result

    profit.short_description = '利润'

    def __str__(self):
        return "%s %s (%s)" % (
            self.customer,
            self.comment,
            self.status,
        )

    def price(self):
        result = 0
        ordergoods = OrderGood.objects.filter(order=self)
        for ordergood in ordergoods:
            print(int(self.customer.level) == 1 or int(self.customer.level) == 2)
            if int(self.customer.level) == 1 or int(self.customer.level) == 2:
                result += (ordergood.product.wholesale_price) * ordergood.amount
            else:
                result += (ordergood.product.retail_price) * ordergood.amount
        return result

    price.short_description = '价格'


    def colored_status(self):
        if self.status == '1':
            color = '#008888'
        elif self.status == '2':
            color = '#FF0000'
        elif self.status == '3':
            color = '#00FF00'
        elif self.status == '4':
            color = '#0000FF'
        else:
            color = '#696969'
        return format_html(
            '<span style="color: {}"><b>{}</b></span>',
            color,
            self.STATES[int(self.status) - 1][1],
        )

    colored_status.short_description = '状态'

    def save(self, *args, **kwargs):
        if self.tracker.previous('status') == '1' and self.status == '2':
            ordergoods = OrderGood.objects.filter(order=self)
            for ordergood in ordergoods:
                outlogs = OutLog.objects.filter(
                    Q(ordergood__order=self) & Q(ordergood=ordergood)
                )
                if len(outlogs) == 0:
                    outlog = OutLog.objects.create(
                        ordergood=ordergood
                    )
                    outlog.save()
        super(Order, self).save(*args, **kwargs)


# class Inventory(models.Model):
#     product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='商品')
#     repository = models.ForeignKey('Repository', on_delete=models.CASCADE, verbose_name='仓库')
#     amount = models.IntegerField(default=1, verbose_name="数量")

#     class Meta:
#         verbose_name = '库存'
#         verbose_name_plural = verbose_name


class OrderGood(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name='订单')
    product = models.ForeignKey('Product', verbose_name='商品名称', on_delete=models.CASCADE)
    repository = models.ForeignKey('Repository', on_delete=models.CASCADE, verbose_name='仓库')
    amount = models.PositiveIntegerField(verbose_name='商品数量', default=1)

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s %s (%d)" % (
            self.product,
            self.repository,
            self.amount,
        )


class InLog(models.Model):
    repository = models.ForeignKey('Repository', verbose_name='进货仓库', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', verbose_name='进货产品', on_delete=models.CASCADE)
    time = models.DateTimeField(verbose_name='进货日期', default=timezone.now)
    amount = models.PositiveSmallIntegerField(verbose_name='进货数量', default=1)
    provider = models.ForeignKey('Provider', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '进货日志'
        verbose_name_plural = verbose_name


class OutLog(models.Model):
    ordergood = models.ForeignKey('OrderGood', on_delete=models.CASCADE)
    time = models.DateTimeField(verbose_name='出货日期', default=timezone.now)

    class Meta:
        verbose_name = '出货日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s (%s)" % (
            self.ordergood,
            self.time,
        )


# 调货记录相当于   增加一条出库记录和入库记录
class TransferLog(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='调货数量', default=1)
    from_repository = models.ForeignKey('Repository', verbose_name="出货仓库", on_delete=models.CASCADE,
                                        related_name='from_repository')
    to_repository = models.ForeignKey('Repository', verbose_name="目的仓库", on_delete=models.CASCADE,
                                      related_name='to_repository')
    time = models.DateTimeField(verbose_name='出货日期', default=timezone.now)

    class Meta:
        verbose_name = '调货日志'
        verbose_name_plural = verbose_name


class Feedback_Stat(models.Model):
    class Meta:
        verbose_name = '仓库盘点'
        verbose_name_plural = verbose_name


class sale_manage(models.Model):
    class Meta:
        verbose_name = '销售统计-----'
        verbose_name_plural = verbose_name

