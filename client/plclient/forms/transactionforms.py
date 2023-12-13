from typing import Any
from plclient.forms.forms import Form, Table
from plclient.api.productapi import ProductDetail, ProductList
from plclient.api.shopapi import ShopDetail
from plclient.api.transactionapi import TransactionDetail
from plclient.api.userapi import UserDetail
import streamlit as st


class TransactionForm(Form):
    element: TransactionDetail

    def __init__(self, element: TransactionDetail) -> None:
        if element.url is None or element.id is None:
            raise ValueError('Cannot access to transaction data')
        self.element = element

    def show(self) -> Any:
        with st.container(border=True) as container:
            st.caption("Product List")
            Table(
                element=ProductList(data=self.element.shopping_cart, datainstance=ProductDetail),
                columns=["url", "name", "value", "fidelity_program"],
                hidden_columns=["url"],
            )
            st.write(f"User: {UserDetail(url=self.element.user).get().username}")
            st.divider()
            st.write(f"Shop: {ShopDetail(url=self.element.shop).get().name}")
            st.divider()
            st.write(f"Total: {self.element.total}")
            st.divider()
            st.write(f"Executed at: {self.element.executed_at}")


class TransactionCreateForm(Form):
    element: TransactionDetail | None

    def __init__(self, user: UserDetail, shop: ShopDetail, product_list: Table, prize_list: Table) -> None:
        if user.url is None or user.username is None:
            raise ValueError('Missing user data to complete transaction')
        if shop.url is None or shop.name is None:
            raise ValueError('Missing shop data to complete transaction')
        self.element = None
        self.user = user
        self.shop = shop
        self.product_list = product_list
        self.prize_list = prize_list
        self.shopping_cart = None

    def show(self) -> Any:
        with st.container(border=True) as container:
            tab1, tab2, tab3 = st.tabs(["User and shop", "Products", "Prizes"])
            with tab1:
                st.write(f'User: {self.user.username}')
                st.write(f'Shop: {self.shop.name}')
            with tab2:
                products = self.product_list.show()
            with tab3:
                prizes = self.prize_list.show()
            create_tr = st.button("Submit")
            if create_tr:
                self.shopping_cart = [pr["url"] for pr in products.selected_rows]+[pr['url'] for pr in prizes.selected_rows]
                self.element = TransactionDetail(
                    user=self.user.url,
                    shop=self.shop.url,
                    shopping_cart=self.shopping_cart
                ).create_or_update()
