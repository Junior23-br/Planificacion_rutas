import random
import unittest

from src.ruta_optima.tsp import fuerza_bruta, held_karp, vecino_mas_cercano, tiempo_de_ruta

# Caso 1 de specs/R4_ruta_optima.md (resuelto a mano)
T4 = [
    [0, 10, 15, 20],
    [5, 0, 9, 10],
    [6, 13, 0, 12],
    [8, 8, 9, 0],
]


class TestCaso4Lugares(unittest.TestCase):
    def test_fuerza_bruta(self):
        self.assertEqual(fuerza_bruta(T4, 0, [1, 2, 3]), (35, [0, 1, 3, 2, 0]))

    def test_held_karp(self):
        self.assertEqual(held_karp(T4, 0, [1, 2, 3]), (35, [0, 1, 3, 2, 0]))

    def test_heuristica(self):
        self.assertEqual(vecino_mas_cercano(T4, 0, [1, 2, 3]), (39, [0, 1, 2, 3, 0]))


class TestCasosBorde(unittest.TestCase):
    def test_sin_lugares(self):
        for f in (fuerza_bruta, held_karp, vecino_mas_cercano):
            self.assertEqual(f(T4, 0, []), (0, [0, 0]))

    def test_un_lugar(self):
        for f in (fuerza_bruta, held_karp, vecino_mas_cercano):
            self.assertEqual(f(T4, 0, [2]), (15 + 6, [0, 2, 0]))


class TestCruzado(unittest.TestCase):
    """Fuerza bruta y Held-Karp deben dar el mismo tiempo en matrices asimétricas aleatorias."""

    def test_aleatorio(self):
        rng = random.Random(2026)
        for k in range(1, 9):
            for _ in range(5):
                n = k + 1
                T = [[0 if i == j else rng.randint(1, 100) for j in range(n)] for i in range(n)]
                lugares = list(range(1, n))
                tb, rb = fuerza_bruta(T, 0, lugares)
                th, rh = held_karp(T, 0, lugares)
                self.assertEqual(tb, th)
                self.assertEqual(tiempo_de_ruta(T, rh), th)             # la ruta devuelta suma ese tiempo
                self.assertEqual(sorted(rh[1:-1]), lugares)             # visita todos una vez
                self.assertEqual((rh[0], rh[-1]), (0, 0))
                self.assertGreaterEqual(vecino_mas_cercano(T, 0, lugares)[0], th)  # la heurística no puede ganar


if __name__ == "__main__":
    unittest.main()