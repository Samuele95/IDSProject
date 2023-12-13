from typing import Any
from plclient.forms.forms import Form, Table
from plclient.api.catalogueapi import CatalogueDetail
from plclient.api.fidelityprogramapi import FidelityProgramDetail
from plclient.api.userapi import UserDetail
import streamlit as st


class CatalogueForm(Form):
    element: CatalogueDetail

    def __init__(self, element: CatalogueDetail) -> None:
        if element.url is None or element.id is None:
            raise ValueError('No catalogue element available')
        self.element = element
        self.username = None
        self.fidelity_program = None
        self.points = None

    def show(self) -> Any:
        container = st.container()
        self.username = container.text_input(
            label="User",
            value=UserDetail(url=self.element.customer).get().username,
            placeholder="enter your username",
            disabled=True,
            key=str(self.element) + "1",
        )
        self.fidelity_program = container.text_input(
            label="Fidelity Program",
            value=FidelityProgramDetail(url=self.element.fidelity_program).get().name,
            placeholder="enter your email address",
            disabled=True,
            key=str(self.element) + "2",
        )
        self.points = container.write(f"Points: {self.element.points}")
        return container


class CatalogueCreateForm(Form):
    element: CatalogueDetail | None

    def __init__(self, fidelity_program: FidelityProgramDetail, user_data: UserDetail | Table) -> None:
        if fidelity_program.url is None or fidelity_program.name is None:
            raise ValueError('Catalogue element must be bound to a fidelity program')
        if isinstance(user_data, UserDetail) and (user_data.url is None or user_data.username is None):
            raise ValueError('Catalogue element must be bount to a user')
        self.element = None
        self.fidelity_program = fidelity_program
        self.user_data = user_data

    def show(self) -> Any:
        with st.container() as container:
            if not isinstance(self.user_data, UserDetail):
                st.caption('Select user')
                users = self.user_data.show()
                selected_user = users.selected_rows[0]["url"] if len(users.selected_rows) > 0 else None
            create_button = st.button("Create catalogue element")
            if create_button:
                if isinstance(self.user_data, UserDetail):
                    self.element = CatalogueDetail(
                        customer=self.user_data.url,
                        fidelity_program=self.fidelity_program.url,
                    ).create_or_update()
                elif selected_user is not None:
                    self.element = CatalogueDetail(
                        customer=selected_user,
                        fidelity_program=self.fidelity_program.url,
                    ).create_or_update()


class CatalogueUpdateForm(Form):
    element: CatalogueDetail | None = None

    def __init__(self, decorated: CatalogueForm) -> None:
        self.decorated = decorated
        self.element = None

    def show(self) -> Any:
        container = self.decorated.show()
        new_pts = container.text_input(label="New points", key=str(self.decorated))
        update_button = st.button("Update catalogue element")
        if update_button:
            points_number = float(new_pts)
            self.element = CatalogueDetail(
                url=self.decorated.element.url,
                customer=self.decorated.element.customer,
                fidelity_program=self.decorated.element.fidelity_program,
                points=points_number if points_number >= 0 else 0.0,
            ).create_or_update()
