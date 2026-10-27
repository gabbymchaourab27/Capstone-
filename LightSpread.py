from LightImport import *

def main() -> None:
    print("Light Spreading Simulation")
    if (1==InverseSquare()):
        return
    else:
        print("Failed Operand, Try Again")

    
    
    return


def InverseSquare()-> int:
# Source for formulas https://en.wikipedia.org/wiki/Inverse-square_law
# LEO altitude found in this link (1,200 miles -> 1931213m) https://www.nasa.gov/humans-in-space/leo-economy-frequently-asked-questions/
    LEO = 100
    LinesToPlot = {.0001:[], .003:[], .02:[]}
    LEDDis = [] ### distance
    UVals = [.0001, 0.003, .02] # https://journals.ametsoc.org/view/journals/atsc/73/11/jas-d-16-0102.1.xml
                ### uses the Koschmieder Model  Vct = 3.9/ea (summ of absorption and scattering coefficient) 
                ### three values given to me via gemini
    print("This is simulating light attentuation using the Inverse Square Law\n")
    CommonU()
    InitIn = float(input("Input Light Source Lumens: "))
    InitIn = InitIn/4*math.pi
    
    for value in UVals:
        inc = 1
        while inc <= LEO:
           
            ## Gemini aided in the devolpment of this math but not the code
            
            intensity = (InitIn/(inc**2)) * math.exp(-value*inc)
            LinesToPlot[value].append((inc,intensity))

            # a Lux is 1 lumen of light spread over a 1m^2
            # more lux is more lumens per m^2 so more intensity
            #https://en.wikipedia.org/wiki/Lux
            inc +=1
    plotData(LinesToPlot)       
           
    
    return 1
    
    
    

def BloomModel() -> int:
    print("This Functions Will Now Model Light Bloom Over of inputted Distance")
    # This code utilizes the point spread function found from Wikipedia idea gained from Gemini
    # https://en.wikipedia.org/wiki/Point_spread_function

    
def CommonU():
    # values provided via Gemini
    print("Common Atmosphere densitys values are:\n Clean Air: 0.00001 (No Scattering)")
    print("Light Haze: 0.001 to 0.01")
    print("Thick Fog 0.02 to 0.1")

    print("Common Light Source Lumens are:")
    print("LED Diode: 1-5 Lumens")


def plotData(Dictionary: int) -> None:
    """
    for key in Dictionary:
        XValues = []
        YValues = []
        print(key)
        print(Dictionary.keys(), "this is the dictionary")
    """
    XValues = []
    YValues = []
    for values in Dictionary[.0001]: ## should be tuples with data
        XValues.append(values[0])
        YValues.append(values[1])
    xpoints = np.array(XValues)
    ypoints = np.array(YValues)

    plt.title("LUX vs Distance")
    plt.text(10, 60, 'Attenuation Coefficient (u) is .0001 (Clean Air)', fontsize=8)
    plt.xlabel("Distance (meters)")
    plt.ylabel("Illuminance (Lux)")
    plt.plot(xpoints, ypoints)
    plt.show()
