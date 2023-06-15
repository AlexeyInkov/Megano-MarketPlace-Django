from django.conf import settings
from decimal import Decimal
from api.models import Product


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

    def change(self, product, count):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(product.id)
        if product_id not in self.basket:
            self.basket[product_id] = {'count': count,
                                     'price': str(product.price)}
        else:
            self.basket[product_id]['count'] += count
        if self.basket[product_id]['count'] == 0:
            self.remove(product_id)
        self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.BASKET_SESSION_ID] = self.basket
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product_id):
        """
        Удаление товара из корзины.
        """
        if product_id in self.basket:
            del self.basket[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.basket.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.basket[str(product.id)]['product'] = product

        for item in self.basket.values():
            item['price'] = Decimal(item['price'])
            yield item

    def clear(self) -> None:
        """очистить корзину"""
        return self.basket.clear()

    def merge_baskets(self, old):
        """Перенос анонимной корзины в корзину зарегистрированного"""
        for item in old:
            self.change(item['product'], item['count'], )
        old.clear()
