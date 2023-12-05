import streamlit as st
import pandas as pd
import requests
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from plclient.utils.hashers import hash_password
from plclient.utils.settings import users_endpoint, shops_endpoint, fidelity_programs_endpoint, catalogue_endpoint


@runtime_checkable
class APIClient(Protocol):
    """
    Abstract class representing a client interacting 
    with a remote resource, located through a url endpoint, 
    by consumption of an API made available 
    by the application backend.
    """
    api_endpoint : str

    def get(self):
        ...
    


class APIClientList(ABC):
    """
    Abstract class representing a particular type of APIClient 
    where the resource to interact with is a collection or 
    series of model data elements stored in the underlying 
    system database.
    """

    api_endpoint : str
    data : list | None = None
    datainstance : type['APIClientDetail'] | None = None

    def get(self):
        if (self.data is not None and self.datainstance is not None):
            return list(map(lambda x : self.datainstance(api_endpoint=self.api_endpoint, url=x).get().as_dict(), self.data))
        if self.data is not None:
            return self.data
        return requests.get(self.api_endpoint).json()['results']
    


class APIClientDetail(ABC):
    """
    Abstract class representing a particular type of APIClient 
    where the resource to interact with is a single instance 
    of model data stored in the underlying system database.
    """
    api_endpoint : str
    url : str = None

    def get(self):
        try:
            if not self.url:
                return 'No resource to obtain' 
            response = requests.get(self.url)
            response.raise_for_status()
            return type(self)(self.api_endpoint, **response.json())
        except requests.HTTPError as ex:
            return st.error(str(ex))

    def delete(self):
        try:
            if not self.url:
                return 'No resource to delete' 
            return requests.delete(self.url).raise_for_status()
        except requests.HTTPError as ex:
            return st.error(str(ex)) 
    
 
    @abstractmethod
    def create_or_update(self):
        pass
    
    @abstractmethod
    def as_dict(self) -> dict:
        pass




@dataclass(eq=True, order=True)
class UserDetail(APIClientDetail):
    api_endpoint : str = field(default=users_endpoint)
    url : str = None
    username : str = None
    password : str = None
    confirm_password: str = None
    email : str = None
    phone : str = None
    groups : list = None
    avatar : str = None
    bio : str = None
    location : str = None


    def create_or_update(self):
        try:
            data = {'username': self.username, 'password': self.password}
            if self.confirm_password is not None:
                if self.password != self.confirm_password:
                    return st.error('Passwords are not equal! Try again')
                data['password'] = hash_password(self.password)
            if self.email is not None:
                data['email'] = self.email
            if self.location is not None:
                data['location'] = self.location
            if self.bio is not None:
                data['bio'] = self.bio
            response = requests.post(self.api_endpoint, data=data) if not self.url else requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('User stored successfully!')
            return self
        except requests.HTTPError as ex:
            return st.error(str(ex))
    
    def as_dict(self) -> dict:
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
class ShopDetail(APIClientDetail):
    api_endpoint : str = field(default=shops_endpoint)
    url : str | None = None
    name : str | None = None 
    email : str | None = None 
    phone : str | None = None 
    location : str | None = None 
    owner : str | None = None 
    employees : list | None = None


    def create_or_update(self):
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
            response = requests.post(self.api_endpoint, data=data) if not self.url else requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('User stored successfully!')
            return self
        except requests.HTTPError as ex:
            return st.error(str(ex))
        
    def as_dict(self) -> dict:
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
class FidelityProgramDetail(APIClientDetail):
    api_endpoint : str = field(default=fidelity_programs_endpoint)
    url : str = None
    name : str = None 
    program_type : str = None 
    points_coefficient : float = None
    prize_coefficient : float = None
    description : str = None 
    shop_list: list[str] = None

    def create_or_update(self):
        try:
            data = {}
            if self.name is not None:
                data['name'] = self.name
            if self.program_type is not None:
                data['program_type'] = self.program_type
            if self.points_coefficient is not None:
                data['points_coefficient'] = self.points_coefficient
            if self.prize_coefficient is not None:
                data['prize_coefficient'] = self.prize_coefficient
            if self.description is not None:
                data['description'] = self.description
            if self.shop_list is not None:
                data['shop_list'] = self.shop_list
            response = requests.post(self.api_endpoint, data=data) if not self.url else requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('Catalogue element stored successfully!')
            return self
        except requests.HTTPError as ex:
            return st.error(str(ex))
    
    def as_dict(self) -> dict:
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
class CatalogueDetail(APIClientDetail):
    api_endpoint : str = field(default=catalogue_endpoint)
    url : str = None
    id : int = None
    points : float = None
    customer : str = None
    fidelity_program : str = None

    def create_or_update(self):
        try:
            data = {}
            if self.customer is not None:
                data['customer'] = self.customer
            if self.fidelity_program is not None:
                data['fidelity_program'] = self.fidelity_program
            if self.points is not None:
                data['points'] = self.points
            response = requests.post(self.api_endpoint, data=data) if not self.url else requests.put(self.url, data=data)
            response.raise_for_status()
            st.success('Catalogue element stored successfully!')
            return self
        except requests.HTTPError as ex:
            return st.error(str(ex))

    def as_dict(self) -> dict:
        return {
            'url': self.url,
            'id': self.id,
            'points': self.points,
            'customer': self.customer,
            'fidelity_program': self.fidelity_program
        }

@dataclass(frozen=True, eq=True, order=True)
class UserList(APIClientList):
    api_endpoint : str = field(default=users_endpoint)
    data : list | None = None
    datainstance : type['APIClientDetail'] | None = None

@dataclass(frozen=True, eq=True, order=True)
class ShopList(APIClientList):
    api_endpoint : str = field(default=shops_endpoint)
    data : list | None = None
    datainstance : type['APIClientDetail'] | None = None

@dataclass(frozen=True, eq=True, order=True)
class FidelityProgramList(APIClientList):
    api_endpoint : str = field(default=fidelity_programs_endpoint)
    data : list | None = None
    datainstance : type['APIClientDetail'] | None = None

@dataclass(frozen=True, eq=True, order=True)
class CatalogueList(APIClientList):
    api_endpoint : str = field(default=catalogue_endpoint)
    data : list | None = None
    datainstance : type['APIClientDetail'] | None = None