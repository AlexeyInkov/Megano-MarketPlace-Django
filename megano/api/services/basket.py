from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User

from api.models import Product, Order, OrderProduct, StatusOrder


class Basket(object):
    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)
        if not basket:
            basket = self.session[settings.BASKET_SESSION_ID] = {}
        self.basket = basket

    def change(self, user: User, product: Product, count: int) -> None:
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(product.pk)
        if product_id not in self.basket:
            self.basket[product_id] = {'count': count, 'price': product.price}
        else:
            self.basket[product_id]['count'] += count
        if self.basket[product_id]['count'] == 0:
            self.remove(product_id, user)

        self.save()

    def save(self):
        self.session[settings.BASKET_SESSION_ID] = self.basket
        self.session.modified = True

    def remove(self, product_id, user):
        """
        Удаление товара из корзины.
        """
        if product_id in self.basket:
            del self.basket[product_id]
            self.save()
            if user.is_authenticated:
                order = Order.objects.filter(user=user, status=StatusOrder.objects.get(id=1)).get()
                product = Product.objects.get(id=product_id)
                order_product = OrderProduct.objects.filter(order=order, product=product)
                if order_product:
                    order_product.delete()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.basket.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.basket[str(product.id)]['product'] = product
            self.basket[str(product.id)]['category'] = product.category
        for item in self.basket.values():
            item['total_price'] = item['price'] * item['count']
            yield item

    def __len__(self):
        """Возвращает количество наименований товара в корзине"""
        return sum(item['count'] for item in self.basket.values())

    def get_totalCost(self):
        """Возвращает общую стоимость товаров в корзине"""
        return sum(Decimal(item['price']) * item['count'] for item in self.basket.values())

    def clear(self) -> None:
        """очистить корзину"""
        return self.basket.clear()

    def copy_to_basket(self, user: User, order: Order) -> None:
        products = OrderProduct.objects.filter(order=order.pk)
        for item in products:
            product = Product.objects.get(id=item.product_id)
            self.change(user, product, item.count)

    def copy_to_order(self, order: Order) -> None:
        for key, item in self.basket.items():
            order_product = OrderProduct.objects.filter(
                order=order,
                product=Product.objects.get(id=int(key)))
            if order_product.exists():
                instance = order_product.get()
                instance.count = item['count']
                instance.price = item['price']
                instance.save()
            else:
                OrderProduct.objects.create(
                    order=order,
                    product=item['product'],
                    count=item['count'],
                    price=item['price']
                )

    def merge(self, user: User, order: Order) -> None:
        self.copy_to_basket(user, order)
        self.copy_to_order(order)
