from __future__ import annotations
from typing import Protocol, runtime_checkable
from dataclasses import dataclass

from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu

from plclient.api.shopapi import ShopList
from plclient.api.userapi import UserDetail
from plclient.forms.forms import Table
from plclient.forms.userforms import UserCreateForm, LoginForm
from plclient.utils.settings import users_endpoint, shops_endpoint, fidelity_programs_endpoint, catalogue_endpoint
from plclient.views.userviews import GenericUserView
from plclient.views.shopviews import CustomerShopView, CashierShopView
from plclient.views.fidelityprogramviews import ReadOnlyFidelityProgramView, CashierFidelityProgramView, \
    BusinessOwnerFidelityProgramView
from plclient.views.transactionviews import CustomerTransactionView, CashierTransactionView
import streamlit as st
import requests
import os

app_image = os.path.dirname(__file__) + '/plplatform.png'


@runtime_checkable
class View(Protocol):
    """
    Interface representing a UI which the user can interact with.
    At startup, the view is opened through the open_view function, 
    which shows all the available data and info.
    At logout, the view is closed through the close_view function.
    """

    def open_view(self):
        ...

    def close_view(self):
        ...


@dataclass(frozen=True, eq=True, order=True)
class UserDashboard:
    """
    View instance for the App Dashboard shown
    to a customer.
    """

    user_view: GenericUserView
    shop_view: CustomerShopView
    fidelity_program_view: ReadOnlyFidelityProgramView
    transaction_view: CustomerTransactionView

    def open_view(self):
        st.title('Project Loyalty Platform')
        st.subheader('Customer dashboard')
        self.sideBar()

    def close_view(self):
        st.session_state['token'] = None
        st.session_state['user_url'] = None
        st.session_state['user_url'] = None
        switch_page('main')

    def home(self):
        return self.user_view.open_view()

    def sideBar(self):
        st.sidebar.image(app_image, caption="Developed and Maintaned by Samuele95")
        with st.sidebar as sidebar:
            selected = option_menu(
                menu_title="Main Menu",
                options=['Home', 'Shops', 'Fidelity Programs', 'Orders', 'Logout'],
                icons=['house', 'shop', 'people', 'cart', 'dash-circle'],
                menu_icon="cast",
                default_index=0
            )
        if selected == "Home":
            self.home()
        if selected == 'Shops':
            self.shop_view.open_view()
        if selected == 'Fidelity Programs':
            self.fidelity_program_view.open_view()
        if selected == 'Orders':
            self.transaction_view.open_view()
        if selected == 'Logout':
            self.close_view()


@dataclass(frozen=True, eq=True, order=True)
class CashierDashboard:
    """
    View instance for the App Dashboard shown
    to a cashier.
    """

    user_view: GenericUserView
    shop_view: CashierShopView
    fidelity_program_view: CashierFidelityProgramView
    transaction_view: CashierTransactionView

    # catalogue_view : CatalogueView

    def open_view(self):
        st.title('Project Loyalty Platform')
        st.subheader('Cashier dashboard')
        self.sideBar()

    def close_view(self):
        st.session_state['token'] = None
        st.session_state['user_url'] = None
        st.session_state['shop_url'] = None
        switch_page('main')

    def home(self):
        return self.user_view.open_view()

    def sideBar(self):
        st.sidebar.image(app_image, caption="Developed and Maintaned by Samuele95")
        with st.sidebar as sidebar:
            selected = option_menu(
                menu_title="Main Menu",
                options=['Home', 'Shop', 'Fidelity Programs', 'Orders', 'Logout'],
                icons=['house', 'shop', 'people', 'cart', 'dash-circle'],
                menu_icon="cast",
                default_index=0
            )
        if selected == "Home":
            self.home()
        if selected == 'Shop':
            self.shop_view.open_view()
        if selected == 'Fidelity Programs':
            self.fidelity_program_view.open_view()
        if selected == 'Orders':
            self.transaction_view.open_view()
        if selected == 'Logout':
            self.close_view()


@dataclass(frozen=True, eq=True, order=True)
class BusinessOwnerDashboard:
    """
    View instance for the App Dashboard shown
    to a business owner.
    """

    user_view: GenericUserView
    shop_view: CashierShopView
    fidelity_program_view: BusinessOwnerFidelityProgramView

    def open_view(self):
        st.title('Project Loyalty Platform')
        st.subheader('Business owner dashboard')
        self.sideBar()

    def close_view(self):
        st.session_state['token'] = None
        st.session_state['user_url'] = None
        st.session_state['user_url'] = None
        switch_page('main')

    def home(self):
        if self.shop_view.shop.owner is None or self.shop_view.shop.owner != self.user_view.user.url:
            raise ValueError('You must be the owner of the selected shop')
        return self.user_view.open_view()

    def sideBar(self):
        st.sidebar.image(app_image, caption="Developed and Maintaned by Samuele95")
        with st.sidebar as sidebar:
            selected = option_menu(
                menu_title="Main Menu",
                options=['Home', 'Shop', 'Fidelity Programs', 'Logout'],
                icons=['house', 'shop', 'people', 'dash-circle'],
                menu_icon="cast",
                default_index=0
            )
        if selected == "Home":
            self.home()
        if selected == 'Shop':
            self.shop_view.open_view()
        if selected == 'Fidelity Programs':
            self.fidelity_program_view.open_view()
        if selected == 'Logout':
            self.close_view()

class CustomerLogin:

    def open_view(self):
        login_tab, signup_tab = st.tabs(["Login", "Signup"])
        with login_tab:
            login = LoginForm().show()
            if login.token is not None and login.user_url is not None:
                st.session_state['token'] = login.token
                st.session_state['user_url'] = login.user_url
                switch_page('customerdashboard')
            button = st.button('Back')
            if button:
                self.close_view()
        with signup_tab:
            UserCreateForm().show()

    def close_view(self):
        st.session_state['token'] = None
        st.session_state['user_url'] = None
        st.session_state['user_url'] = None
        switch_page('main')

class CashierLogin:

    def __init__(self, token: str | None = None, user_url: str | None = None, shop_url: str | None = None) -> None:
        self.token = token
        self.user_url = user_url
        self.shop_url = shop_url

    def open_view(self):
        if self.user_url is None:
            st.subheader('Cashier login')
            with st.container(border=True):
                login = LoginForm().show()
                if login.token is not None and login.user_url is not None:
                    st.session_state['token'] = login.token
                    st.session_state['user_url'] = login.user_url
                    switch_page('cashierloginpage')
                button = st.button('Back')
                if button:
                    self.close_view()
        elif self.shop_url is None:
            st.subheader('Please, select a shop')
            with st.container(border=True):
                shops = self.get_all_shops_by_employee().show()
                button = st.button('Login')
                if button and len(shops.selected_rows) > 0:
                    st.session_state['shop_url'] = shops.selected_rows[0]['url']
                    switch_page('cashierloginpage')
                button = st.button('Back')
                if button:
                    self.close_view()
        else:
            switch_page('cashierdashboard')

    def close_view(self):
        st.session_state['token'] = None
        st.session_state['user_url'] = None
        st.session_state['user_url'] = None
        switch_page('main')

    def get_all_shops_by_employee(self):
        if self.user_url is None:
            raise ValueError('Cannot access employee data')
        employee = UserDetail(url=self.user_url).get()
        return Table(
            element= ShopList(api_endpoint=shops_endpoint + 'byemployee/' + employee.username),
            columns=['url', 'name', 'location'],
            hidden_columns=['url']
        )


class BusinessOwnerLogin:

    def __init__(self, token: str | None = None, user_url: str | None = None, shop_url: str | None = None) -> None:
        self.token = token
        self.user_url = user_url
        self.shop_url = shop_url

    def open_view(self):
        if self.user_url is None:
            st.subheader('Business owner login')
            with st.container(border=True):
                login = LoginForm().show()
                if login.token is not None and login.user_url is not None:
                    st.session_state['token'] = login.token
                    st.session_state['user_url'] = login.user_url
                    switch_page('businessownerloginpage')
                button = st.button('Back')
                if button:
                    self.close_view()
        elif self.shop_url is None:
            st.subheader('Please, select a shop')
            with st.container(border=True):
                shops = self.get_all_shops_by_owner().show()
                button = st.button('Login')
                if button and len(shops.selected_rows) > 0:
                    st.session_state['shop_url'] = shops.selected_rows[0]['url']
                    switch_page('businessownerloginpage')
                button = st.button('Back')
                if button:
                    self.close_view()
        else:
            switch_page('businessownerdashboard')

    def close_view(self):
        st.session_state['token'] = None
        st.session_state['user_url'] = None
        st.session_state['user_url'] = None
        switch_page('main')

    def get_all_shops_by_owner(self):
        if self.user_url is None:
            raise ValueError('Cannot access employee data')
        employee = UserDetail(url=self.user_url).get()
        return Table(
            element= ShopList(api_endpoint=shops_endpoint + 'byowner/' + employee.username),
            columns=['url', 'name', 'location'],
            hidden_columns=['url']
        )