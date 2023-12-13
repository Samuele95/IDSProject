from __future__ import annotations
from typing import Protocol, runtime_checkable
from plclient.api.shopapi import ShopDetail, ShopList
from plclient.forms.forms import Table
from plclient.forms.shopforms import ShopForm, ShopUpdateForm
from plclient.utils.settings import shops_endpoint
from plclient.views.fidelityprogramviews import FidelityProgramView
from plclient.views.productviews import ProductView, CustomerProductView
import streamlit as st

from plclient.views.userviews import UserView


@runtime_checkable
class ShopView(Protocol):

    def open_view(self):
        ...

    def close_view(self):
        ...

    def get_shop(self, shopname: str):
        ...
    
    def get_session_shop(self):
        ...
    
    def create_shop(self, shopname: str):
        ...

    def update_shop(self, shopname: str):
        ...
    
    def get_all_shops(self):
        ...


class CustomerShopView:

    def __init__(self, fidelity_program_view: FidelityProgramView):
        self.fidelity_program_view = fidelity_program_view

    def open_view(self):
        all_shops, selected_shop = st.columns(2)
        with all_shops:
            shops = self.get_all_shops().show()
        with selected_shop:
            if len(shops.selected_rows) > 0:
                self.get_shop(shops.selected_rows[0]['name']).show()

    def close_view(self):
        raise NotImplementedError

    def get_shop(self, shopname: str):
        shop = ShopDetail(url=shops_endpoint+shopname).get()
        return ShopForm(
            element=shop,
            product_list=CustomerProductView(shop).get_all_products_by_shop(),
            fidelity_programs=self.fidelity_program_view.get_all_fidelity_programs_by_shop(shopname)
        )
    
    def get_session_shop(self):
        raise NotImplementedError
    
    def create_shop(self, shopname: str):
        raise NotImplementedError

    def update_shop(self, shopname: str):
        raise NotImplementedError

    def get_all_shops(self):
        return Table(element=ShopList(), columns=['url', 'name', 'location'], hidden_columns=['url'])


class CashierShopView:

    def __init__(self, shop: ShopDetail, user_view: UserView, fidelity_program_view: FidelityProgramView):
        if shop.url is None or shop.name is None:
            raise ValueError('Cannot access shop data')
        self.shop = shop
        self.user_view = user_view
        self.fidelity_program_view = fidelity_program_view

    def open_view(self):
        self.get_session_shop().show()


    def close_view(self):
        raise NotImplementedError

    def get_shop(self, shopname: str):
        raise NotImplementedError

    def get_session_shop(self):
        return ShopUpdateForm(ShopForm(
            element=self.shop,
            product_list=CustomerProductView(self.shop).get_all_products_by_shop(),
            fidelity_programs=self.fidelity_program_view.get_all_fidelity_programs_by_shop(self.shop.name)
        ),
            user_list=self.user_view.get_all_users()
        )


    def create_shop(self, shopname: str):
        raise NotImplementedError

    def update_shop(self, shopname: str):
        raise NotImplementedError

    def get_all_shops(self):
        raise NotImplementedError




# class CashierShopView:
#
#     def open_view(self):
#         return self.get_session_shop().show()
#
#     def close_view(self):
#         raise NotImplementedError
#
#     def __init__(self, shop: ShopDetail):
#         self.shop = shop
#
#     def get_shop(self, shopname: str):
#         raise NotImplementedError
#
#     def get_session_shop(self):
#         raise NotImplementedError
#
#     def update_shop(self, shopname: str):
#         raise NotImplementedError
#
#     def get_all_shops(self):
#         raise NotImplementedError