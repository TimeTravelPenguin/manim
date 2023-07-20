import numpy as np


def cis(x):
    return np.cos(x) + np.sin(x) * 1j

if __name__ == "__main__":
    z = 1 + 1j
    print(z)
    print(cis(z))