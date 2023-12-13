from __future__ import annotations
from dataclasses import dataclass, field
from plclient.utils.settings import catalogue_endpoint
from plclient.api.apiclient import APIClientDetail, APIClientList
import streamlit as st
import requests


@dataclass(frozen=True, eq=True, order=True)
class CatalogueDetail(APIClientDetail):
    api_endpoint: str = field(default=catalogue_endpoint)
    error: str | None = None
    url: str | None = None
    id: int | None = None
    points: float | None = None
    customer: str | None = None
    fidelity_program: str | None = None

    def create_or_update(self, update_is_patch: bool = False) -> CatalogueDetail:
        try:
            data = {}
            if self.customer is not None:
                data['customer'] = self.customer
            if self.fidelity_program is not None:
                data['fidelity_program'] = self.fidelity_program
            if self.points is not None:
                data['points'] = self.points
            if not self.url:
                response = requests.post(self.api_endpoint, data=data)
            elif update_is_patch:
                response = requests.patch(self.url, data=data)
            else:
                response = requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('Catalogue element stored successfully!')
            return self
        except requests.HTTPError as ex:
            st.error('Some error occurred during catalogue element creation or update')
            return CatalogueDetail(error=str(ex))

    def as_dict(self) -> dict:
        if self.error is not None:
            return {'error': self.error}
        return {
            'url': self.url,
            'id': self.id,
            'points': self.points,
            'customer': self.customer,
            'fidelity_program': self.fidelity_program
        }


@dataclass(frozen=True, eq=True, order=True)
class CatalogueList(APIClientList):
    api_endpoint: str = field(default=catalogue_endpoint)
    error: str | None = None
    data: list | None = None
    datainstance: type['APIClientDetail'] | None = None
