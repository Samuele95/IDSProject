from __future__ import annotations
from dataclasses import dataclass, field
from plclient.utils.settings import transaction_endpoint
from plclient.api.apiclient import APIClientDetail, APIClientList
import streamlit as st
import requests


@dataclass(frozen=True, eq=True, order=True)
class TransactionDetail(APIClientDetail):
    api_endpoint: str = field(default=transaction_endpoint)
    error: str | None = None
    url: str | None = None
    id: int | None = None
    executed_at: str | None = None
    user: str | None = None
    shop: str | None = None
    shopping_cart: list[str] | None = None
    total: float | None = None

    def create_or_update(self, update_is_patch: bool = False) -> TransactionDetail:
        try:
            data = {}
            if self.user is not None:
                data['user'] = self.user
            if self.shop is not None:
                data['shop'] = self.shop
            if self.shopping_cart is not None:
                data['shopping_cart'] = self.shopping_cart
            if self.total is not None:
                data['total'] = self.total
            if self.shop is not None:
                data['shop'] = self.shop
            if not self.url:
                response = requests.post(self.api_endpoint, data=data)
            elif update_is_patch:
                response = requests.patch(self.url, data=data)
            else:
                response = requests.put(self.url, data=data)
            response.raise_for_status()
            st.success(f'Order stored successfully! Total price was {response.json()["total"]}')
            return self
        except requests.HTTPError as ex:
            st.error('Some error occurred during transaction creation or update')
            return TransactionDetail(error=str(ex))

    def as_dict(self) -> dict:
        if self.error is not None:
            return {'error': self.error}
        return {
            'url': self.url,
            'id': self.id,
            'executed_at': self.executed_at,
            'user': self.user,
            'shop': self.shop,
            'shopping_cart': self.shopping_cart,
            'total': self.total
        }


@dataclass(frozen=True, eq=True, order=True)
class TransactionList(APIClientList):
    api_endpoint: str = field(default=transaction_endpoint)
    error: str | None = None
    data: list | None = None
    datainstance: type['APIClientDetail'] | None = None
