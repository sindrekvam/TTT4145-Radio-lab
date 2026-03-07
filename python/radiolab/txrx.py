import time

import adi
import fir_filter
import matplotlib.pyplot as plt
import modem
import numpy as np
from scipy import signal


def connect_and_configure_pluto() -> adi.Pluto:
    """Connect to an Adalm Pluto software defined radio and configure it"""
    sdr = adi.Pluto()

    # Configure properties
    sdr.rx_rf_bandwidth = 4000000
    sdr.rx_lo = 2000000000
    sdr.tx_lo = 2000000000
    sdr.tx_cyclic_buffer = True
    sdr.tx_hardwaregain_chan0 = -30
    sdr.gain_control_mode_chan0 = "slow_attack"

    return sdr


def main():
    sps = 8
    num_symbols = 1024 // sps

    # Instantiate pulse shaping filter
    rrc = fir_filter.RootRaisedCosine(0.2, 10, sps)
    rrc_coeff = np.array(rrc.get_coefficients())

    M = 16
    qam = modem.Qam(M)

    qpsk = modem.Qam(4)

    # Instantiate Data
    data = np.random.randint(M, size=num_symbols)

    # Modulate data
    # TODO: Do this better in Cpp
    modulated_data = np.zeros_like(data, dtype=complex)
    for idx, val in enumerate(data):
        modulated_data[idx] = qam.modulate(val)

    # Oversample data
    oversampled_data = np.zeros((num_symbols * sps,), dtype=complex)
    oversampled_data[::sps] = modulated_data

    # Pule shape data
    pulse_shaped_data = np.convolve(oversampled_data, rrc_coeff, mode="same")

    sdr = connect_and_configure_pluto()
    # Read properties
    print("RX LO %s" % (sdr.rx_lo))

    # Create a sinewave waveform
    fs = int(sdr.sample_rate)
    print(fs)
    # N = 1024
    # fc = int(3000000 / (fs / N)) * (fs / N)
    # ts = 1 / float(fs)
    # t = np.arange(0, N * ts, ts)
    # i = np.cos(2 * np.pi * t * fc) * 2**14
    # q = np.sin(2 * np.pi * t * fc) * 2**14
    # iq = i + 1j * q
    # data = np.arange(0, N) % 16
    # iq = np.zeros((N,), dtype=complex)
    # for i, t in enumerate(data):
    #     iq[i] = m16_qam.modulate(t)
    # print(iq)

    # iq = np.zeros_like(iq)
    # Send data
    sdr.tx(pulse_shaped_data)

    # Collect data
    for r in range(20):
        x = sdr.rx()
        print(x.shape, x)
        f, Pxx_den = signal.periodogram(x, fs)
        plt.clf()
        plt.plot(f, 10 * np.log10(Pxx_den))
        # plt.ylim([1e-7, 1e2])
        plt.ylim([-100, 10])
        plt.xlabel("frequency [Hz]")
        # plt.ylabel("PSD [V**2/Hz]")
        plt.ylabel("PSD [dB/Hz]")
        plt.draw()
        plt.pause(0.05)
        time.sleep(0.1)

    plt.show()


main()
