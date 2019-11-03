#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import yaml
import htm2d.environment
import htm2d.agent
from htm2d.agent import Direction
import numpy as np
import time
import matplotlib.pyplot as plt

from utilities import (
    plotBinaryMap,
    isNotebook,
    plotEnvironment,
)  # auxiliary functions from utilities.py

from htm.bindings.algorithms import SpatialPooler, TemporalMemory
from htm.bindings.sdr import SDR, Metrics
from htm.encoders.rdse import RDSE, RDSE_Parameters
from htm.encoders.grid_cell_encoder import GridCellEncoder
from htm.algorithms.anomaly import Anomaly

# Panda vis
from pandaComm.pandaServer import PandaServer
from pandaComm.dataExchange import ServerData, dataHTMObject, dataLayer, dataInput


PLOT_GRAPHS = False

_EXEC_DIR = os.path.dirname(os.path.abspath(__file__))
# go one folder up and then into the objects folder
_OBJECTS_DIR = os.path.join(_EXEC_DIR, os.path.pardir, "objects")

OBJECT_FILENAME = "a.yml"  # what object to load

anomalyHistData = []
fig_layers = None
fig_graphs = None
fig_environment = None

pandaServer = PandaServer()

def SystemSetup(parameters, verbose=True):
    global agent, sensorEncoder, env, sensorLayer_sp, sensorLayer_SDR_columns
    global gridCellEncoder, locationlayer_SDR_cells
    global sensorLayer_tm

    if verbose:
        import pprint

        print("Parameters:")
        pprint.pprint(parameters, indent=4)
        print("")

    # create environment and the agent
    env = htm2d.environment.TwoDimensionalEnvironment(20, 20)
    agent = htm2d.agent.Agent()

    # load object from yml file
    with open(os.path.join(_OBJECTS_DIR, OBJECT_FILENAME), "r") as stream:
        try:
            env.load_object(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # SENSOR LAYER --------------------------------------------------------------
    # setup sensor encoder
    sensorEncoderParams = RDSE_Parameters()
    sensorEncoderParams.category = True
    sensorEncoderParams.size = parameters["enc"]["size"]
    sensorEncoderParams.sparsity = parameters["enc"]["sparsity"]
    sensorEncoder = RDSE(sensorEncoderParams)

    # Create SpatialPooler
    spParams = parameters["sensorLayer_sp"]
    sensorLayer_sp = SpatialPooler(
        inputDimensions=(sensorEncoder.size,),
        columnDimensions=(spParams["columnCount"],),
        potentialPct=spParams["potentialPct"],
        potentialRadius=sensorEncoder.size,
        globalInhibition=True,
        localAreaDensity=spParams["localAreaDensity"],
        synPermInactiveDec=spParams["synPermInactiveDec"],
        synPermActiveInc=spParams["synPermActiveInc"],
        synPermConnected=spParams["synPermConnected"],
        boostStrength=spParams["boostStrength"],
        wrapAround=True,
    )
    sp_info = Metrics(sensorLayer_sp.getColumnDimensions(), 999999999)

    # Create an SDR to represent active columns, This will be populated by the
    # compute method below. It must have the same dimensions as the Spatial Pooler.
    sensorLayer_SDR_columns = SDR(spParams["columnCount"])

    # LOCATION LAYER ------------------------------------------------------------
    # Grid cell modules
    locParams = parameters["locationLayer"]

    gridCellEncoder = GridCellEncoder(
        size=locParams["cellCount"],
        sparsity=locParams["sparsity"],
        periods=locParams["periods"],
    )

    locationlayer_SDR_cells = SDR(gridCellEncoder.dimensions)

    tmParams = parameters["sensorLayer_tm"]
    sensorLayer_tm = TemporalMemory(
        columnDimensions=(spParams["columnCount"],),
        cellsPerColumn=tmParams["cellsPerColumn"],
        activationThreshold=tmParams["activationThreshold"],
        initialPermanence=tmParams["initialPerm"],
        connectedPermanence=spParams["synPermConnected"],
        minThreshold=tmParams["minThreshold"],
        maxNewSynapseCount=tmParams["newSynapseCount"],
        permanenceIncrement=tmParams["permanenceInc"],
        permanenceDecrement=tmParams["permanenceDec"],
        predictedSegmentDecrement=0.0,
        maxSegmentsPerCell=tmParams["maxSegmentsPerCell"],
        maxSynapsesPerSegment=tmParams["maxSynapsesPerSegment"],
        externalPredictiveInputs=locParams["cellCount"],
    )
    tm_info = Metrics([sensorLayer_tm.numberOfCells()], 999999999)


def SystemCalculate():
    global sensorLayer_sp, sensorLayer_tm, anomalyHistData, fig_layers, fig_graphs, fig_environment

    # Encode sensor data to SDR--------------------------------------------------

    # Convert sensed feature to int
    sensedFeature = 1 if agent.get_feature(Direction.UP) == "X" else 0

    sensorSDR = sensorEncoder.encode(sensedFeature)

    # Execute Spatial Pooling algorithm on Sensory Layer with sensorSDR as proximal input
    sensorLayer_sp.compute(sensorSDR, True, sensorLayer_SDR_columns)

    # Execute Location Layer - it is just GC encoder
    gridCellEncoder.encode(agent.get_position(), locationlayer_SDR_cells)

    # Execute Temporal memory algorithm over the Sensory Layer, with mix of
    # Location Layer activity and Sensory Layer activity as distal input
    externalDistalInput = locationlayer_SDR_cells
    #sensorLayer_tm.compute(
    #    activeColumns=sensorLayer_SDR_columns,
    #    learn=True,
    #    externalPredictiveInputsActive=externalDistalInput,
    #    externalPredictiveInputsWinners=externalDistalInput,
    #)  # we don't have columns in Location Layer

    # activateDendrites calculates active segments
    sensorLayer_tm.activateDendrites(learn=True, externalPredictiveInputsActive=externalDistalInput, externalPredictiveInputsWinners=externalDistalInput)
    # predictive cells are calculated directly from active segments
    predictiveCellsSDR = sensorLayer_tm.getPredictiveCells()

    rawAnomaly = Anomaly.calculateRawAnomaly(sensorLayer_SDR_columns, predictiveCellsSDR)



    sensorLayer_tm.activateCells(sensorLayer_SDR_columns, True)

    # ------------------HTMpandaVis----------------------

    # fill up values
    serverData.HTMObjects["HTM1"].inputs["FeatureSensor"].stringValue = "Feature: {:.2f}".format(sensedFeature)
    serverData.HTMObjects["HTM1"].inputs["FeatureSensor"].bits = sensorSDR.sparse
    serverData.HTMObjects["HTM1"].inputs["FeatureSensor"].count = sensorSDR.size

    serverData.HTMObjects["HTM1"].inputs["LocationLayer"].stringValue = str(agent.get_position())
    serverData.HTMObjects["HTM1"].inputs["LocationLayer"].bits = locationlayer_SDR_cells.sparse
    serverData.HTMObjects["HTM1"].inputs["LocationLayer"].count = locationlayer_SDR_cells.size

    serverData.HTMObjects["HTM1"].layers["SensoryLayer"].activeColumns = sensorLayer_SDR_columns.sparse
    serverData.HTMObjects["HTM1"].layers["SensoryLayer"].winnerCells = sensorLayer_tm.getWinnerCells().sparse
    serverData.HTMObjects["HTM1"].layers["SensoryLayer"].predictiveCells = predictiveCellsSDR.sparse

    pandaServer.serverData = serverData

    pandaServer.spatialPoolers["HTM1"] = sensorLayer_sp
    pandaServer.temporalMemories["HTM1"] = sensorLayer_tm
    pandaServer.NewStateDataReady()

    print("Position:" + str(agent.get_position()))
    print("Feature:" + str(sensedFeature))
    print("Anomaly score:" + str(rawAnomaly))
    anomalyHistData += [sensorLayer_tm.anomaly]

    # Plotting and visualising environment-------------------------------------------
    if (
            fig_environment == None or isNotebook()
    ):  # create figure only if it doesn't exist yet or we are in interactive console
        fig_environment, _ = plt.subplots(nrows=1, ncols=1, figsize=(6, 4))
    else:
        fig_environment.axes[0].clear()

    plotEnvironment(fig_environment.axes[0], "Environment", env, agent.get_position())
    fig_environment.canvas.draw()

    plt.show(block=False)
    plt.pause(0.1)  # delay is needed for proper redraw

    print("One step finished")
    #while not pandaServer.runInLoop and not pandaServer.runOneStep:
    #    pass
    pandaServer.runOneStep = False
    print("Proceeding one step...")

    # ------------------HTMpandaVis----------------------

    if PLOT_GRAPHS:
        # ---------------------------
        if (
                fig_graphs == None or isNotebook()
        ):  # create figure only if it doesn't exist yet or we are in interactive console
            fig_graphs, _ = plt.subplots(nrows=1, ncols=1, figsize=(5, 2))
        else:
            fig_graphs.axes[0].clear()

        fig_graphs.axes[0].set_title("Anomaly score")
        fig_graphs.axes[0].plot(anomalyHistData)
        fig_graphs.canvas.draw()

        #if agent.get_position() != [3, 4]:  # HACK ALERT! Ignore at this pos (after reset)
        #    anomalyHistData += [sensorLayer_tm.anomaly]




def BuildPandaSystem(modelParams):
    global serverData
    serverData = ServerData()
    serverData.HTMObjects["HTM1"] = dataHTMObject()
    serverData.HTMObjects["HTM1"].inputs["FeatureSensor"] = dataInput()

    serverData.HTMObjects["HTM1"].layers["SensoryLayer"] = dataLayer(
        modelParams["sensorLayer_sp"]["columnCount"],
        modelParams["sensorLayer_tm"]["cellsPerColumn"],
    )
    serverData.HTMObjects["HTM1"].layers["SensoryLayer"].proximalInputs = ["FeatureSensor"]
    serverData.HTMObjects["HTM1"].layers["SensoryLayer"].distalInputs = ["LocationLayer"]


    serverData.HTMObjects["HTM1"].inputs["LocationLayer"] = dataInput() # for now, Location layer is just position encoder

if __name__ == "__main__":

    # load model parameters from file
    f = open("modelParams.cfg", "r").read()
    modelParams = eval(f)

    # set up pandaVis
    pandaServer.Start()
    BuildPandaSystem(modelParams)

    # set up system
    SystemSetup(modelParams)

    # put agent in the environment
    agent.set_env(env, 3, 4)

    agentDir = Direction.RIGHT
    iterationNo = 0






    for x in range(2000):
        for i in range(5):
            print("Iteration:" + str(iterationNo))
            SystemCalculate()
            agent.moveDir(agentDir)
            if agent.get_position() == [3, 4]:
                sensorLayer_tm.reset()
                print("reset!")
            time.sleep(0.01)
            iterationNo += 1
        agentDir = Direction.RIGHT if agentDir == Direction.LEFT else Direction.LEFT

    pandaServer.MainThreadQuitted()