import string
import random
from typing import Any

from plclient.api.shopapi import ShopDetail
from plclient.forms.forms import Form, Table
from plclient.api.fidelityprogramapi import FidelityProgramDetail
from plclient.api.productapi import ProductDetail
import streamlit as st

from plclient.utils.settings import coefficient_limits


class ProductForm(Form):
    element: ProductDetail

    def __init__(self, element: ProductDetail, read_only: bool = True) -> None:
        self.element = element
        self.read_only = read_only
        self.prod_value = None

    def show(self) -> Any:
        container = st.container(border=True)
        container.caption("Product description")
        container.write(f"Name: {self.element.name}")
        container.write(f"Shop: {self.element.shop}")
        container.divider()
        self.prod_value = container.text_input(
            label="Value",
            value=self.element.value or None,
            placeholder="enter product value",
            disabled=self.read_only,
        )
        return container


class PrizeForm(Form):
    element: ProductDetail

    def __init__(self, decorated: ProductForm) -> None:
        if decorated.element.fidelity_program is None:
            raise ValueError("The product is not a prize!")
        self.decorated = decorated
        self.element = self.decorated.element
        self.is_persistent = None

    def show(self) -> Any:
        container = self.decorated.show()
        self.is_persistent = container.checkbox(
            label='Is a prize which can be redeemed later by customer',
            value=self.element.is_persistent,
            disabled=self.decorated.read_only)
        container.write(
            f"Fidelity program: {FidelityProgramDetail(url=self.element.fidelity_program).get().name}"
        )
        return container


class ProductUpdateForm(Form):
    element: ProductDetail

    def __init__(self, decorated: ProductForm) -> None:
        if decorated.read_only:
            decorated.read_only = False
        self.decorated = decorated
        self.element = self.decorated.element

    def show(self) -> Any:
        container = self.decorated.show()
        button = container.button("Update")
        if button:
            ProductDetail(
                url=self.element.url,
                name=self.element.name,
                shop=self.element.shop,
                value=float(self.decorated.prod_value),
            ).create_or_update()
        return container


class PrizeUpdateForm(Form):
    element: ProductDetail

    def __init__(self, decorated: PrizeForm) -> None:
        if decorated.decorated.read_only:
            decorated.decorated.read_only = False
        self.decorated = decorated
        self.element = self.decorated.element

    def show(self) -> Any:
        container = self.decorated.show()
        fidelity_program = FidelityProgramDetail(
            url=self.element.fidelity_program
        ).get()
        min_lim, max_lim = coefficient_limits(fidelity_program.program_type)
        points_coefficient = container.slider(
            label="Points coefficient",
            min_value=min_lim,
            max_value=max_lim,
            value=self.element.points_coefficient,
            step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
            format="%.4f",
        )
        prize_coefficient = container.slider(
            label="Prize coefficient",
            min_value=min_lim,
            max_value=max_lim,
            value=self.element.prize_coefficient,
            step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
            format="%.4f",
        )
        button = container.button("Update")
        if button:
            ProductDetail(
                url=self.element.url,
                name=self.element.name,
                shop=self.element.shop,
                value=float(self.decorated.decorated.prod_value),
                points_coefficient=points_coefficient,
                prize_coefficient=prize_coefficient,
                is_persistent=self.decorated.is_persistent
            ).create_or_update()
        return container


class ProductDeleteForm(Form):
    element: ProductDetail

    def __init__(self, decorated: ProductUpdateForm) -> None:
        self.decorated = decorated
        self.element = decorated.element

    def show(self) -> Any:
        container = self.decorated.show()
        button = container.button("Delete")
        if button:
            ProductDetail(
                url=self.element.url,
                name=self.element.name,
                shop=self.element.shop,
            ).delete()
        return container


class PrizeDeleteForm(Form):
    element: ProductDetail

    def __init__(self, decorated: PrizeUpdateForm) -> None:
        self.decorated = decorated
        self.element = decorated.element

    def show(self) -> Any:
        container = self.decorated.show()
        button = container.button("Delete")
        if button:
            ProductDetail(
                url=self.element.url,
                name=self.element.name,
                shop=self.element.shop,
            ).delete()
        return container


class ProductCreateForm(Form):
    element: ProductDetail

    def __init__(self, shop: ShopDetail, fidelity_programs_data: FidelityProgramDetail | Table) -> None:
        if shop.url is None or shop.name is None:
            raise ValueError('New product must be associated to a shop')
        self.shop = shop
        self.fidelity_programs_data = fidelity_programs_data
        self.name = None
        self.prod_value = None
        self.points_coefficient = None
        self.prize_coefficient = None
        self.selected_program = None
        self.is_persistent = False

    def show(self) -> Any:
        container = st.container()
        self.name = container.text_input(
            label='Name'
        )
        self.prod_value = container.text_input(
            label="Value",
            placeholder="enter product value",
        )
        if isinstance(self.fidelity_programs_data, FidelityProgramDetail):
            self.selected_program = self.fidelity_programs_data
        else:
            programs = self.fidelity_programs_data.show()
            if len(programs.selected_rows) > 0:
                self.selected_program = FidelityProgramDetail(url=programs.selected_rows[0]['url']).get()
        if self.selected_program is not None:
            min_lim, max_lim = coefficient_limits(self.selected_program.program_type)
            self.is_persistent = container.checkbox(
                label='Is a prize which can be redeemed later by customer',
                key='Create checkbox'
            )
            self.points_coefficient = container.slider(
                label="Points coefficient",
                min_value=min_lim,
                max_value=max_lim,
                value=self.selected_program.points_coefficient,
                step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
                format="%.4f",
                key='Points coefficient create'
            )
            self.prize_coefficient = container.slider(
                label="Prize coefficient",
                min_value=min_lim,
                max_value=max_lim,
                value=self.selected_program.points_coefficient,
                step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
                format="%.4f",
                key='Prize coefficient create'
            )
        button = container.button("Create")
        if button:
            self.element = ProductDetail(
                name=self.name,
                shop=self.shop.url,
                value=float(self.prod_value),
                fidelity_program=self.selected_program.url,
                is_persistent=self.is_persistent,
                points_coefficient=self.points_coefficient,
                prize_coefficient=self.prize_coefficient,
            ).create_or_update()
        return container


