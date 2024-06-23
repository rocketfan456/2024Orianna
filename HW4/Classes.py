import numpy as np
import math

def PrintData(phaseList):
    print('{0:25s}'.format("-----------------------------------------------------------------------------------------" ))
    print('{0:20s}{1:>11s}{2:>11s}{3:>11s}{4:>13s}{5:>13s}{6:>14s}'.format("Phase Name", "DV (m/s)", "Mass0 (kg)", "MassF (kg)", "TotProp (kg)", "OxProp (kg)", "FuelProp (kg)"  ))
    print('{0:25s}'.format("-----------------------------------------------------------------------------------------" ))
    for curPhase in phaseList:
        print('{0:20s}{1:11.1f}{2:11.1f}{3:11.1f}{4:13.1f}{5:13.1f}{6:14.1f}'.format(curPhase.strName, curPhase.dvPhase, curPhase.mStart, curPhase.mEnd, curPhase.mPropImpulse, curPhase.mPropImpulseOx, curPhase.mPropImpulseFuel ))

class Phase:

    def __init__(self,strName, mStart, dvPhase, clsEng):

        # Check if this is a T/W phase. If so,
        # update the dV calculate the thrust-to-weight
        twPhase = clsEng.thrust/(mStart*9.81)
        if dvPhase<0:
            dvPhase = 4335*np.exp(-(twPhase)*20.25)+1880


        # Calculate Impulse Propellant Using Rocket Equation
        mPropImpulse = mStart - mStart / np.exp(dvPhase/(9.81*clsEng.isp))


        # Determine Oxidizer and Fuel
        mPropImpulseOx = mPropImpulse*clsEng.mr/(1+clsEng.mr)
        mPropImpulseFuel = mPropImpulse/(1+clsEng.mr)


        mEnd = mStart - mPropImpulse


        # Move data to class structure to save information
        self.mStart         = mStart
        self.mEnd           = mEnd
        self.dvPhase        = dvPhase
        self.clsEng         = clsEng
        self.mPropImpulse   = mPropImpulse
        self.strName        = strName
        self.twPhase        = twPhase

        self.mPropImpulse   = mPropImpulse
        self.mPropImpulseOx = mPropImpulseOx
        self.mPropImpulseFuel = mPropImpulseFuel

class MissionSummary:
    def __init__(self, tupPhases):
        """
        Inputs:
            tupPhases: list of phase classes

        """



        mPropImpulse     = 0
        mPropImpulseOx   = 0
        mPropImpulseFuel = 0

        # sum up the usages by phase
        for curPhase in tupPhases:
            mPropImpulse     += curPhase.mPropImpulse
            mPropImpulseOx   += curPhase.mPropImpulseOx
            mPropImpulseFuel += curPhase.mPropImpulseFuel

        # Stuff everything into self
        self.mPropImpulse      = mPropImpulse
        self.mPropImpulseOx    = mPropImpulseOx
        self.mPropImpulseFuel  = mPropImpulseFuel



class Engine:
    def __init__(self,isp, thrust, mr):
        self.isp = isp
        self.thrust = thrust
        self.mr = mr

class TankSet:
    def __init__(self, strPropType, strMatType, nTanks, lMaxRadTank, presTank, mPropTotal):
        # General Parameters for Tanks
        pctUllage = 0.10         # Extra ullage room as a percentage of tank volume
        aMax      = 50          # Maximum acceleration (m/s2)
        pctFudge  = 0.20        # Fudge factor for welds, etc
        fosMat    = 1.5         # factor of safety for material (nd)

        # Tank material switch case
        if strMatType=="Al2219":
            rhoMat = 2840     # Density of material (kg/m3)
            sigMat = 2.9e8    # Yield Stress of material (Pa)
            thkMin = 0.004   # Minimum thickness of material (m)
        elif strMatType=="Stainless":
            rhoMat = 8000
            sigMat = 2.15e8
            thkMin = 0.0004
        elif strMatType == "Al-Li":
            rhoMat = 2700
            sigMat = 7e8
            thkMin = 0.004


        # Propellant Density switch case
        if strPropType=="Oxygen":
            rhoProp =1140    # Density of propellant (kg/m3)
        elif strPropType=="Hydrogen":
            rhoProp =70
        elif strPropType == "Methane":
            rhoProp =420
        elif strPropType == "MMH":
            rhoProp =866
        elif strPropType == "NTO":
            rhoProp = 866
        elif strPropType == "RP-1":
            rhoProp = 820


        # Calculate propellant volume and volume per tank (include ullage)
        volPropTotal    = mPropTotal/rhoProp
        volPropPerTank  = volPropTotal/nTanks
        volPerTank      = volPropPerTank*(1+pctUllage)

        # Compare volume of tank to maximum allowable for given radius
        #    This will help us determine if the tank is a sphere or a pill.
        volMaxRadius    = 4/3*np.pi*(lMaxRadTank**3)

        if volMaxRadius>volPerTank:
            # A sphere with the max radius is too big, so calculate
            # the needed radius and set cylinder length to zero
            lRadiusTank = (volPerTank*3/4/np.pi)**(1/3)
            lCylTank   = 0

        else:
            # A sphere with the max radius is too small, so calculate
            # what the cylinder length will be
            lRadiusTank = lMaxRadTank
            lCylTank    = (volPerTank-4/3*np.pi*(lRadiusTank**3))/(np.pi*lRadiusTank**2)

        # Calculate the total length of the tank
        lTankLength = lCylTank+lRadiusTank*2

        # Calculate the surface area of each portion of the tank
        saDomesPerTank   = 4*np.pi*lRadiusTank**2
        saCylinderPerTank = 2*np.pi*lRadiusTank*lCylTank
        saTotalPerTank   =saDomesPerTank+saCylinderPerTank

        # Calculate the thickness.  Start with pressure
        presTotal = fosMat*(presTank + rhoProp*aMax*lTankLength)
        thkDomesCalc  = presTotal*lRadiusTank/(2*sigMat)
        thkCylCalc    = 2*thkDomesCalc

        # Compare the pressure thickness to the minimum thickness
        thkDomes  = max(thkDomesCalc,thkMin)
        thkCyl    =  max(thkCylCalc,thkMin)

        # Calculate the volume of the material
        volMatDomesPerTank = thkDomes*saDomesPerTank
        volMatCylPerTank   = thkCyl*saCylinderPerTank

        # Calculate the mass of each tank
        mDomesPerTank = volMatDomesPerTank*rhoMat
        mCylPerTank   =volMatCylPerTank*rhoMat

        # Add in the fudge factor
        mTotalPerTank = (mCylPerTank+mDomesPerTank)*(1+pctFudge)
        mTotal        = (mTotalPerTank*nTanks)*(1.1**nTanks)




        # Stuff everything back into "self" for output
        self.strPropType = strPropType
        self.strMatType  = strMatType
        self.nTanks      = nTanks
        self.lMaxRadTank = lMaxRadTank
        self.presTank    = presTank
        self.mPropTotal  = mPropTotal

        self.pctUllage       = pctUllage
        self.rhoProp         = rhoProp
        self.volPropTotal    = volPropTotal
        self.volPropPerTank  = volPropPerTank
        self.volPerTank      = volPerTank
        self.volMaxRadius    = volMaxRadius
        self.lRadiusTank     = lRadiusTank
        self.lCylTank        = lCylTank
        self.lTankLength     = lTankLength
        self.saDomesPerTank     = saDomesPerTank
        self.saCylinderPerTank  = saCylinderPerTank
        self.saTotalPerTank  = saTotalPerTank
        self.presTotal       = presTotal
        self.thkDomesCalc    = thkDomesCalc
        self.thkCylCalc      = thkCylCalc
        self.thkDomes        = thkDomes
        self.thkCyl          = thkCyl
        self.volMatDomesPerTank = volMatDomesPerTank
        self.volMatCylPerTank = volMatCylPerTank
        self.mDomesPerTank   = mDomesPerTank
        self.mCylPerTank     = mCylPerTank
        self.mTotalPerTank   = mTotalPerTank
        self.mTotal          = mTotal