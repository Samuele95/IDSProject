from __future__ import annotations

from abc import ABC
from typing import Protocol, runtime_checkable
from dataclasses import dataclass

from plclient.api.catalogueapi import CatalogueDetail, CatalogueList
from plclient.api.fidelityprogramapi import FidelityProgramDetail
from plclient.api.userapi import UserDetail
from plclient.forms.catalogueforms import CatalogueUpdateForm, CatalogueForm, CatalogueCreateForm
from plclient.forms.forms import Table
from plclient.utils.settings import catalogue_endpoint


@runtime_checkable
class CatalogueView(Protocol):

    def open_view(self):
        ...

    def close_view(self):
        ...

    # def create_catalogue_element(self, programurl: str):
    #    ...

    def get_catalogue_element(self, username: str, programname: str):
        ...

    def delete_catalogue_element(self, username: str, programname: str):
        ...

    def update_catalogue_element(self, username: str, programname: str):
        ...

    def get_all_catalogue_elements(self):
        ...

    # def get_all_catalogue_elements_by_user(self, username: str):
    #    ...

    # def get_all_catalogue_elements_by_fidelity_program(self, programname: str):
    #    ...


class GenericCatalogueView(ABC):
    def get_catalogue_element(self, username: str, programname: str):
        return CatalogueForm(CatalogueDetail(api_endpoint=catalogue_endpoint + username + '/' + programname).get())

    def delete_catalogue_element(self, username: str, programname: str):
        return self.get_catalogue_element(username, programname).element.delete()

    def update_catalogue_element(self, username: str, programname: str):
        return CatalogueUpdateForm(self.get_catalogue_element(username, programname))

    def get_all_catalogue_elements(self):
        return Table(element=CatalogueList(), columns=['url', 'customer', 'fidelity_program'], hidden_columns=['url'])


class UserCatalogueView:
    user: UserDetail

    def __init__(self, user: UserDetail):
        if user.url is None or user.username is None:
            raise ValueError('User data is required')
        self.user = user

    def create_catalogue_element(self, programurl: str):
        return CatalogueCreateForm(
            fidelity_program=FidelityProgramDetail(url=programurl).get(),
            user_data=self.user
        )

    def get_all_catalogue_elements_by_user(self):
        return Table(element=CatalogueList(api_endpoint=catalogue_endpoint + 'byuser/' + self.userusername),
                     columns=['url', 'customer', 'fidelity_program'], hidden_columns=['url'])

    def get_all_catalogue_elements_by_fidelity_program(self, programname: str):
        return Table(element=CatalogueList(api_endpoint=catalogue_endpoint + 'byprogram/' + programname),
                     columns=['url', 'customer', 'fidelity_program'], hidden_columns=['url'])


class FidelityProgramCatalogueView:
    user: UserDetail

    def __init__(self, program: FidelityProgramDetail):
        if program.url is None or program.name is None:
            raise ValueError('Fidelity Program data is required')
        self.program = program

    def create_catalogue_element(self, user: UserDetail):
        if user.url is None or user.username is None:
            raise ValueError('User data is required')
        return CatalogueCreateForm(
            fidelity_program=self.program,
            user_data=user
        )

    def get_all_catalogue_elements_by_fidelity_program(self):
        return Table(element=CatalogueList(api_endpoint=catalogue_endpoint + 'byprogram/' + self.program.name),
                     columns=['url', 'customer', 'fidelity_program'], hidden_columns=['url'])
