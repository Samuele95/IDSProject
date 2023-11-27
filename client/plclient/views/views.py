import streamlit as st
import pandas as pd
import requests
import random
import string
from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_option_menu import option_menu
from plclient.utils.hashers import hash_password
from plclient.utils.settings import users_endpoint, shops_endpoint, split_frame
from plclient.utils.apiclient import UserDetail, ShopDetail, ShopList

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

class ClientView(ABC):
    """
    View instance which makes use of an underlying APIClient to 
    retrieve from and send information to a backend, where this 
    information is prompted by the user.
    """

    url : str
    username : str
    shopname : str = None

    @abstractmethod
    def open_view(self):
        pass

    @abstractmethod
    def close_view(self):
        pass

    def get_shop(self, shopname: str):
        return ShopDetail(api_endpoint=shops_endpoint, url=shops_endpoint+shopname).get()
    
    def get_user(self, username: str):
        return UserDetail(api_endpoint=users_endpoint, url=users_endpoint+username).get()
    
    def get_self_user(self):
        return self.get_user(self.username)
    
    def get_session_shop(self):
        if self.shopname:
            return self.get_shop(self.shopname)
    
    def get_shop_list(self):
        return ShopList(api_endpoint=shops_endpoint).as_table(table_cols=['url','name', 'location'], column_config={'url':None})
    
    def user_create_form(self):
        return UserDetail(api_endpoint=users_endpoint).as_form()
    

@dataclass(frozen=True, eq=True, order=True)
class UserDashboard(ClientView):
    """
    ClientView instance of a user which doesn't have 
    administrative privileges. It may be associated 
    to both a customer and a business user.
    """

    url : str
    username : str

    def open_view(self):
        st.title('Project Loyalty Platform')
        self.sideBar()
    
    def close_view(self):
        st.write('LOGOUT')

    def home(self):
        user_profile, change_password = st.tabs(['User profile', 'Change password'])
        user = self.get_self_user()
        if user:
            with user_profile:
                user.as_form()
            with change_password:
                user.as_password_update_form()      

    def sideBar(self): 
        with st.sidebar as sidebar:
            selected=option_menu(
                menu_title="Main Menu",
                options=['Home', 'Shops', 'Logout'],
                icons=['house', 'cart', 'dash-circle'],
                menu_icon="cast",
                default_index=0
            )
        if selected=="Home":
            home_col1, home_col2 = st.columns(2)
            with home_col1:
                self.home()
            with home_col2:
                st.markdown("Welcome to Project Loyalty Platfom.\nThis application helps customers and companies in tightning each others' bonds and in finding the best opportunities.\n Personal data is treated according to EU policies.\n For further clarification and for additional information, send an email to projectloyalty@gmail.com")
        if selected=='Shops':
            all_shops, selected_shop = st.columns(2)
            with all_shops:
                shops = self.get_shop_list()
            with selected_shop:
                if shops and shops.size != 0:
                    st.write(self.get_shop(shops.iloc[0].to_dict()['name']).as_form())
        if selected=='Logout':
            self.close_view()