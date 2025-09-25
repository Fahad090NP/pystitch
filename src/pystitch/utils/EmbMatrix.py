import math
from typing import List, Optional, Union, Tuple, Any

# Type alias for matrix representation
Matrix = Union[Tuple[float, float, float, float, float, float, float, float, float], List[float]]

class EmbMatrix:
    def __init__(self, m: Optional[Matrix] = None):
        if m is None:
            self.m: Matrix = self.get_identity()
        else:
            self.m = m

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EmbMatrix):
            return False
        return self.m == other.m

    def __matmul__(self, other: 'EmbMatrix') -> 'EmbMatrix':
        return EmbMatrix(EmbMatrix.matrix_multiply(self.m, other.m))  # type: ignore

    def __rmatmul__(self, other: 'EmbMatrix') -> 'EmbMatrix':
        return EmbMatrix(EmbMatrix.matrix_multiply(self.m, other.m))  # type: ignore

    def __imatmul__(self, other: 'EmbMatrix') -> None:
        self.m = EmbMatrix.matrix_multiply(self.m, other.m)  # type: ignore

    def __str__(self) -> str:
        return "[%3f, %3f, %3f\n %3f, %3f, %3f\n %3f, %3f, %3f]" % self.m

    def get_matrix(self) -> Matrix:
        return self.m

    def reset(self) -> None:
        self.m = self.get_identity()

    def inverse(self) -> None:
        m = self.m
        m48s75 = m[4] * m[8] - m[7] * m[5]  # type: ignore
        m38s56 = m[5] * m[6] - m[3] * m[8]  # type: ignore
        m37s46 = m[3] * m[7] - m[4] * m[6]  # type: ignore
        det = m[0] * m48s75 + m[1] * m38s56 + m[2] * m37s46  # type: ignore
        inverse_det = 1.0 / float(det)
        self.m = [
            m48s75 * inverse_det,
            (m[2] * m[7] - m[1] * m[8]) * inverse_det,  # type: ignore
            (m[1] * m[5] - m[2] * m[4]) * inverse_det,  # type: ignore
            m38s56 * inverse_det,
            (m[0] * m[8] - m[2] * m[6]) * inverse_det,  # type: ignore
            (m[3] * m[2] - m[0] * m[5]) * inverse_det,  # type: ignore
            m37s46 * inverse_det,
            (m[6] * m[1] - m[0] * m[7]) * inverse_det,  # type: ignore
            (m[0] * m[4] - m[3] * m[1]) * inverse_det,  # type: ignore
        ]

    def post_scale(self, sx: float = 1, sy: Optional[float] = None, x: float = 0, y: float = 0) -> None:
        if sy is None:
            sy = sx
        if x == 0 and y == 0:
            self.m = self.matrix_multiply(self.m, self.get_scale(sx, sy))  # type: ignore
        else:
            self.post_translate(-x, -y)
            self.post_scale(sx, sy)
            self.post_translate(x, y)

    def post_translate(self, tx: float, ty: float) -> None:
        self.m = self.matrix_multiply(self.m, self.get_translate(tx, ty))  # type: ignore

    def post_rotate(self, theta: float, x: float = 0, y: float = 0) -> None:
        if x == 0 and y == 0:
            self.m = self.matrix_multiply(self.m, self.get_rotate(theta))  # type: ignore
        else:
            self.post_translate(-x, -y)
            self.post_rotate(theta)
            self.post_translate(x, y)

    def post_cat(self, matrix_list: List[Matrix]) -> None:
        for mx in matrix_list:
            self.m = self.matrix_multiply(self.m, mx)  # type: ignore

    def pre_scale(self, sx: float = 1, sy: Optional[float] = None) -> None:
        if sy is None:
            sy = sx
        self.m = self.matrix_multiply(self.get_scale(sx, sy), self.m)  # type: ignore

    def pre_translate(self, tx: float, ty: float) -> None:
        self.m = self.matrix_multiply(self.get_translate(tx, ty), self.m)  # type: ignore

    def pre_rotate(self, theta: float) -> None:
        self.m = self.matrix_multiply(self.get_rotate(theta), self.m)  # type: ignore

    def pre_cat(self, matrix_list: List[Matrix]) -> None:
        for mx in matrix_list:
            self.m = self.matrix_multiply(mx, self.m)  # type: ignore

    def point_in_matrix_space(self, v0: Any, v1: Optional[Any] = None) -> List[float]:
        m = self.m
        if v1 is None:
            try:
                return [
                    v0[0] * m[0] + v0[1] * m[3] + 1 * m[6],  # type: ignore
                    v0[0] * m[1] + v0[1] * m[4] + 1 * m[7],  # type: ignore
                    v0[2],  # type: ignore
                ]
            except (IndexError, TypeError):
                return [
                    v0[0] * m[0] + v0[1] * m[3] + 1 * m[6],  # type: ignore
                    v0[0] * m[1] + v0[1] * m[4] + 1 * m[7]  # type: ignore
                    # Must not have had a 3rd element.
                ]
        return [v0 * m[0] + v1 * m[3] + 1 * m[6], v0 * m[1] + v1 * m[4] + 1 * m[7]]  # type: ignore

    def apply(self, v: Any) -> None:
        m = self.m
        nx = v[0] * m[0] + v[1] * m[3] + 1 * m[6]  # type: ignore
        ny = v[0] * m[1] + v[1] * m[4] + 1 * m[7]  # type: ignore
        v[0] = nx  # type: ignore
        v[1] = ny  # type: ignore

    @staticmethod
    def get_identity() -> Tuple[float, float, float, float, float, float, float, float, float]:
        return 1, 0, 0, 0, 1, 0, 0, 0, 1  # identity

    @staticmethod
    def get_scale(sx: float, sy: Optional[float] = None) -> Tuple[float, float, float, float, float, float, float, float, float]:
        if sy is None:
            sy = sx
        return sx, 0, 0, 0, sy, 0, 0, 0, 1

    @staticmethod
    def get_translate(tx: float, ty: float) -> Tuple[float, float, float, float, float, float, float, float, float]:
        return 1, 0, 0, 0, 1, 0, tx, ty, 1

    @staticmethod
    def get_rotate(theta: float) -> Tuple[float, float, float, float, float, float, float, float, float]:
        tau = math.pi * 2
        theta *= tau / 360
        ct = math.cos(theta)
        st = math.sin(theta)
        return ct, st, 0, -st, ct, 0, 0, 0, 1

    @staticmethod
    def matrix_multiply(m0: Matrix, m1: Matrix) -> List[float]:
        return [
            m0[0] * m1[0] + m0[1] * m1[3] + m0[2] * m1[6],  # type: ignore
            m0[0] * m1[1] + m0[1] * m1[4] + m0[2] * m1[7],  # type: ignore
            m0[0] * m1[2] + m0[1] * m1[5] + m0[2] * m1[8],  # type: ignore
            m0[3] * m1[0] + m0[4] * m1[3] + m0[5] * m1[6],  # type: ignore
            m0[3] * m1[1] + m0[4] * m1[4] + m0[5] * m1[7],  # type: ignore
            m0[3] * m1[2] + m0[4] * m1[5] + m0[5] * m1[8],  # type: ignore
            m0[6] * m1[0] + m0[7] * m1[3] + m0[8] * m1[6],  # type: ignore
            m0[6] * m1[1] + m0[7] * m1[4] + m0[8] * m1[7],  # type: ignore
            m0[6] * m1[2] + m0[7] * m1[5] + m0[8] * m1[8],  # type: ignore
        ]
