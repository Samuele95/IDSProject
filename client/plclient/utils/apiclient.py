import streamlit as st
import pandas as pd
import requests
import random
import string
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from streamlit_extras.dataframe_explorer import dataframe_explorer
from plclient.utils.hashers import hash_password
from plclient.utils.settings import users_endpoint, shops_endpoint, split_frame

@runtime_checkable
class APIClient(Protocol):
    """
    Abstract class representing a client interacting 
    with a remote resource, located through a url endpoint, 
    by consumption of an API made available 
    by the application backend.
    """
    api_endpoint : str

    def get(self, is_list = False):
        ...

    def post(self):
        ...

    def put(self):
        ...

    def delete(self):
        ...
    
    

class APIClientList(ABC):
    """
    Abstract class representing a particular type of APIClient 
    where the resource to interact with is a collection or 
    series of model data elements stored in the underlying 
    system database.
    """

    api_endpoint : str

    def get(self, is_list = False):
        return requests.get(self.api_endpoint).json()['results'] if (not is_list) else requests.get(self.url).json()

    @abstractmethod
    def post(self):
        pass

    @abstractmethod
    def put(self):
        pass

    @abstractmethod
    def delete(self):
        pass 

    def as_table(self, table_cols, column_config = None, is_list = False):
        data = self.get(is_list=is_list)
        if len(data) == 0:
            st.text(f'No data registered yet!')
            return 

        filtered_df = dataframe_explorer(pd.DataFrame.from_dict(data)[table_cols], case=False) 
        pagination = st.container()
        pagination.bottom_menu = st.columns((1, 1, 1))
                
        with pagination.bottom_menu[2]:
            batch_size = st.selectbox("Page Size", options=[5, 10, 25, 50, 100], key=random.choices(string.ascii_lowercase, k=5))
        with pagination.bottom_menu[1]:
            total_pages = (
                int(len(filtered_df) / batch_size) if int(len(filtered_df) / batch_size) > 0 else 1
            )
            current_page = st.number_input(
                "Page",
                    min_value=1, 
                    max_value=total_pages, 
                    step=1,
                    key=random.choices(string.ascii_lowercase, k=5)
            )
        with pagination.bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}** ")

        pages = split_frame(filtered_df, batch_size)
        pagination.dataframe(filtered_df, use_container_width=True, column_config=column_config)    
        return filtered_df
        


class APIClientDetail(ABC):
    """
    Abstract class representing a particular type of APIClient 
    where the resource to interact with is a single instance 
    of model data stored in the underlying system database.
    """
    api_endpoint : str
    url : str = None

    def get(self, is_list = False):
        try:
            if not self.url:
                return 'No resource to obtain' 
            response = requests.get(self.url)
            response.raise_for_status()
            return type(self)(self.api_endpoint, **response.json())
        except requests.HTTPError as ex:
            return st.error(str(ex))

    def post(self):
        return self.create_or_update()
    
    def put(self):
        return self.create_or_update()

    def delete(self):
        try:
            if not self.url:
                return 'No resource to delete' 
            return requests.delete(self.url).raise_for_status()
        except requests.HTTPError as ex:
            return st.error(str(ex)) 
    
    @abstractmethod
    def as_form(self):
        pass

    @abstractmethod
    def as_init_form(self):
        pass

    @abstractmethod
    def create_or_update(self, create=True):
        pass

@dataclass(frozen=True, eq=True, order=True)
class UserDetail(APIClientDetail):
    api_endpoint : str
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
    
    def as_form(self):
        with st.form('User profile'):
            username = st.text_input(
                label='Username', 
                value=self.username,
                placeholder='enter your username',
                disabled=True,
            )
            email = st.text_input(
                label='Email address', 
                value=self.email, 
                placeholder='enter your email address',
            )
            location = st.text_input(
                label='Location', 
                value=self.location, 
                placeholder='enter your location',
            )
            bio = st.text_area(
                label='Bio', 
                value=self.bio, 
                placeholder='enter a small description',
            )
            update_button = st.form_submit_button('Update')
            if update_button:
                type(self)(
                    api_endpoint = self.api_endpoint,
                    url=self.url,
                    username=username,
                    password=self.password,
                    email=email,
                    location=location,
                    bio=bio,
                ).put()

    def as_init_form(self):
        with st.form('User profile'):
            username = st.text_input(
                label='Username', 
                value=self.username,
                placeholder='enter your username',
                disabled=True,
            )
            password = st.text_input(
                label='New password',
                placeholder='enter yout new password',
                type='password',
            )
            confirm_password = st.text_input(
                label='Confirm password',
                placeholder='enter password again',
                type='password',
            )
            email = st.text_input(
                label='Email address', 
                value=self.email, 
                placeholder='enter your email address',
            )
            create_button = st.form_submit_button('Update')
            if create_button:
                type(self)(
                api_endpoint = self.api_endpoint,
                username=username,
                password=password,
                confirm_password=confirm_password,
                email=email,
                ).post()        
        
    def as_password_update_form(self):
        with st.form('Signup form'):
            password = st.text_input(
                label='New password',
                placeholder='enter yout new password',
                type='password',
            )
            confirm_password = st.text_input(
                label='Confirm password',
                placeholder='enter password again',
                type='password',
            )
            submitted = st.form_submit_button('Submit')
            if submitted and self.url: 
                type(self)(
                    api_endpoint = self.api_endpoint,
                    url=self.url,
                    username=self.username,
                    password=password,
                    confirm_password=confirm_password,
                ).put()
    
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

@dataclass(frozen=True, eq=True, order=True)
class ShopList(APIClientList):
    api_endpoint : str

    def post(self):
        raise NotImplementedError
    
    def put(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError
    

@dataclass(frozen=True, eq=True, order=True)
class ShopDetail(APIClientDetail):
    api_endpoint : str
    url : str = None
    name : str = None 
    email : str = None 
    phone : str = None 
    location : str = None 
    owner : str = None 
    employees : list = None

    def put(self):
        raise NotImplementedError
    
    def as_form(self):
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Info", "Products", "Reviews", "Contact us", "Owner", "Employees", 'Joined Fidelity Programs'])
        with tab1:
            shop_name = st.text_input(
                label='Shop name', 
                value=self.name,
                placeholder='enter shop name',
                disabled=True,
                key=random.choices(string.ascii_lowercase, k=5)
            )

            shop_location = st.text_area(
                label='Location', 
                value=self.location, 
                placeholder='enter shop location',
                disabled=True,
                key=random.choices(string.ascii_lowercase, k=5)
            )

            
        with tab4:
            with st.expander('Phone'):
                shop_number = st.text_input(
                    label='Phone number', 
                    value=self.phone,
                    placeholder='enter phone number',
                    disabled=True,
                    key=random.choices(string.ascii_lowercase, k=5),
                    label_visibility='collapsed'
                )

        with tab5:
            if self.owner:
                UserDetail(api_endpoint=users_endpoint, url=self.owner).get()
    
    def as_init_form(self):
        with st.form('Shop init profile'):
            name = st.text_input(
                label='Shop name', 
                value=self.name,
                placeholder='enter shop name',
            )
            email = st.text_input(
                label='Email address', 
                value=self.email, 
                placeholder='enter shop email address',
            )
            owner = st.text_input(
                label='Owner username', 
                value= UserDetail(api_endpoint=users_endpoint, url=self.owner).get().owner if self.owner else '',  
                placeholder='enter your location',
            )
            create_button = st.form_submit_button('Create shop')
            if create_button:
                type(self)(
                    api_endpoint = self.api_endpoint,
                    name=name,
                    email=email,
                    owner=shops_endpoint+owner
                ).post()

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
