import radio

mqam = radio.Qam(16)

assert mqam.demodulate(mqam.modulate(7)) == 7
