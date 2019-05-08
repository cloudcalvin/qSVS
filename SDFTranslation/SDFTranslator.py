# ============================================================================#
#                           SDF Translator for qSVS                          #
#                                                                            #
#                      Arash Fayyazi and Massoud Pedram                      #
#     SPORT Lab, University of Southern California, Los Angeles, CA 90089    #
#                          http://sportlab.usc.edu/                          #
#                                                                            #
# For licensing, please refer to the LICENSE file in the main directory.     #
#                                                                            #
#                                                                            #
# The development is supported in part by IARPA SuperTools program           #
# via grant W911NF-17-1-0120.                                                #
#                                                                            #
# ============================================================================#
# !/usr/bin/python
import sys, os, re, fileinput, argparse, timeit
from operator import add


############## class definition ############
class Gate(object):

    def __init__(self, NAME, TYPE):
        self.IN = {}
        self.OUT = {}
        self.NAME = NAME
        self.TYPE = TYPE
        self.DELAY = {}
        self.SETUP = {}
        self.HOLD = {}


def parseCommandLines():
    global CircuitName, SDFFile, MODE
    MODE = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", type=int, choices=[0, 1],
                        help="SFQ or AQFP circuit. default mode is SFQ circuit. 0 for SFQ and 1 for AQFP")
    parser.add_argument("SDF_File_Name", help="the input SDF file")
    args = parser.parse_args()
    ###
    if args.mode: MODE = args.mode
    ###
    SDFFile = args.SDF_File_Name
    CircuitName = os.path.splitext(os.path.basename(args.SDF_File_Name))[0]
    current_path = os.getcwd()


################################################################################
### run it
def AQFP_translation():
    # SDFFile = sys.argv[1]
    # circuitName = os.path.splitext(os.path.basename(SDFFile))[0]
    CircuitInputFile = CircuitName + ".sv"
    SDFCopyFile = CircuitName + "_qSVS.sdf"
    INSTANCEstrings = ("INSTANCE", "(INSTANCE")
    CellTypestrings = ("CellType", "(CellType")
    IOPATHstrings = ("IOPATH", "(IOPATH")
    Splitterstrings = ("spl2", "spl3")
    SplitterOutstrings = ("out1", "out2", "out3")
    IOPATHName = "in out"
    CellType = '"ModuleDelay"'
    SuffixINSTANCE = [".snd.gDATA", ".snd1.gDATA", ".snd2.gDATA", ".snd3.gDATA"];
    os.system("cp " + SDFFile + " " + SDFCopyFile)
    fh = fileinput.input(SDFCopyFile, inplace=True)
    for line in fh:
        SPlitterLine = line
        if any(s in line for s in INSTANCEstrings):
            OutInd = 0
            words = line.split()
            for s in INSTANCEstrings:
                if (s in words):
                    ind = words.index(s)
                    INSTANCENamePos = ind + 1
                    INSTANCENameOrig = words[INSTANCENamePos]
                    INSTANCEName = INSTANCENameOrig.replace(")", "")
                    ######## handling of splitters
                    # with open(CircuitInputFile, 'r') as SVfile:
                    #	for SVline in SVfile:
                    #		if (INSTANCEName in SVline):
                    #			SVwords=SVline.split()
                    #			if (SVwords[0] in Splitterstrings):
                    nextLine1 = next(fh)
                    nextLine2 = next(fh)
                    SPlitterLine = next(fh)
                    Splitterwords = SPlitterLine.split()
                    for s in SplitterOutstrings:
                        if (s in Splitterwords):
                            OutInd = SplitterOutstrings.index(s) + 1

                    ######## finished handling of splitters
                    INSTANCEName = INSTANCEName + SuffixINSTANCE[OutInd] + ")"
            print(line.replace(INSTANCENameOrig, INSTANCEName), end="")
            print(nextLine1, end='')
            print(nextLine2, end='')
            if any(s in SPlitterLine for s in IOPATHstrings):
                words = SPlitterLine.split()
                for s in IOPATHstrings:
                    if (s in words):
                        ind = words.index(s)
                        IOPATHinPos = ind + 1
                        IOPATHinNameOrig = words[IOPATHinPos]
                        IOPATHoutPos = IOPATHinPos + 1
                        IOPATHoutNameOrig = words[IOPATHoutPos]
                        IOPATHNameOrig = IOPATHinNameOrig + " " + IOPATHoutNameOrig
                print(SPlitterLine.replace(IOPATHNameOrig, IOPATHName), end='')
        elif any(s in line for s in CellTypestrings):
            words = line.split()
            for s in CellTypestrings:
                if (s in words):
                    ind = words.index(s)
                    CellTypePos = ind + 1
                    CellTypeNameOrig = words[CellTypePos]
                    CellTypeName = CellType + ")"
            print(line.replace(CellTypeNameOrig, CellTypeName), end='')
        else:
            print(line, end='')

    fh.close()


##########################################################
def SFQ_translation():
    # SDFFile = sys.argv[1]
    # circuitName = os.path.splitext(os.path.basename(SDFFile))[0]
    CircuitInputFile = CircuitName + ".sv"
    SDFCopyFile = CircuitName + "_qSVS.sdf"
    INSTANCEstrings = ("INSTANCE", "(INSTANCE", "(INSTANCE)")
    CellTypestrings = ("CELLTYPE", "(CELLTYPE")
    DesignNameStrings = ("DESIGN", "(DESIGN")
    IOPATHstrings = ("IOPATH", "(IOPATH")
    InterconnectStrings = ("INTERCONNECT", "(INTERCONNECT")
    SetupStrings = ("SETUP", "(SETUP")
    HoldStrings = ("HOLD", "(HOLD")
    DelayCellType = "SFQGateDelay"
    SetupHoldCellType = ("SFQtimingcheck1", "SFQtimingcheck2")
    SetupHoldDic = ["data1", "data2", "data"]
    SuffixINSTANCE = [".gPD.g0", ".gPD1.g0", ".gPD2.g0", ".TC"]
    outName = ("out", "out", "out")
    bad_chars = [')', '(', '"']
    netlist = {}
    index = -1
    infile = open(SDFFile, 'r')
    # Parsing the input SDF file
    for line in infile:
        # Finding the design Name
        if any(s in line for s in DesignNameStrings):
            words = line.split()
            for s in DesignNameStrings:
                if s in words:
                    ind = words.index(s)
                    designNamePos = ind + 1
                    designNameOrig = words[designNamePos]
                    for i in bad_chars:
                        designNameOrig = designNameOrig.replace(i, '')
        # Finding the Cell name
        elif any(s in line for s in CellTypestrings):
            words = line.split()
            for s in CellTypestrings:
                if s in words:
                    ind = words.index(s)
                    CellTypePos = ind + 1
                    CellTypeOrig = words[CellTypePos]
                    for i in bad_chars:
                        CellTypeOrig = CellTypeOrig.replace(i, '')
        # Finding the instance name and build new gate based on cell and instance names
        elif any(s in line for s in INSTANCEstrings):
            index = index + 1
            words = line.split()
            for s in INSTANCEstrings:
                if s in words:
                    if len(words) == 1:
                        netlist[index] = Gate("INTERCONNECT", CellTypeOrig)
                    else:
                        ind = words.index(s)
                        INSTANCENamePos = ind + 1
                        INSTANCENameOrig = words[INSTANCENamePos]
                        for i in bad_chars:
                            INSTANCENameOrig = INSTANCENameOrig.replace(i, '')
                        netlist[index] = Gate(INSTANCENameOrig, CellTypeOrig)
                    # INSTANCEName = INSTANCEName + SuffixINSTANCE[OutInd] + ")"
        # Finding the IOPATH delay and fill the gate DELAY field
        elif any(s in line for s in IOPATHstrings):
            words = line.split()
            for s in IOPATHstrings:
                if s in words:
                    ind = words.index(s)
                    IOPATHinPos = ind + 1
                    IOPATHoutPos = IOPATHinPos + 1
                    IOPATHoutName = words[IOPATHoutPos]
                    IOPATHinName = words[IOPATHinPos]
                    IOPATHValue = words[ind + 3]
                    for i in bad_chars:
                        IOPATHValue = IOPATHValue.replace(i, '')
                    IOPATHvaluesFloat = list(map(float, IOPATHValue.split(':')))
                    if IOPATHinName in netlist[index].DELAY:
                        for key in netlist[index].OUT:
                            netlist[index].OUT[key] = "out1"
                        netlist[index].OUT[IOPATHoutName] = "out2"
                    else:
                        netlist[index].IN[IOPATHinName] = "in"
                        netlist[index].OUT[IOPATHoutName] = "out"
                        netlist[index].DELAY[IOPATHinName] = {}
                    netlist[index].DELAY[IOPATHinName][IOPATHoutName] = IOPATHvaluesFloat
        # Finding the INTERCONNECT delay and fill the gate DELAY field
        elif any(s in line for s in InterconnectStrings):
            words = line.split()
            for s in InterconnectStrings:
                if s in words:
                    ind = words.index(s)
                    INTERCONNECTinPos = ind + 1
                    INTERCONNECTinName = words[INTERCONNECTinPos]
                    INTERCONNECTValue = words[ind + 3]
                    for i in bad_chars:
                        INTERCONNECTValue = INTERCONNECTValue.replace(i, '')
                    INTERCONNECTvaluesFloat = list(map(float, INTERCONNECTValue.split(':')))
                    INTERCONNECTinGateWire = INTERCONNECTinName.split('/')
                    netlist[index].IN[INTERCONNECTinName] = INTERCONNECTinGateWire[0]
                    netlist[index].OUT[INTERCONNECTinName] = INTERCONNECTinGateWire[1]
                    netlist[index].DELAY[INTERCONNECTinName] = INTERCONNECTvaluesFloat
        # Finding the SETUP checks and fill the gate SETUP field
        elif any(s in line for s in SetupStrings):
            words = line.split()
            for s in SetupStrings:
                if s in words:
                    ind = words.index(s)
                    SetupNamePos = ind + 1
                    SetupName = words[SetupNamePos]
                    SetupValue = words[ind + 3]
                    for i in bad_chars:
                        SetupValue = SetupValue.replace(i, '')
                    SetupValuesFloat = list(map(float, SetupValue.split(':')))
                    netlist[index].SETUP[SetupName] = SetupValuesFloat
        # Finding the HOLD checks and fill the gate HOLD field
        elif any(s in line for s in HoldStrings):
            words = line.split()
            for s in HoldStrings:
                if s in words:
                    ind = words.index(s)
                    HoldNamePos = ind + 1
                    HoldName = words[HoldNamePos]
                    HoldValue = words[ind + 3]
                    for i in bad_chars:
                        HoldValue = HoldValue.replace(i, '')
                    HoldValuesFloat = list(map(float, HoldValue.split(':')))
                    netlist[index].HOLD[HoldName] = HoldValuesFloat
    infile.close()

    # Add interconnect delay to preceding gate
    for gateind1 in range(index+1):
        if netlist[gateind1].NAME == "INTERCONNECT":
            for gateInterconnectind in netlist[gateind1].IN:
                for gateind2 in range(index+1):
                    if netlist[gateind1].IN[gateInterconnectind] == netlist[gateind2].NAME:
                        for inkey in netlist[gateind2].IN:
                            netlist[gateind2].DELAY[inkey][netlist[gateind1].OUT[gateInterconnectind]]=\
                                list(map(add, netlist[gateind1].DELAY[gateInterconnectind],
                                     netlist[gateind2].DELAY[inkey][netlist[gateind1].OUT[gateInterconnectind]]))
                            break
                        break
        break

    # writing the output file
    outfile = open(SDFCopyFile, 'w')
    outfile.write("(DELAYFILE\n")
    outfile.write(" (DESIGN \"%s\")\n" % (designNameOrig))
    outfile.write(" (TIMESCALE 1ps)\n")
    for gateind in range(index+1):
        if netlist[gateind].NAME != "INTERCONNECT":
            # writing delay cell
            for inkey in netlist[gateind].IN:
                for outkey in netlist[gateind].OUT:
                    if netlist[gateind].OUT[outkey] == "out":
                        outfile.write(" (CELL\n   (CELLTYPE \"%s\")\n   (INSTANCE %s)\n   (DELAY\n     (ABSOLUTE\n" % (
                            DelayCellType, (netlist[gateind].NAME + SuffixINSTANCE[0])))
                        outfile.write("     (IOPATH %s %s (%.1f:%.1f))\n" % (
                            netlist[gateind].IN[inkey], outName[0],
                            netlist[gateind].DELAY[inkey][outkey][0],
                            netlist[gateind].DELAY[inkey][outkey][1]))
                        outfile.write("     )\n   )\n )\n")
                    elif netlist[gateind].OUT[outkey] == "out1":
                        outfile.write(" (CELL\n   (CELLTYPE \"%s\")\n   (INSTANCE %s)\n   (DELAY\n     (ABSOLUTE\n" % (
                            DelayCellType, (netlist[gateind].NAME + SuffixINSTANCE[1])))
                        outfile.write("     (IOPATH %s %s (%.1f:%.1f))\n" % (
                            netlist[gateind].IN[inkey], outName[1],
                            netlist[gateind].DELAY[inkey][outkey][0],
                            netlist[gateind].DELAY[inkey][outkey][1]))
                        outfile.write("     )\n   )\n )\n")
                    else:
                        outfile.write(" (CELL\n   (CELLTYPE \"%s\")\n   (INSTANCE %s)\n   (DELAY\n     (ABSOLUTE\n" % (
                            DelayCellType, (netlist[gateind].NAME + SuffixINSTANCE[2])))
                        outfile.write("     (IOPATH %s %s (%.1f:%.1f))\n" % (
                            netlist[gateind].IN[inkey], outName[2],
                            netlist[gateind].DELAY[inkey][outkey][0],
                            netlist[gateind].DELAY[inkey][outkey][1]))
                        outfile.write("     )\n   )\n )\n")

            # writing timingcheck cell
            if bool(netlist[gateind].SETUP):
                if len(netlist[gateind].SETUP) == 1:
                    outfile.write(" (CELL\n   (CELLTYPE \"%s\")\n   (INSTANCE %s)\n   (TIMINGCHECK\n" % (
                        SetupHoldCellType[0], (netlist[gateind].NAME + SuffixINSTANCE[3])))
                    for timingkey in netlist[gateind].SETUP:
                        outfile.write("     (SETUP %s (posedge clkin) (%.1f))\n" % (
                            SetupHoldDic[2], netlist[gateind].SETUP[timingkey][0]))
                        outfile.write("     (HOLD %s (posedge clkin) (%.1f))\n" % (
                            SetupHoldDic[2], netlist[gateind].HOLD[timingkey][0]))
                    outfile.write("   )\n )\n")
                else:
                    outfile.write(" (CELL\n   (CELLTYPE \"%s\")\n   (INSTANCE %s)\n   (TIMINGCHECK\n" % (
                        SetupHoldCellType[1], (netlist[gateind].NAME + SuffixINSTANCE[3])))
                    DicFlag = 0
                    for timingkey in netlist[gateind].SETUP:
                        outfile.write("     (SETUP %s (posedge clkin) (%.1f))\n" % (
                            SetupHoldDic[DicFlag], netlist[gateind].SETUP[timingkey][0]))
                        outfile.write("     (HOLD %s (posedge clkin) (%.1f))\n" % (
                            SetupHoldDic[DicFlag], netlist[gateind].HOLD[timingkey][0]))
                        DicFlag = DicFlag + 1
                    outfile.write("   )\n )\n")
    outfile.write(")\n")
    outfile.close()


##########################################################
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


################################################################################
start_time = timeit.default_timer()
print("      +------------------------------------------------------------------+")
print("      |                          SDF Translator 2.0                      |")
print("      |                                                                  |")
print("      | Copyright (C) 2019, SPORT Lab, University of Southern California |")
print("      +------------------------------------------------------------------+\n")
parseCommandLines()
if MODE == 0:
    message = "Translating of " + CircuitName + " in SFQ mode"
    print(message)
    SFQ_translation()
else:
    AQFP_translation()
    message = "Translating of " + CircuitName + " in AQFP mode"
    print(message)
stop_time = timeit.default_timer()
print("--------------------------------------------------------------------------------")
print("Translating of '" + CircuitName + "' finished (Runtime: %s)" % (hms_string(stop_time - start_time)))
print("Generated compatible SDF file is " + CircuitName + "_qSVS.sdf")
