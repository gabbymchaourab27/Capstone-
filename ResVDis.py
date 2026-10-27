import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
#### Google Gemini Was used inorder to aid in error checking
#### Formula https://en.wikipedia.org/wiki/Ground_sample_distance
#### DJI Inspire 3 Values


def main() -> None:
    print("This Gives us Ground Sample Distance")
    print("It uses the DJI Inspire 3 Camera for Calculations")
    try:
        PltVals = ResVDisComp()
        
        CreatePlot(PltVals)
    except:
        print("Error Calculating or Plotting")

    return


def ResVDisComp()-> int:
#This comps spatial Resolution
#https://www.dji.com/inspire-3/specs
# Values used for formula can be find above
    PlotVals = [] #Will be Tuples of (Distance, GSD)
    

    Dis = 0
    while Dis < 1000: # Distance is Meters
        GSD = (Dis*1000*36)/(75*8192) ### the 36mm and 75mm values have been converted to meters and the pix is in 8912
        PlotVals.append((Dis, GSD))
        Dis += 1

    return PlotVals

def CreatePlot(pltVals: list) -> None:
    
    xpoints = []
    ypoints = []

    for vals in pltVals:
        xpoints.append(vals[0]) #distance
        ypoints.append(vals[1])

    Xpoints = np.array(xpoints)
    Ypoints = np.array(ypoints)
    plt.title("Ground Sample Distance vs Altitude Using DJI Inspire 3")
    plt.xlabel("Distance (m)")
    plt.text(10, 40, 'Lens Size: 70mm, Max Resolution Photo: 8192×5456 ', fontsize=8)
    plt.ylabel("GSD (mm/pixel)")
    plt.plot(Xpoints, Ypoints)
    plt.show()

    return


## Function Calls
main()
