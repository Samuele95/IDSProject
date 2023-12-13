from __future__ import annotations
from dataclasses import dataclass, field
from plclient.utils.settings import shops_endpoint
from plclient.api.apiclient import APIClientDetail, APIClientList
import streamlit as st
import requests


@dataclass(frozen=True, eq=True, order=True)
class ShopDetail(APIClientDetail):
    api_endpoint: str = field(default=shops_endpoint)
    error: str | None = None
    url: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    owner: str | None = None
    employees: list | None = None

    def create_or_update(self, update_is_patch: bool = False) -> ShopDetail:
        try:
            data = {'name': self.name}
            if self.email is not None:
                data['email'] = self.email
            if self.phone is not None:
                data['phone'] = self.phone
            if self.location is not None:
                data['location'] = self.location
            if self.owner is not None:
                data['owner'] = self.owner
            if self.employees is not None:
                data['employees'] = self.employees
            if not self.url:
                response = requests.post(self.api_endpoint, data=data)
            elif update_is_patch:
                response = requests.patch(self.url, data=data)
            else:
                response = requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('Shop created successfully!')
            return self
        except requests.HTTPError as ex:
            st.error('Some error occurred during shop creation or update')
            return ShopDetail(error=str(ex))

    def as_dict(self) -> dict:
        if self.error is not None:
            return {'error': self.error}
        return {
            'url': self.url,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'owner': self.owner,
            'employees': self.employees
        }


@dataclass(frozen=True, eq=True, order=True)
class ShopList(APIClientList):
    api_endpoint: str = field(default=shops_endpoint)
    error: str | None = None
    data: list | None = None
    datainstance: type['APIClientDetail'] | None = None
