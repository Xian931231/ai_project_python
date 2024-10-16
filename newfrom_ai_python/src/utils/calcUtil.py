import numpy as np

# 코사인 유사도 계산
def cosineSimilarity(v1, v2):
    vector1 = np.array(v1)
    vector2 = np.array(v2)

    dotProduct = np.dot(vector1, vector2)

    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)

    return dotProduct / (magnitude1 * magnitude2)