from __future__ import annotations
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, AgGridReturn, ColumnsAutoSizeMode
from typing import Protocol, runtime_checkable, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from plclient.api.apiclient import APIClientDetail, APIClientList


@runtime_checkable
class UIElement(Protocol):
    def show(self) -> Any:
        ...


class Form(ABC):
    element: APIClientDetail

    @abstractmethod
    def show(self) -> Any:
        pass


@dataclass(frozen=True)
class Table:
    element: APIClientList
    columns: list[str]
    hidden_columns: list[str] | None = None
    selection_mode: str = field(default="single")
    key: str | None = None

    def show(self) -> Any:
        data = self.element.get()
        #if len(data) == 0:
        #    return st.text(f"No data registered yet!")
        df = pd.DataFrame.from_dict(data)[self.columns] if len(data) != 0 else pd.DataFrame(columns=self.columns)
        builder = GridOptionsBuilder.from_dataframe(df)
        builder.configure_selection(selection_mode=self.selection_mode)
        if self.hidden_columns is not None:
            builder.configure_columns(column_names=self.hidden_columns, hide=True)
        go = builder.build()
        filtered_df = AgGrid(
            df,
            gridOptions=go,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
            theme="alpine",
            enable_enterprise_modules=False,
            key=self.key
        )
        #st.write(filtered_df.selected_rows)
        return filtered_df
