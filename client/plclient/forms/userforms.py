from __future__ import annotations
from typing import Any

from streamlit_extras.switch_page_button import switch_page

from plclient.forms.forms import Form
from plclient.api.userapi import UserDetail
import streamlit as st


class UserForm(Form):
    element: UserDetail

    def __init__(self, element: UserDetail, read_only: bool = True) -> None:
        if element.url is None:
            raise ValueError('No user available')
        self.element = element
        self.read_only = read_only
        self.username = None
        self.email = None
        self.location = None
        self.bio = None

    def show(self) -> Any:
        container = st.container()
        self.username = container.text_input(
            label="Username",
            value=self.element.username,
            placeholder="enter your username",
            disabled=True,
        )
        self.email = container.text_input(
            label="Email address",
            value=self.element.email,
            placeholder="enter your email address",
            disabled=self.read_only,
        )
        self.location = container.text_input(
            label="Location",
            value=self.element.location,
            placeholder="enter your location",
            disabled=self.read_only,
        )
        self.bio = container.text_area(
            label="Bio",
            value=self.element.bio,
            placeholder="enter a small description",
            disabled=self.read_only,
        )
        return container


class UserUpdateForm:

    def __init__(self, decorated: UserForm) -> None:
        if decorated.read_only:
            decorated.read_only = False
        self.decorated = decorated

    def show(self) -> Any:
        container = self.decorated.show()
        button = container.button('Update')
        if button:
            UserDetail(
                url=self.decorated.element.url,
                username=self.decorated.location,
                password=self.decorated.element.password,
                email=self.decorated.email,
                location=self.decorated.location,
                bio=self.decorated.bio,
            ).create_or_update()


class UserCreateForm(Form):
    element: UserDetail | None

    def __init__(self) -> None:
        self.element = None
        self.username = None
        self.password = None
        self.confirm_password = None
        self.email = None
        self.phone_number = None

    def show(self) -> Any:
        with st.form("User create"):
            self.username = st.text_input(
                label="Username",
                placeholder="enter your username",
            )
            self.email = st.text_input(
                label="Email address",
                placeholder="enter your email address",
            )
            self.password = st.text_input(
                label="New password",
                placeholder="enter yout new password",
                type="password",
            )
            self.confirm_password = st.text_input(
                label="Confirm password",
                placeholder="enter password again",
                type="password",
            )
            self.phone_number = st.text_input(
                label="Phone number",
                placeholder="enter your phone number",
            )
            update_button = st.form_submit_button("Create")
            if update_button:
                self.element = UserDetail(
                    username=self.username,
                    password=self.password,
                    confirm_password=self.confirm_password,
                    email=self.email,
                    phone=self.phone_number
                ).create_or_update()


class UserSetPasswordForm(Form):
    element: UserDetail

    def __init__(self, element: UserDetail) -> None:
        if element.url is None:
            raise ValueError('No user available')
        self.element = element
        self.password = None
        self.confirm_password = None

    def show(self) -> Any:
        with st.form("User password update"):
            self.password = st.text_input(
                label="New password",
                placeholder="enter yout new password",
                type="password",
            )
            self.confirm_password = st.text_input(
                label="Confirm password",
                placeholder="enter password again",
                type="password",
            )
            update_button = st.form_submit_button("Change password")
            if update_button:
                UserDetail(
                    api_endpoint=self.element.api_endpoint,
                    url=self.element.url,
                    username=self.element.username,
                    password=self.password,
                    confirm_password=self.confirm_password,
                ).create_or_update()


class LoginForm(Form):
    element: UserDetail | None

    def __init__(self) -> None:
        self.element = None
        self.username = None
        self.password = None
        self.token = None
        self.user_url = None

    def show(self) -> LoginForm:
        with st.form('Login form'):
            username = st.text_input(
                label='Username',
                placeholder='enter username',
            )
            password = st.text_input(
                label='Password',
                placeholder='enter password',
                type='password',
            )
            submitted = st.form_submit_button('Login')
            if submitted:
                result = UserDetail(username=username, password=password).authenticate()
                if 'error' in result:
                    st.error(result['error'])
                else:
                    self.token = result['token']
                    self.user_url = result['url']
        return self
