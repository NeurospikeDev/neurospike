from hh_output import HHOutput

import numpy as np
import sys


DEFAULT_NUM_TIMEPOINTS = 101
DEFAULT_NUM_VOLTAGE_POINTS = 101

# Default voltages are in mV
DEFAULT_RESTING_VOLTAGE = -65

# Capacitance and Ohms in microfarads and ohms respectively
DEFAULT_MEMBRANE_CAPACITANCE = 1
DEFAULT_MEMBRANE_RESISTANCE = 4

# Simulation duration in ms
DEFAULT_SIMULATION_DURATION = 100
DEFAULT_RESOLUTION = 1000

# Reversal potentials in mV
DEFAULT_REVERSAL_POTENTIAL_NA = 50
DEFAULT_REVERSAL_POTENTIAL_K = -77
DEFAULT_REVERSAL_POTENTIAL_LEAK = -54.387

# Default conductances in mS / cm^2
DEFAULT_CONDUCTANCE_NA = 120
DEFAULT_CONDUCTANCE_K = 36
DEFAULT_CONDUCTANCE_LEAK = 0.3 

class HHModel:
    """
    Hodg_kin-Huxley Simulation Module for Neurospike. Provides
    HH Model support for Neurospike simulation app
    """
    @staticmethod
    def simulate(
        initial_v=DEFAULT_RESTING_VOLTAGE,
        membrane_c=DEFAULT_MEMBRANE_CAPACITANCE,
        e_na=DEFAULT_REVERSAL_POTENTIAL_NA,
        e_k=DEFAULT_REVERSAL_POTENTIAL_K,
        e_leak=DEFAULT_CONDUCTANCE_LEAK,
        g_na=DEFAULT_CONDUCTANCE_NA,
        g_k=DEFAULT_CONDUCTANCE_K,
        g_leak=DEFAULT_CONDUCTANCE_LEAK,
        simulation_duration=DEFAULT_SIMULATION_DURATION,
        resolution=DEFAULT_RESOLUTION,
        pulses=list()
    ):
        """
        Runs HH model simulation given the following data:
            - Threshold voltage (mV)
            - Resting voltage (mV)
            - Membrane capacitance (Microfarads)
            - Membrane resistance (Ohms)
            - Pulses object
        """
        num_points = (simulation_duration * resolution)
        if num_points == 0:
            return [[], []]

        dt = simulation_duration / num_points
        time_vec = np.linspace(0, simulation_duration, num_points)
        current_vec = np.zeros(len(time_vec))

        for pulse in pulses:
            pulse_start = pulse["start"]
            pulse_end = pulse["end"]
            pulse_amplitude = pulse["amp"]

            # Determining indices to apply pulse
            pulse_start_idx = pulse_start * resolution
            pulse_end_idx = pulse_end * resolution
            pulse_app_indices = [range(pulse_start_idx, pulse_end_idx)]
            pulse_vec = np.zeros(len(pulse_app_indices))
            pulse_vec.fill(pulse_amplitude)
            np.put(current_vec, pulse_app_indices, pulse_vec)

        # The following code is attributed to Robert Rosenbaum
        # and his work which can be found at the following repo:
        # https://github.com/RobertRosenbaum/ModelingNeuralCircuits/blob/main/Hodg_kinHuxley.ipynb
        
        # We don't parameterise alpha and beta
        # due to the complexity in their origin and tendency to
        # arise from experimental fitting

        # Define gating variables as inline functions
        alphan = lambda V: .01*(V+55)/(1-np.exp(-.1*(V+55)))
        betan = lambda V: .125*np.exp(-.0125*(V+65))
        alpham = lambda V: .1*(V+40)/(1-np.exp(-.1*(V+40)))
        betam = lambda V: 4*np.exp(-.0556*(V+65))
        alphah = lambda V: .07*np.exp(-.05*(V+65))
        betah = lambda V: 1/(1+np.exp(-.1*(V+35)))


        # n variable
        ninfty= lambda V: (alphan(V)/(alphan(V)+betan(V)))
        taun= lambda V: (1/(alphan(V)+betan(V)))
        minfty= lambda V: (alpham(V)/(alpham(V)+betam(V)))
        taum= lambda V: (1/(alpham(V)+betam(V)))
        hinfty= lambda V: (alphah(V)/(alphah(V)+betah(V)))
        tauh= lambda V: (1/(alphah(V)+betah(V)))
        
        # Initial conditions near their fixed points when Ix=0
        V0=-65.0
        n0=ninfty(V0)
        m0=minfty(V0)
        h0=hinfty(V0)

        # Currents
        IL= lambda V: (-g_leak*(V-DEFAULT_REVERSAL_POTENTIAL_LEAK))
        IK = lambda n,V: (-g_k*n **4*(V-DEFAULT_REVERSAL_POTENTIAL_K))
        INa = lambda m,h,V: (-g_na*m **3*h*(V-DEFAULT_REVERSAL_POTENTIAL_NA))

        # Toal ion currents
        Iion = lambda n,m,h,V: IL(V)+IK(n,V)+INa(m,h,V)

        # Euler solver
        V=np.zeros_like(time_vec)
        n=np.zeros_like(time_vec)
        m=np.zeros_like(time_vec)
        h=np.zeros_like(time_vec)
        V[0]=V0
        n[0]=n0
        m[0]=m0
        h[0]=h0

        for i in range(len(time_vec)-1):
            # Update gating variables
            n[i+1]=n[i]+dt*((1-n[i])*alphan(V[i])-n[i]*betan(V[i]))
            m[i+1]=m[i]+dt*((1-m[i])*alpham(V[i])-m[i]*betam(V[i]))
            h[i+1]=h[i]+dt*((1-h[i])*alphah(V[i])-h[i]*betah(V[i]))

            # Update membrane potential
            V[i+1]=V[i]+dt*(Iion(n[i],m[i],h[i],V[i])+current_vec[i])/membrane_c

        # Create output instance
        simulation_output = HHOutput()
        simulation_output.set_membrane_voltage(V)
        simulation_output.set_timepoints(time_vec)
        simulation_output.set_injected_current(current_vec)
        sys.stdout.write(simulation_output.jsonify())
        sys.stdout.write('\n')
        return [V, time_vec]