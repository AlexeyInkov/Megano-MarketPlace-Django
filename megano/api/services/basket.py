from typing import Union

from django.conf import settings
from decimal import Decimal

from django.shortcuts import get_object_or_404

from api.models import Product, Order, OrderProduct, StatusOrder


class BasketAnonim(object):
    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)
        if not basket:
            basket = self.session[settings.BASKET_SESSION_ID] = {}
        self.basket = basket

    def change(self, product: Product, count: int) -> None:
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(product.pk)
        if product_id not in self.basket:
            self.basket[product_id] = {'count': count, 'price': product.price}
        else:
            self.basket[product_id]['count'] += count
        if self.basket[product_id]['count'] == 0:
            self.remove(product_id)
        self.save()

    def save(self):
        self.session[settings.BASKET_SESSION_ID] = self.basket
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
            self.basket[str(product.id)]['category'] = product.category
        for item in self.basket.values():
            item['price'] = Decimal(item['price'])
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


class BasketService:
    """
    Сервис корзины

    add_to_cart: метод добавления товара в корзину
    remove_from_cart: убирает товар из корзины
    update_product: изменить количество товара в корзине и заменить продавца
    get_goods: получение товаров из корзины
    get_quantity: получение количества товаров в корзине
    get_total_sum: получение общей суммы товаров в корзине
    get_total_discounted_sum: получение общей суммы товаров в корзине со скидками
    clear: очистка корзины
    """

    def __init__(self, request):
        if request.user.is_authenticated:
            print('Cоздаем Order корзину')
            self.basket = Order.objects.filter(
                user=request.user,
                status=StatusOrder.objects.get(status='Корзина')).first()
            if not self.basket:
                self.basket = Order.object.create(
                    user=request.user,
                    status=StatusOrder.objects.get(status='Корзина'))
        else:
            print('Создаем SESSION корзину')
            self.basket = BasketAnonim(request)

    def remove_from_cart(self, product_id: int) -> None:
        """
        убрать товар из корзины

        product_id: id товара
        """
        product = get_object_or_404(Product, id=product_id)
        if isinstance(self.basket, Order):
            cart_product = get_object_or_404(OrderProduct, order=self.basket)
            cart_product.delete()
            self.basket.save()
        else:
            self.basket.remove(product)

    def add_to_basket(self, product, count: int, price: Decimal = 0) -> bool:
        """
        Изменить количество товара в корзине
        quantity: новое количество
        """
        if isinstance(self.basket, Order):
            cart_product = OrderProduct.objects.filter(order=self.basket, product=product).first()
            if not cart_product:
                cart_product = OrderProduct.objects.create(order=self.basket,
                                                           product=product,
                                                           count=count,
                                                           price=product.price)
            else:
                cart_product.count += count
                cart_product.save()
                self.basket.save()
        else:
            self.basket.change(product, count)

    def get_goods(self) -> Union[OrderProduct, BasketAnonim]:
        """получить товары из корзины"""
        if isinstance(self.basket, BasketService):
            return self.basket.order_products.all
        return self.basket

    def get_count(self) -> int:
        """получить количество товаров в корзине"""
        return len(self.basket)

    def get_total_sum(self) -> Decimal:
        """получить общую сумму заказа"""
        if isinstance(self.basket, Order):
            return self.basket.totalCost
        return self.basket.get_totalCost()

    def merge_baskets(self, other:BasketAnonim):
        """Перенос анонимной корзины в корзину зарегистрированного"""
        for item in other:
            self.add_to_basket(item['product'], item['count'], )
        other.clear()

    def clear(self) -> None:
        """очистить корзину"""
        return self.basket.clear()

    def save(self) -> None:
        """Сохранить корзину (любую сущность)"""
        return self.save()

    def __len__(self):
        """получить общее количество товаров в корзине"""
        return len(self.basket)
