import raiseAp as ff

cAp=float(input('Enter the current Apoapsis in Km: '))
dV=ff.raiseAp(cAp)
print('The change in velocity required to reach 410000km Apoapsis is ', str(round(dV,3)), ' m/s')
