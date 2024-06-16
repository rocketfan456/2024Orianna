def raiseAp(cAp):
  ''' Calculates the dV required to reach 410000km apoapsis'''
  EarthR=6378  #Radius of earth
  u=398600 #gravitational parameter
  r=EarthR+185

  # current V

  cA=(r+EarthR+cAp)/2 #current semi-major axis
  cV=(u*((2/r)-(1/cA)))**0.5 #current Velocity km/s

  # goal V
  gA=(r+EarthR+410000)/2 #goal semi-major axis
  gV=(u*((2/r)-(1/gA)))**0.5 #goal Velocity km/s

  # dV in m/s
  dV=(gV-cV)*1000
  return dV