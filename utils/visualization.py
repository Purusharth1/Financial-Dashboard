"""Visualization helper functions for the Financial Dashboard."""

from pathlib import Path
from typing import TypedDict

import matplotlib.pyplot as plt
import pandas as pd


class PlotConfig(TypedDict):
    """Configuration for the line chart."""

    title: str
    xlabel: str
    ylabel: str
    output_path: Path


def plot_line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    config: PlotConfig,
) -> None:
    """Plot a line chart and save it to a file.

    Args:
        data: DataFrame with data to plot.
        x_col: Column name for the x-axis.
        y_cols: List of column names for the y-axis.
        config: Configuration dictionary for the chart (title, labels, output path).

    """
    # Create the plot
    plt.figure(figsize=(10, 6))
    for y_col in y_cols:
        plt.plot(data[x_col], data[y_col], label=y_col)

    # Add labels, title, and legend
    plt.title(config["title"])
    plt.xlabel(config["xlabel"])
    plt.ylabel(config["ylabel"])
    plt.legend()

    # Enable grid with explicit keyword argument
    plt.grid(visible=True)

    # Save the plot to the specified output path
    plt.savefig(config["output_path"], bbox_inches="tight")
    plt.close()
