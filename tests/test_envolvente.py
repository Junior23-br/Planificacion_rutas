import random
import unittest

from src.envolvente.envolvente import envolvente_convexa


class TestCasosAMano(unittest.TestCase):
    def test_cuadrado_con_punto_interior(self):
        pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]
        self.assertEqual(envolvente_convexa(pts), [(0, 0), (4, 0), (4, 4), (0, 4)])

    def test_punto_alineado_sobre_un_lado(self):
        pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (2, 0)]
        self.assertEqual(envolvente_convexa(pts), [(0, 0), (4, 0), (4, 4), (0, 4)])

    def test_hipotenusa_e_interior(self):
        pts = [(0, 0), (6, 0), (0, 6), (3, 3), (1, 1)]
        self.assertEqual(envolvente_convexa(pts), [(0, 0), (6, 0), (0, 6)])

    def test_todos_alineados(self):
        self.assertEqual(envolvente_convexa([(0, 0), (1, 1), (2, 2)]), [(0, 0), (2, 2)])

    def test_repetidos(self):
        pts = [(0, 0), (0, 0), (4, 0), (4, 4), (0, 4), (4, 4)]
        self.assertEqual(envolvente_convexa(pts), [(0, 0), (4, 0), (4, 4), (0, 4)])

    def test_un_punto_o_ninguno(self):
        self.assertEqual(envolvente_convexa([]), [])
        self.assertEqual(envolvente_convexa([(3, 5)]), [(3, 5)])
        self.assertEqual(envolvente_convexa([(3, 5), (3, 5)]), [(3, 5)])

    def test_coordenadas_grandes(self):
        g = 10 ** 9
        pts = [(g, g), (3 * g, g), (3 * g, 3 * g), (g, 3 * g), (2 * g, 2 * g)]
        self.assertEqual(envolvente_convexa(pts), [(g, g), (3 * g, g), (3 * g, 3 * g), (g, 3 * g)])

    def test_sentido_antihorario_desde_menor_x(self):
        res = envolvente_convexa([(5, 1), (1, 1), (3, 6), (3, 3)])
        self.assertEqual(res[0], (1, 1))
        self.assertEqual(res, [(1, 1), (5, 1), (3, 6)])


class TestContraScipy(unittest.TestCase):
    def test_aleatorios(self):
        try:
            import numpy as np
            from scipy.spatial import ConvexHull
        except ImportError:
            self.skipTest("falta scipy")
        rng = random.Random(2026)
        for n in (5, 20, 100, 1000):
            for _ in range(20):
                pts = [(rng.randint(0, 200), rng.randint(0, 200)) for _ in range(n)]
                propio = set(envolvente_convexa(pts))
                unicos = sorted(set(pts))
                if len(unicos) < 3:
                    continue
                try:
                    h = ConvexHull(np.array(unicos, dtype=float))
                except Exception:  # todos alineados: SciPy no la calcula
                    continue
                self.assertEqual(propio, {unicos[i] for i in h.vertices})


if __name__ == "__main__":
    unittest.main()
