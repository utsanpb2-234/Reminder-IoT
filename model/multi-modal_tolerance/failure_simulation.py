# simulate sensor failure, data pollution, and latency mismatch
import numpy as np


def simulate_sensor_failure(data):
    """
    simulate sensor failure by replacing the data of the specified sensor with zeros. 
    """
    data_failed = np.zeros_like(data)
    
    return data_failed


def simulate_data_pollution(data, noise_level=0.2):
    """
    simulate data pollution by adding random noise to one sensor's data.
    noise_level: standard deviation of the added Gaussian noise
    """
    noise = np.random.normal(0, noise_level, size=data.shape)

    data_polluted = data + noise

    return data_polluted


def simulate_latency_mismatch(cur_data, prev_data, delay_steps=1):
    """
    simulate latency mismatch by shifting the data of one sensor by a number of steps.
    """
    cur_data = np.roll(cur_data, shift=delay_steps, axis=0)

    cur_data[:delay_steps] = prev_data[-delay_steps:]

    return cur_data


if __name__ == "__main__":
    # example usage
    tof_data = np.random.rand(5, 1)
    thermal_data = np.random.rand(5, 5)
    print(f"original ToF data:\n{tof_data}")
    print(f"original Thermal data:\n{thermal_data}")

    previous_thermal = np.zeros_like(thermal_data)
    previous_tof = np.zeros_like(tof_data)
    print(f"previous_thermal:\n{previous_thermal}")
    print(f"previous_tof:\n{previous_tof}")

    # simulate sensor failure
    tof_data_failed = simulate_sensor_failure(tof_data)
    thermal_data_failed = simulate_sensor_failure(thermal_data)
    print(f"failed ToF data:\n{tof_data_failed}")
    print(f"failed Thermal data:\n{thermal_data_failed}")
    
    # simulate data pollution
    tof_data_polluted = simulate_data_pollution(tof_data, noise_level=1)
    thermal_data_polluted = simulate_data_pollution(thermal_data, noise_level=1)
    print(f"polluted ToF data:\n{tof_data_polluted}")
    print(f"polluted Thermal data:\n{thermal_data_polluted}")

    # simulate latency mismatch
    tof_data_latency = simulate_latency_mismatch(tof_data, previous_tof, delay_steps=2)
    thermal_data_latency = simulate_latency_mismatch(thermal_data, previous_thermal, delay_steps=2)
    print(f"latency ToF data:\n{tof_data_latency}")
    print(f"latency Thermal data:\n{thermal_data_latency}")
