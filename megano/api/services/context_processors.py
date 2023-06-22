from .basket import BasketAnonim


def cart(request):
    return {'basket': BasketAnonim(request)}

