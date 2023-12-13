from __future__ import annotations
from dataclasses import dataclass, field
from plclient.api.apiclient import APIClientDetail, APIClientList
from plclient.utils.hashers import hash_password
from plclient.utils.settings import users_endpoint, auth_endpoint
import streamlit as st
import requests


@dataclass(eq=True, order=True)
class UserDetail(APIClientDetail):
    api_endpoint: str = field(default=users_endpoint)
    error: str | None = None
    url: str | None = None
    username: str | None = None
    password: str | None = None
    confirm_password: str | None = None
    email: str | None = None
    phone: str | None = None
    groups: list | None = None
    avatar: str | None = None
    bio: str | None = None
    location: str | None = None

    def create_or_update(self, update_is_patch: bool = False) -> UserDetail:
        try:
            data = {'username': self.username, 'password': self.password}
            if self.confirm_password is not None:
                if self.password != self.confirm_password:
                    return st.error('Passwords are not equal! Try again')
                data['password'] = hash_password(self.password)
            if self.email is not None:
                data['email'] = self.email
            if self.phone is not None:
                data['phone'] = self.phone
            if self.location is not None:
                data['location'] = self.location
            if self.bio is not None:
                data['bio'] = self.bio
            if not self.url:
                response = requests.post(self.api_endpoint, data=data)
            elif update_is_patch:
                response = requests.patch(self.url, data=data)
            else:
                response = requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('User stored successfully!')
            return self
        except requests.HTTPError as ex:
            st.error('Some error occurred during user creation or update')
            return UserDetail(error=str(ex))

    def authenticate(self) -> dict:
        try:
            response = requests.post(auth_endpoint, data={'username': self.username, 'password': self.password})
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as ex:
            st.error('Could not login. Try again')
            return {'error': response.json()['non_field_errors'].pop()}

    def as_dict(self) -> dict:
        if self.error is not None:
            return {'error': self.error}
        return {
            'url': self.url,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'phone': self.phone,
            'groups': self.groups,
            'avatar': self.avatar,
            'bio': self.bio,
            'location': self.location
        }


@dataclass(frozen=True, eq=True, order=True)
class UserList(APIClientList):
    api_endpoint: str = field(default=users_endpoint)
    error: str | None = None
    data: list | None = None
    datainstance: type['APIClientDetail'] | None = None
