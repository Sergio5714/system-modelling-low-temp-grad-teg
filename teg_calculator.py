import os
import numpy as np
import pickle
from scipy.optimize import root_scalar

class TegPowerCalculator:
    def __init__(self, alpha, el_res, therm_res, T_aver, dT, therm_res_ext, el_res_parasitic=0):
        # Constructor

        ## Parameters of the thermoelectric module фтв thermal system
        self.alpha = alpha
        self.el_res = el_res
        self.el_res_parasitic = el_res_parasitic
        self.therm_res = therm_res
        self.T_aver = T_aver
        self.dT = dT
        self.dT_tem = dT
        self.therm_res_ext = therm_res_ext
        self.ZT = alpha ** 2 * therm_res / el_res * T_aver

        ## Input voltage accessible range for the power conversion system
        self.input_voltage_range = [0, 0.2]

        ## Upload spline models
        dir_path = os.path.dirname(os.path.abspath(__file__))
        with open(dir_path + '\\' + 'interpolators\\interpolator_1D_eff.pkl', 'rb') as f:
            self.spl_efficiency = pickle.load(f)
        with open(dir_path + '\\' + 'interpolators\\interpolator_1D_imp.pkl', 'rb') as f:
            self.spl_input_resistance = pickle.load(f)

        ## Define the optimized parameters of the model

        ### Coefficients for the linear spproximation of the efficiency "tail"
        self.spl_eff_tail_linear_coef = [-0.49332607889101876, 0.22939273235763408]
        ### Optimal parameters for the efficiency approximation
        self.popt_efficiency = np.array([ 3.86054210e+00,  2.71372329e+00,  9.52156532e-02,  3.99017187e+00,
        2.47051159e+00,  1.97878745e-03, -3.92471024e-03,  5.28872970e-03])
        ### Optimal parameters for input resistance approximation
        self.popt_input_resistance = np.array([ 1.00000000e+00,  3.73786403e+00,  2.27262651e+00, -3.05612960e-03,
       -3.92613447e-03,  5.34495183e-03])

        ## Voltage threshold of 0.2 V for the power converter model
        self.VOLTAGE_THRESHOLD = 0.2

    # Calculate effective thermal resistance of the thermoelectric module
    def calc_therm_res(self, el_res_load):
        R = self.therm_res/(1 + self.ZT/((el_res_load + self.el_res_parasitic)/self.el_res + 1))
        return R
    
    # Calculate 
    def spl_eff_with_linear_tail(self, x):
        x = np.asarray(x).flatten()
        result = self.spl_efficiency(x)
        
        # Check right boundary
        idx = np.argwhere(x > self.input_voltage_range[1])

        # if there is data that exceeds 0.200 V than extrapolaste it
        if idx.shape[0] !=0:
            tail = self.spl_eff_tail_linear_coef[0] * x[idx] + self.spl_eff_tail_linear_coef[1]
            np.put(result, idx.reshape(-1, 1), tail.reshape(-1, 1))
        
        return result.reshape(result.shape[0], )

    # Formula for alpha and beta
    def a_b_function (self, R, a_1, a_2, a_3):
        return a_1/(R + a_2) + a_3

    # Custom function for the efficiency
    def custom_func_efficiency (self, data, a_0, a_1, a_2, b_0, b_1, b_2, c_0, c_1):
        V = data[:, 0]
        R = data[:, 1]
        f = self.a_b_function(R, a_0, a_1, a_2) * self.spl_eff_with_linear_tail(self.a_b_function(R, b_0, b_1, b_2) * (V - (c_0 * R + c_1)))
        return f

    # Custom function for the input resistance
    def custom_func_input_resistance (self, data, a_0, b_0, b_1, b_2, c_0, c_1):
        V = data[:, 0]
        R = data[:, 1]
        f = (a_0) * self.spl_input_resistance(self.a_b_function(R, b_0, b_1, b_2) * (V - (c_0 * R + c_1)))
        return f  

    # Function for root-finding algorithm
    def funct_to_find_root(self, dT_tem):
        r_in = self.custom_func_input_resistance(np.array([self.alpha * dT_tem, self.el_res + self.el_res_parasitic]).reshape(1,-1), 
                                                *self.popt_input_resistance)[0]
        R_eff = self.calc_therm_res(el_res_load=r_in)
        return (dT_tem - self.dT/ (R_eff + self.therm_res_ext) * R_eff)

    # Function for calculation the generated power in mW
    def calc_power_mw(self):
        
        # Calculate numerically temp. diff. across the thermoelectric module
        sol = root_scalar(self.funct_to_find_root, bracket=[0, self.dT], method='brentq')
        self.dT_tem = sol.root

        # Check the boundaries
        if self.alpha * self.dT_tem > self.VOLTAGE_THRESHOLD:
            print("/n The input voltage for the converter is out of range [0 mV, 200 mV].\n")
            print("The output power is forced to 0.\n")
            return 0

        input_V_r = np.array([self.alpha * self.dT_tem, self.el_res + self.el_res_parasitic]).reshape(1,-1)
        eff = self.custom_func_efficiency(input_V_r, *self.popt_efficiency)[0]
        r_in = self.custom_func_input_resistance(input_V_r, *self.popt_input_resistance)

        self.input_volt_teg = (self.alpha * self.dT_tem)

        self.input_volt_dc_dc = (self.alpha * self.dT_tem) / (self.el_res + self.el_res_parasitic + r_in) * r_in
        
        w = eff * (self.alpha * self.dT_tem) ** 2 / (self.el_res + self.el_res_parasitic + r_in)
        return w * 1000

        # Function for calculation the generated power in mW
    def calc_power_conventional_mw(self):
        
        # Calculate temp. diff. across the thermoelectric module

        R_eff = self.therm_res

        self.dT_tem = self.dT/ (R_eff + self.therm_res_ext) * R_eff

        r_in = self.custom_func_input_resistance(np.array([self.alpha * self.dT_tem, self.el_res + self.el_res_parasitic]).reshape(1,-1), 
                                                *self.popt_input_resistance)[0]

        # Check the boundaries
        if self.alpha * self.dT_tem > self.VOLTAGE_THRESHOLD:
            print("/n The input voltage for the converter is out of range [0 mV, 200 mV].\n")
            print("The output power is forced to 0.\n")
            return 0

        input_V_r = np.array([self.alpha * self.dT_tem, self.el_res + self.el_res_parasitic]).reshape(1,-1)
        eff = self.custom_func_efficiency(input_V_r, *self.popt_efficiency)[0]
        r_in = self.custom_func_input_resistance(input_V_r, *self.popt_input_resistance)
        
        w = eff * (self.alpha * self.dT_tem) ** 2 / (self.el_res + self.el_res_parasitic + r_in)
        return w * 1000

    