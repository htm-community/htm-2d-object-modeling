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
import random

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

PLOT_GRAPHS = False
PLOT_ENV = False
DISABLE_PANDA = True

# Panda vis
if not DISABLE_PANDA:
    from pandaComm.pandaServer import PandaServer
    from pandaComm.dataExchange import ServerData, dataHTMObject, dataLayer, dataInput


_EXEC_DIR = os.path.dirname(os.path.abspath(__file__))
# go one folder up and then into the objects folder
_OBJECTS_DIR = os.path.join(_EXEC_DIR, os.path.pardir, "objects")

OBJECT_FILENAME = "a.yml"  # what object to load

anomalyHistData = []
fig_layers = None
fig_graphs = None
fig_environment = None
fig_expect = None
firstStep = True
iterationNo = 0

if not DISABLE_PANDA:
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
    sensorEncoderParams.seed = parameters["enc"]["seed"]
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
        seed=locParams["seed"],
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


def SystemCalculate(feature, learning , predictiveCellsSDR_last):
    global sensorLayer_sp, sensorLayer_tm, anomalyHistData, fig_layers, fig_graphs, fig_environment, rawAnomaly, firstStep, predictiveCellsSDR

    # ENCODE DATA TO SDR--------------------------------------------------
    # Convert sensed feature to int
    sensedFeature = 1 if feature == "X" else 0
    sensorSDR = sensorEncoder.encode(sensedFeature)

    # ACTIVATE COLUMNS IN SENSORY LAYER ----------------------------------
    # Execute Spatial Pooling algorithm on Sensory Layer with sensorSDR as proximal input
    sensorLayer_sp.compute(sensorSDR, learning, sensorLayer_SDR_columns)

    if not firstStep:
    # and calculate anomaly - compare how much of active columns had some predictive cells
        rawAnomaly = Anomaly.calculateRawAnomaly(sensorLayer_SDR_columns,
                                             sensorLayer_tm.cellsToColumns(predictiveCellsSDR_last))
    else:
        rawAnomaly = 0

    # SIMULATE LOCATION LAYER --------------------------------------------
    # Execute Location Layer - it is just GC encoder
    gridCellEncoder.encode(agent.get_nextPosition(), locationlayer_SDR_cells)

    #
    # Execute Temporal memory algorithm over the Sensory Layer, with mix of
    # Location Layer activity and Sensory Layer activity as distal input
    externalDistalInput = locationlayer_SDR_cells


    if firstStep:
        firstStep = False


    sensorLayer_tm.activateCells(sensorLayer_SDR_columns, learning)

    # activateDendrites calculates active segments
    sensorLayer_tm.activateDendrites(learn=learning, externalPredictiveInputsActive=externalDistalInput,
                                     externalPredictiveInputsWinners=externalDistalInput)
    # predictive cells are calculated directly from active segments
    predictiveCellsSDR = sensorLayer_tm.getPredictiveCells()

    # --------------------- VIS ------------------------------

    if not DISABLE_PANDA and (not pandaServer.gotoIteration or (pandaServer.gotoIteration and pandaServer.gotoIteration_no == iterationNo)):
        # ------------------HTMpandaVis----------------------
        # fill up values
        serverData.iterationNo = iterationNo
        serverData.HTMObjects["HTM1"].inputs["FeatureSensor"].stringValue = "Feature: {:.2f}".format(sensedFeature)
        serverData.HTMObjects["HTM1"].inputs["FeatureSensor"].bits = sensorSDR.sparse
        serverData.HTMObjects["HTM1"].inputs["FeatureSensor"].count = sensorSDR.size

        serverData.HTMObjects["HTM1"].inputs["LocationLayer"].stringValue = str(agent.get_position())
        serverData.HTMObjects["HTM1"].inputs["LocationLayer"].bits = locationlayer_SDR_cells.sparse
        serverData.HTMObjects["HTM1"].inputs["LocationLayer"].count = locationlayer_SDR_cells.size

        serverData.HTMObjects["HTM1"].layers["SensoryLayer"].activeColumns = sensorLayer_SDR_columns.sparse


        serverData.HTMObjects["HTM1"].layers["SensoryLayer"].winnerCells = sensorLayer_tm.getWinnerCells().sparse
        serverData.HTMObjects["HTM1"].layers["SensoryLayer"].activeCells = sensorLayer_tm.getActiveCells().sparse
        serverData.HTMObjects["HTM1"].layers["SensoryLayer"].predictiveCells = predictiveCellsSDR.sparse


        # print("ACTIVECOLS:"+str(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].activeColumns ))
        # print("WINNERCELLS:"+str(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].winnerCells))
        # print("ACTIVECELLS:" + str(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].activeCells))
        # print("PREDICTCELLS:"+str(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].predictiveCells))

        pandaServer.serverData = serverData

        pandaServer.spatialPoolers["HTM1"] = sensorLayer_sp
        pandaServer.temporalMemories["HTM1"] = sensorLayer_tm
        pandaServer.NewStateDataReady()


    print("Position:" + str(agent.get_position()))
    print("Feature:" + str(sensedFeature))
    print("Anomaly score:" + str(rawAnomaly))
    anomalyHistData += [rawAnomaly]
    # ------------------HTMpandaVis----------------------


    if PLOT_ENV and not pandaServer.gotoIteration:
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
        plt.pause(0.001)  # delay is needed for proper redraw

    if not DISABLE_PANDA:

        if pandaServer.gotoIteration:
            if pandaServer.gotoIteration_no <= iterationNo:
                pandaServer.gotoIteration = False

        if not pandaServer.gotoIteration:
            print("One step finished")
            while not pandaServer.runInLoop and not pandaServer.runOneStep and not pandaServer.gotoIteration:
                pass
            pandaServer.runOneStep = False
            print("Proceeding one step...")



    if PLOT_GRAPHS and not pandaServer.gotoIteration:
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

    if not DISABLE_PANDA:
        # set up pandaVis
        pandaServer.Start()
        BuildPandaSystem(modelParams)

    # set up system
    SystemSetup(modelParams)
    firstStep = True

    # put agent in the environment
    agent.set_env(env, 1, 1, 1, 1) # is on [1,1] and will go to [1,1]

    agentDir = Direction.RIGHT




    random.seed(1)

    # for x in range(2000):
    #     print("Iteration:" + str(iterationNo))
    #     SystemCalculate(agent.get_feature(Direction.UP))
    #
    #     # find direction that is not behind border of environment
    #     agentDir = Direction(random.randrange(0, 4))
    #     while agent.isBorderInThisDir(agentDir):
    #         agentDir = Direction(random.randrange(0, 4))
    #
    #     agent.moveDir(agentDir)
    #
    #     if PLOT_ENV or PLOT_GRAPHS:
    #         time.sleep(0.01)
    #     iterationNo += 1

    # iterationNo = 0
    # for i in range(10):
    #     for x in range(1, 19):
    #         for y in range(1, 19):
    #             print("Iteration:" + str(iterationNo))
    #
    #             if iterationNo <= 246:
    #                 pandaServer.runOneStep = True
    #             SystemCalculate(agent.get_feature(Direction.UP))
    #
    #             if iterationNo == 245:
    #                 print(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].activeColumns)
    #                 print(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].winnerCells)
    #                 print(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].predictiveCells)
    #             if iterationNo == 246:
    #                 print(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].activeColumns)
    #                 print(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].winnerCells)
    #                 print(serverData.HTMObjects["HTM1"].layers["SensoryLayer"].predictiveCells)
    #
    #             agent.move(x, y)
    #
    #             iterationNo += 1

    iterationNo = 0
    # for i in range(100000):
    #     for x in range(1, 19):
    #         for y in range(1, 19):
    #             print("Iteration:" + str(iterationNo))
    #             SystemCalculate(agent.get_feature(Direction.UP))
    #
    #             agent.nextMove(x, y) # this tells agent where he will make movement next time & it will make previously requested movement
    #
    #             iterationNo += 1

    predictiveCellsSDR_last = SDR( modelParams["sensorLayer_sp"]["columnCount"]*modelParams["sensorLayer_tm"]["cellsPerColumn"])
    for i in range(20):
        for x in range(1, 19):
            for y in range(1, 19):
                print("Iteration:" + str(iterationNo))
                SystemCalculate(agent.get_feature(Direction.UP),learning=True, predictiveCellsSDR_last = predictiveCellsSDR_last)
                predictiveCellsSDR_last = predictiveCellsSDR
                agent.nextMove(x, y) # this tells agent where he will make movement next time & it will make previously requested movement

                iterationNo += 1

    expectedObject = [x[:] for x in [[0] * 20] * 20]

    A = [x[:] for x in [[0] * 20] * 20]
    B = [x[:] for x in [[0] * 20] * 20]

    predSDR1 = SDR(predictiveCellsSDR)
    predSDR2 = SDR(predictiveCellsSDR)

    # calculate what kind of object will system expect
    for x in range(0,20):
        for y in range(1,20):# for sensor UP !
            agent.nextMove(x, y)

            SystemCalculate("X", learning=False, predictiveCellsSDR_last = predSDR1)
            predSDR1 = predictiveCellsSDR
            print("active:" + str(sensorLayer_SDR_columns.sparse))
            print("predictive:"+ str(predictiveCellsSDR))
            scoreWithFeature = rawAnomaly

            SystemCalculate(" ", learning=False, predictiveCellsSDR_last = predSDR2)
            predSDR2 = predictiveCellsSDR
            print("active:" + str(sensorLayer_SDR_columns.sparse))
            print("predictive:" + str(predictiveCellsSDR))
            scoreWithoutFeature = rawAnomaly

            A[x][y] = scoreWithFeature
            B[x][y] = scoreWithoutFeature
            expectedObject[x][y] = 1 if scoreWithFeature > scoreWithoutFeature else 0


    print(A)
    print(B)
    print(expectedObject)

    # Plotting and visualising environment-------------------------------------------
    if (
            fig_expect == None or isNotebook()
    ):  # create figure only if it doesn't exist yet or we are in interactive console
        fig_expect, _ = plt.subplots(nrows=1, ncols=1, figsize=(6, 4))
    else:
        fig_expect.axes[0].clear()

    plotBinaryMap(fig_expect.axes[0], "Expectation", expectedObject)
    fig_expect.canvas.draw()

    plt.show(block=False)
    plt.pause(20)  # delay is needed for proper redraw


    # for x in range(2000):
    #     for i in range(5):
    #         print("Iteration:" + str(iterationNo))
    #         SystemCalculate()
    #         agent.moveDir(agentDir)
    #         if agent.get_position() == [3, 4]:
    #             sensorLayer_tm.reset()
    #             print("reset!")
    #         time.sleep(0.01)
    #         iterationNo += 1
    #     agentDir = Direction.RIGHT if agentDir == Direction.LEFT else Direction.LEFT

    if not DISABLE_PANDA:
        pandaServer.MainThreadQuitted()