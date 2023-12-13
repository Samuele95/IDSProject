from __future__ import annotations
from dataclasses import dataclass, field
from plclient.utils.settings import product_endpoint
from plclient.api.apiclient import APIClientDetail, APIClientList
import streamlit as st
import requests


@dataclass(frozen=True, eq=True, order=True)
class ProductDetail(APIClientDetail):
    api_endpoint: str = field(default=product_endpoint)
    error: str | None = None
    url: str | None = None
    id: int | None = None
    name: str | None = None
    value: float | None = None
    points_coefficient: float = None
    prize_coefficient: float | None = None
    is_persistent: bool | None = None
    shop: str | None = None
    fidelity_program: str = None
    owning_users: list[str] | None = None

    def create_or_update(self, update_is_patch: bool = False) -> ProductDetail:
        try:
            data = {}
            if self.name is not None:
                data['name'] = self.name
            if self.value is not None:
                data['value'] = self.value
            if self.points_coefficient is not None:
                data['points_coefficient'] = self.points_coefficient
            if self.prize_coefficient is not None:
                data['prize_coefficient'] = self.prize_coefficient
            if self.is_persistent is not None:
                data['is_persistent'] = self.is_persistent
            if self.shop is not None:
                data['shop'] = self.shop
            if self.fidelity_program is not None:
                data['fidelity_program'] = self.fidelity_program
            if self.owning_users is not None:
                data['owning_users'] = self.owning_users
            if not self.url:
                response = requests.post(self.api_endpoint, data=data)
            elif update_is_patch:
                response = requests.patch(self.url, data=data)
            else:
                response = requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('Product element stored successfully!')
            return self
        except requests.HTTPError as ex:
            st.error('Some error occurred during product creation or update')
            return ProductDetail(error=str(ex))

    def as_dict(self) -> dict:
        if self.error is not None:
            return {'error': self.error}
        return {
            'url': self.url,
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'points_coefficient': self.points_coefficient,
            'prize_coefficient': self.prize_coefficient,
            'is_persistent': self.is_persistent,
            'shop': self.shop,
            'fidelity_program': self.fidelity_program,
            'owning_users': self.owning_users
        }


@dataclass(frozen=True, eq=True, order=True)
class ProductList(APIClientList):
    api_endpoint: str = field(default=product_endpoint)
    error: str | None = None
    data: list | None = None
    datainstance: type['APIClientDetail'] | None = None
