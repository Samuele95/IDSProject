from __future__ import annotations
from typing import Protocol, runtime_checkable
from dataclasses import dataclass

from plclient.api.shopapi import ShopDetail
from plclient.api.transactionapi import TransactionDetail
from plclient.api.userapi import UserDetail
from plclient.forms.transactionforms import TransactionCreateForm, TransactionForm
import streamlit as st

from plclient.views.productviews import CustomerProductView
from plclient.views.shopviews import CustomerShopView
from plclient.views.userviews import GenericUserView


@runtime_checkable
class TransactionView(Protocol):

    def open_view(self):
        ...

    def close_view(self):
        ...
    
    def get_transaction(self, transactionurl: str):
        ...
    
    def create_transaction(self, userurl: str | None = None, shopurl: str | None = None):
        ...

@dataclass(frozen=True, eq=True, order=True)
class CustomerTransactionView:
    user: UserDetail
    shops: CustomerShopView

    def open_view(self):
        with st.container() as container:
            st.caption('Start a new order')
            tr_shops = self.shops.get_all_shops().show()
            if len(tr_shops.selected_rows) > 0:
                self.create_transaction(
                    userurl=self.user.url,
                    shopurl=tr_shops.selected_rows[0]['url']
                )

    def close_view(self):
        raise NotImplementedError
    
    def get_transaction(self, transactionurl: str):
        return TransactionForm(TransactionDetail(url=transactionurl).get()).show()
    
    def create_transaction(self, userurl: str | None = None, shopurl: str | None = None):
        if shopurl is None:
            raise ValueError('You must choose a shop to start an order')
        user = self.user if userurl is None else UserDetail(url=userurl).get()
        shop = ShopDetail(url=shopurl).get()
        return TransactionCreateForm(
            user=user,
            shop=shop,
            product_list=CustomerProductView(shop=shop).get_all_products_by_shop(),
            prize_list=CustomerProductView(shop=shop).get_all_owned_prizes_by_shop(user)
        ).show()


@dataclass(frozen=True, eq=True, order=True)
class CashierTransactionView:
    shop: ShopDetail
    users: GenericUserView

    def open_view(self):
        with st.container() as container:
            st.caption('Start a new order')
            tr_users = self.users.get_all_users().show()
            with st.expander('Create new user'):
                self.users.user_create_form().show()
            if len(tr_users.selected_rows) > 0:
                self.create_transaction(
                    userurl=tr_users.selected_rows[0]['url'],
                    shopurl=self.shop.url
                )

    def close_view(self):
        raise NotImplementedError

    def get_transaction(self, transactionurl: str):
        return TransactionForm(TransactionDetail(url=transactionurl).get()).show()

    def create_transaction(self, userurl: str | None = None, shopurl: str | None = None):
        if userurl is None:
            raise ValueError('You must choose a user to start an order')
        shop = self.shop if shopurl is None else ShopDetail(url=shopurl).get()
        user = UserDetail(url=userurl).get()
        return TransactionCreateForm(
            user=user,
            shop=shop,
            product_list=CustomerProductView(shop=shop).get_all_products_by_shop(),
            prize_list=CustomerProductView(shop=shop).get_all_owned_prizes_by_shop(user),
        ).show()