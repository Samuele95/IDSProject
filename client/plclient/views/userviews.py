from __future__ import annotations
from typing import Protocol, runtime_checkable
from dataclasses import dataclass

from plclient.forms.forms import Table
from plclient.utils.settings import users_endpoint
from plclient.forms.userforms import UserForm, UserCreateForm, UserSetPasswordForm
from plclient.api.userapi import UserDetail, UserList
from plclient.api.shopapi import ShopDetail
import streamlit as st
import requests


@runtime_checkable
class UserView(Protocol):

    def open_view(self):
        ...

    def close_view(self):
        ...

    def get_user(self, username: str):
        ...

    def get_self_user(self):
        ...

    def user_create_form(self):
        ...

    def get_all_users(self):
        ...

class NoUserView:

    def open_view(self):
        return self.user_create_form()

    def close_view(self):
        raise NotImplementedError

    def get_user(self, username: str):
        return UserForm(UserDetail(url=users_endpoint + username).get())

    def user_create_form(self):
        return UserCreateForm()

    def get_all_users(self):
        return Table(
            element=UserList(),
            columns=['url', 'username', 'email', 'phone'],
            hidden_columns=['url']
        )


@dataclass(frozen=True, eq=True, order=True)
class GenericUserView(NoUserView):
    user: UserDetail

    def open_view(self):
        home_col1, home_col2 = st.columns(2)
        with home_col1:
            user_profile, change_password = st.tabs(['User profile', 'Change password'])
            with user_profile:
                self.get_self_user().show()
            with change_password:
                UserSetPasswordForm(self.user).show()
        with home_col2:
            st.markdown("Welcome to Project Loyalty Platfom.\nThis platform aims to provide a common hub in which "
                        "commercial businesses present themselves to the public and communicate with each other and "
                        "with the customers themselves.\nCommercial establishments can join together in common "
                        "loyalty programmes, channels constituting a way through which a customer is able to obtain "
                        "economic advantages and rewards thanks to the loyalty towards the commercial establishment "
                        "or the consortium of companies participating in the program itself, while commercial "
                        "businesses can adopt strategies aimed at retaining existing customers and obtaining new "
                        "ones.\nFor further clarification and for additional information, send an email to "
                        "projectloyalty@gmail.com")


    def get_self_user(self):
        return UserForm(self.user)


