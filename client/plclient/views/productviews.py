from __future__ import annotations

import random
import string
from typing import Protocol, runtime_checkable

from plclient.api.fidelityprogramapi import FidelityProgramDetail
from plclient.api.productapi import ProductList, ProductDetail
from plclient.api.shopapi import ShopDetail
from plclient.api.userapi import UserDetail
from plclient.forms.forms import Table
from plclient.forms.productforms import ProductForm
from plclient.utils.settings import product_endpoint


@runtime_checkable
class ProductView(Protocol):

    def open_view(self):
        ...

    def close_view(self):
        ...

    def get_product(self, url: str):
        ...

    def create_product(self):
        ...

    def update_product(self, url: str):
        ...

    def delete_product(self, url: str):
        ...

    def get_all_products_by_shop(self):
        ...

    def get_all_products_by_program(self, fidelity_program: FidelityProgramDetail):
        ...

    def get_all_owned_prizes_by_shop(self, user: UserDetail):
        ...

class CustomerProductView:

    def __init__(self, shop: ShopDetail | None = None, fidelity_program: FidelityProgramDetail | None = None):
        self.shop = shop
        self.fidelity_program = fidelity_program

    def open_view(self):
        raise NotImplementedError

    def close_view(self):
        raise NotImplementedError

    def get_product(self, url: str):
        return ProductForm(ProductDetail(url=url).get())

    def create_product(self):
        raise NotImplementedError

    def update_product(self, url: str):
        raise NotImplementedError

    def delete_product(self, url: str):
        raise NotImplementedError

    def get_all_products_by_shop(self):
        if self.shop.url is None or self.shop.name is None:
            raise ValueError('Shop data is required')
        return Table(
            element=ProductList(api_endpoint=product_endpoint + 'byshop/' + self.shop.name),
            columns=['url', 'name', 'value', 'fidelity_program'],
            hidden_columns=['url'],
            selection_mode='multiple'
        )

    def get_all_products_by_program(self):
        if self.fidelity_program.url is None or self.fidelity_program.name is None:
            raise ValueError('Fidelity program data is required')
        return Table(
            element=ProductList(api_endpoint=product_endpoint + 'byprogram/' + self.fidelity_program.name),
            columns=['url', 'name', 'value', 'fidelity_program'],
            hidden_columns=['url'],
            selection_mode='multiple'
        )

    def get_all_owned_prizes_by_shop(self, user: UserDetail):
        if self.shop.url is None or self.shop.name is None:
            raise ValueError('Shop data is required')
        if user.url is None:
            raise ValueError('You need to filter prizes by user')
        return Table(
            element=ProductList(api_endpoint=product_endpoint + 'owned/' + self.shop.name + '/' + user.username),
            columns=['url', 'name', 'value', 'fidelity_program'],
            hidden_columns=['url'],
            selection_mode='multiple',
            key=str(user)+str(self.shop)
        )
