import numpy as np
cimport numpy as np
from scipy.stats import pearsonr


def similarity(np.ndarray[np.int_t, ndim=1] pattern, np.ndarray[np.int_t, ndim=1] target_pattern):
    if len(pattern) != len(target_pattern):
        return 0
    correlation, _ = pearsonr(pattern, target_pattern)
    similarity = max(0, correlation * 100)
    return similarity
