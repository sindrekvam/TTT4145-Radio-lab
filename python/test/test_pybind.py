import fir_filter
import matplotlib.pyplot as plt
import modem
import numpy as np
import pytest


@pytest.mark.parametrize("num_symbols", [4, 16, 64, 256, 1024])
def test_modem(num_symbols):
    qam = modem.Qam(num_symbols)
    qam_lookup_table = np.array(qam.get_lookup_table(), dtype=complex)
    plt.scatter(qam_lookup_table.real, qam_lookup_table.imag)
    plt.show()


def test_matched_filter():
    rrc = fir_filter.RootRaisedCosine(0.5, 4, 4)
    rrc_coeff = np.array(rrc.get_coefficients())

    plt.stem(rrc_coeff)
    plt.show()
