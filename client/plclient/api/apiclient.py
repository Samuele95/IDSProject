from __future__ import annotations
import streamlit as st
import requests
from typing import Protocol, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class APIClient(Protocol):
    """
    Abstract class representing a client interacting 
    with a remote resource, located through a url endpoint, 
    by consumption of an API made available 
    by the application backend.
    """
    api_endpoint: str
    error: str | None

    def get(self):
        ...


class APIClientList(ABC):
    """
    Abstract class representing a particular type of APIClient 
    where the resource to interact with is a collection or 
    series of model data elements stored in the underlying 
    system database.
    """

    api_endpoint: str
    error: str | None = None
    data: list | None = None
    datainstance: type['APIClientDetail'] | None = None

    def get(self):
        if self.data is not None and self.datainstance is not None:
            return list(
                map(lambda x: self.datainstance(api_endpoint=self.api_endpoint, url=x).get().as_dict(), self.data))
        if self.data is not None:
            return self.data
        result = requests.get(self.api_endpoint).json()
        return result if 'results' not in result else result['results']


class APIClientDetail(ABC):
    """
    Abstract class representing a particular type of APIClient 
    where the resource to interact with is a single instance 
    of model data stored in the underlying system database.
    """
    api_endpoint: str
    error: str | None = None
    url: str | None = None

    def get(self) -> APIClientDetail:
        try:
            if not self.url:
                return type(self)(self.api_endpoint, error='No resource to obtain')
            response = requests.get(self.url)
            response.raise_for_status()
            return type(self)(self.api_endpoint, error=None, **response.json())
        except requests.HTTPError as ex:
            return type(self)(api_endpoint=self.api_endpoint, error=str(ex))

    def delete(self) -> None:
        try:
            if not self.url:
                return st.error('No resource to delete')
            response = requests.delete(self.url)
            response.raise_for_status()
            st.success('Element correctly deleted')
        except requests.HTTPError as ex:
            return st.error(str(ex))

    @abstractmethod
    def create_or_update(self, update_is_patch: bool = False) -> APIClientDetail:
        pass

    @abstractmethod
    def as_dict(self) -> dict:
        pass





