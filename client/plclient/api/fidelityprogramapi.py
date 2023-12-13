from __future__ import annotations
from dataclasses import dataclass, field
from plclient.utils.settings import fidelity_programs_endpoint, cashback_endpoint, points_endpoint, levels_endpoint, \
    membership_endpoint
from plclient.api.apiclient import APIClientDetail, APIClientList
import streamlit as st
import requests


@dataclass(eq=True, order=True)
class FidelityProgramDetail(APIClientDetail):
    api_endpoint: str = field(default=fidelity_programs_endpoint)
    error: str | None = None
    url: str | None = None
    name: str | None = None
    program_type: str | None = None
    points_coefficient: float | None = None
    prize_coefficient: float | None = None
    description: str | None = None
    shop_list: list[str] | None = None

    def create_or_update(self, update_is_patch: bool = False) -> FidelityProgramDetail:
        try:
            data = {}
            if self.name is not None:
                data['name'] = self.name
            if self.program_type is not None:
                data['program_type'] = self.program_type
                match self.program_type:
                    case 'CASHBACK':
                        self.api_endpoint = cashback_endpoint
                    case 'POINTS':
                        self.api_endpoint = points_endpoint
                    case 'LEVELS':
                        self.api_endpoint = levels_endpoint
                    case 'MEMBERSHIP':
                        self.api_endpoint = membership_endpoint
            if self.description is not None:
                data['description'] = self.description
            if self.points_coefficient is not None:
                data['points_coefficient'] = self.points_coefficient
            if self.prize_coefficient is not None:
                data['prize_coefficient'] = self.prize_coefficient
            if self.shop_list is not None:
                data['shop_list'] = self.shop_list
            if not self.url:
                response = requests.post(self.api_endpoint, data=data)
            elif update_is_patch:
                response = requests.patch(self.url, data=data)
            else:
                response = requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('Fidelity program stored successfully!')
            return self
        except requests.HTTPError as ex:
            st.error('Some error occurred during fidelity program creation or update')
            return FidelityProgramDetail(error=str(ex))

    def as_dict(self) -> dict:
        if self.error is not None:
            return {'error': self.error}
        return {
            'url': self.url,
            'name': self.name,
            'program_type': self.program_type,
            'points_coefficient': self.points_coefficient,
            'prize_coefficient': self.prize_coefficient,
            'description': self.description,
            'shop_list': self.shop_list
        }


@dataclass(frozen=True, eq=True, order=True)
class FidelityProgramList(APIClientList):
    api_endpoint: str = field(default=fidelity_programs_endpoint)
    error: str | None = None
    data: list | None = None
    datainstance: type['APIClientDetail'] | None = None
