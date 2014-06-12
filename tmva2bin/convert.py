import sys
import tempfile
import warnings

from . import tauvariables
from . import treereading
from .decisiontree import *


def convert(inputNames, outputName, type, format, categoryTree=None):

    inputs = []

    for file in inputNames:
        try:
            inputs.append(open(file,'r'))
        except:
            print "Input file %s will not open"%file
            return
    try:
        output = open(outputName,'w')
    except:
        print "Output file %s will not open"%outputName
        return

    if len(inputs) == 1:
        for input,inputName in zip(inputs,inputNames):
            print "Reading input..."
            if type == "BDT":
                bdt = treereading.readTMVA(input)
            elif type == "CUTS":
                bdt = treereading.readCuts(input)
            else:
                print "Unsupported type: %s"%type
                return
            if not bdt:
                return
            print "Writing output..."
            variableList = bdt.variables
            output.write("0\n") # No variables are binned
            output.write(str(len(variableList))+'\n')

            for variable,typename in variableList:
                if variable.upper() in [value.upper() for value in tauvariables.DPD2TD.values()]:
                    output.write("%s %s\n"%(variable.upper(),typename))
                elif tauvariables.DPD2TD.has_key(variable):
                    output.write("%s %s\n"%(tauvariables.DPD2TD[variable].upper(),typename))
                else:
                    """
                    warnings.warn(
                        "variable %s is not defined in tauvariables as a "
                        "TauDiscriminant variable"% variable, RuntimeWarning)
                    """
                    output.write("%s %s\n"%(variable.upper(),typename))

            bdt.write(output,format)
            output.close()
    else:
        masterVariableList = []
        variableTranslator = {}
        temp = tempfile.TemporaryFile()
        categoryVariables = categoryTree.variables

        output.write(str(len(categoryVariables))+'\n')
        for variable,typename in categoryVariables:
            if variable.upper() in [value.upper() for value in tauvariables.DPD2TD.values()]:
                output.write("%s %s\n"%(variable.upper(),typename))
            elif tauvariables.DPD2TD.has_key(variable):
                output.write("%s %s\n"%(tauvariables.DPD2TD[variable].upper(),typename))
            else:
                warnings.warn(
                        "variable %s is not defined in tauvariables as a "
                        "TauDiscriminant variable"% variable, RuntimeWarning)
                output.write("%s %s\n"%(variable.upper(),typename))

        categoryTree.add_pointer_leaves()
        categoryTree.write(output, "txt")

        print "Reading input and merging variable lists..."
        for input in inputs:
            print input.name
            if type == "BDT":
                bdt = treereading.readTMVA(input)
            elif type == "CUTS":
                bdt = treereading.readCuts(input)
            else:
                print "Unsupported type: %s"%type
                return
            if not bdt:
                print "Could not parse %s"% input.name
                return
            varList = bdt.variables
            variableTranslator.clear()

            for index,variable in enumerate(varList):
                if variable in masterVariableList:
                    #print "%s already in variable list"%str(variable)
                    newIndex = masterVariableList.index(variable)
                else:
                    #print "%s not found in variable list. appending"%str(variable)
                    masterVariableList.append(variable)
                    newIndex = len(masterVariableList)-1
                variableTranslator[index] = newIndex
            bdt.write(temp,format,variableTranslator)

        print "Writing output..."

        # Write the variable list information to the output file
        output.write(str(len(masterVariableList))+'\n')
        for variable,typename in masterVariableList:
            if variable.upper() in [value.upper() for value in tauvariables.DPD2TD.values()]:
                output.write("%s %s\n"%(variable.upper(),typename))
            elif tauvariables.DPD2TD.has_key(variable):
                output.write("%s %s\n"%(tauvariables.DPD2TD[variable].upper(),typename))
            else:
                warnings.warn(
                        "variable %s is not defined in tauvariables as a "
                        "TauDiscriminant variable"% variable, RuntimeWarning)
                output.write("%s %s\n"%(variable.upper(),typename))

        # Copy bdts in temporary file to the output file
        temp.seek(0)
        line = temp.readline()
        while line != "":
            output.write(line)
            line = temp.readline()

        temp.close()
        output.close()

    for file in inputs:
        file.close()
    print "Done."

