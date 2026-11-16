import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1])
print(pcbnew.WriteDRCReport(b,sys.argv[2],pcbnew.EDA_UNITS_MILLIMETRES,True))
