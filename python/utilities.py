#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import math
import matplotlib.colors as Colors


def plotBinaryMap(axes, name, data, colors=["black", "lime", "gray"]):

    axes.set_title(name)
    axes.set_xlabel("Rows")
    axes.set_ylabel("Columns")

    plotW = math.ceil(math.sqrt(len(data)))

    rf = np.zeros([plotW, plotW], dtype=np.uint8)
    for i in range(plotW):
        arr = data[i * plotW : i * plotW + plotW] * 5
        if len(arr) < plotW:
            arr = np.concatenate(
                [arr, np.ones(plotW - len(arr)) * 10]
            )  # fill end where is nothing
        rf[:, i] = arr

    cm = Colors.LinearSegmentedColormap.from_list("myCMap", colors, N=3)

    axes.imshow(rf, interpolation="nearest", norm=Colors.Normalize(0, 10), cmap=cm)


def plotEnvironment(
    axes, name, env, agentPos, colors=["white", "blue", "red", "lightGray", "cyan"]
):

    environmentData = env._features

    # Translate list (with custom datatypes) to the numpy numeric array
    width = env._width
    height = env._height
    arr = np.zeros((width, height), dtype=np.uint8)
    for x in range(width):
        for y in range(height):
            if environmentData[x][y] != None:
                arr[x][y] = 1

    axes.set_title(name)
    axes.set_xlabel("x")
    axes.set_ylabel("y")

    # features will be value 5
    arr = arr

    agX = agentPos[0]
    agY = agentPos[1]

    arr[agX, agY] = 2  # agent pos

    # highlight sensors around him
    if agX > 0:
        arr[agX - 1, agY] = 4 if arr[agX - 1, agY] == 1 else 3
    if agY > 0:
        arr[agX, agY - 1] = 4 if arr[agX, agY - 1] == 1 else 3
    if agX < env._width:
        arr[agX + 1, agY] = 4 if arr[agX + 1, agY] == 1 else 3
    if agY < env._height:
        arr[agX, agY + 1] = 4 if arr[agX, agY + 1] == 1 else 3

    cm = Colors.LinearSegmentedColormap.from_list("myCMap", colors, N=5)

    print(arr)
    print(cm)
    axes.set_xticks(np.arange(-0.5, 20, 1))
    axes.set_yticks(np.arange(-0.5, 20, 1))
    axes.set_xticklabels(np.arange(0, 20, 1))
    axes.set_yticklabels(np.arange(0, 20, 1))

    axes.grid(color="w", linestyle="-", linewidth=2)
    axes.imshow(arr.T, interpolation="nearest", norm=Colors.Normalize(0, 5), cmap=cm)


def isNotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter
