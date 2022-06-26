import numpy as np


class AutoDriver():
    def __init__(self, objectMass, objectMaxThrustForce, objectNeutralBreakForce, desiredDistance):
        self.objectNeutralBreakForce = objectNeutralBreakForce
        self.mass = objectMass
        self.objectMaxThrustForce=objectMaxThrustForce
        self.desiredDistance = desiredDistance
        self.currentThrust = 0

        #Kalman initialization
        self.XtPrev = 0
        self.PtPrev = 0
        self.prevTime = 0
        self.XtPrev2 = 0
        self.PtPrev2 = 0
        self.Q = 0.01
        self.R = 0.3
        self.R2 = 0.04
        self.uk = 0

        self.distanceFilt = 0
        self.thrustFilt = 0

        #PID initialization
        self.Kp = 5
        #self.Ki=self.Kp/Ti
        self.Ki = self.Kp / 1000
        # self.Ki=self.Kp*Td
        self.Kd = self.Kp / 1000
        self.acumulation_e = 0
        self.acumulation_e2 = 0
        self.prev_error = 0
        self.prev_error2=0
        self.PID_factor = 0.01

    def updateMeasurement(self, time, distance):
        # filter za distance
        delta_t=time-self.prevTime
        Xt_est = self.XtPrev + self.uk
        Pt_est = self.PtPrev + self.Q
        y = distance - Xt_est
        K = (Pt_est) / (self.R + Pt_est)
        Xt = Xt_est + K * y
        Pt = (1 - K) * Pt_est
        #update za naslednje filtriranje
        self.XtPrev = Xt
        self.PtPrev = Pt
        #filtered distance
        self.distanceFilt = Xt

        #za PID
        SP=self.desiredDistance
        PV=distance
        #PV=self.distanceFilt
        e=PV-SP
        #e = distance - (self.desiredDistance)
        self.acumulation_e += e


        thrust = self.Kp * e + self.Ki * self.acumulation_e + self.Kd * (e - self.prev_error)
        #e2=thrust - self.currentThrust
        #self.acumulation_e2 += e2
        self.MV = (thrust - self.currentThrust) * self.PID_factor
        #thrust2 = self.Kp * e2 + self.Ki * self.acumulation_e2 + self.Kd * (e2 - self.prev_error2)
        adjusted_thrust = self.currentThrust + self.MV


        Xt_est = self.XtPrev2 + self.uk
        Pt_est = self.PtPrev2 + self.Q
        y = adjusted_thrust - Xt_est
        K = (Pt_est) / (self.R2 + Pt_est)
        Xt = Xt_est + K * y
        Pt = (1 - K) * self.PtPrev  # ?

        # time update
        self.XtPrev2 = Xt
        self.PtPrev2 = Pt
        self.thrustFilt= Xt
        self.currentThrust = max(0, min(0.9, self.thrustFilt))
        self.prev_error = e
        #self.prev_error2 = e2


    # object properties - do not touch!!!
    @property
    def distanceFiltered(self):
        '''
        Tukaj vrnete trenutno oddaljenost ocenjeno z filtri.
        To omogoča kasnejši izris, vrnete vašo interno spremenljivko.
        '''
        return self.distanceFilt

    @property
    def thrust(self):
        '''
        Tukaj vrnete relativno količino moči motorjev, vrednost med 0 in 1.
        '''
        return self.currentThrust