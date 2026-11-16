"""Las trazas de la página de Sustentación deben dar lo mismo que los algoritmos del proyecto."""
import random
import unittest

from src.app import simulaciones as sim
from src.caminos.dijkstra import dijkstra_cola, dijkstra_lineal
from src.envolvente.envolvente import envolvente_convexa
from src.ruta_optima.tsp import held_karp, vecino_mas_cercano


def grafo_al_azar(rng, n):
    return [[(v, float(rng.randint(1, 9))) for v in range(n) if v != u and rng.random() < 0.4]
            for u in range(n)]


def matriz_al_azar(rng, n):
    return [[0 if i == j else rng.randint(1, 60) for j in range(n)] for i in range(n)]


class TestTrazaDijkstra(unittest.TestCase):
    def comparar(self, adj, origen, destino):
        for traza, original in ((sim.traza_dijkstra_cola, dijkstra_cola),
                                (sim.traza_dijkstra_lineal, dijkstra_lineal)):
            ultimo = traza(adj, origen, destino)[-1]
            dist, pred, explorados = original(adj, origen, destino)
            self.assertEqual((ultimo["dist"], ultimo["pred"], ultimo["explorados"]),
                             (dist, pred, explorados))

    def test_caso_del_spec(self):
        self.comparar(sim.GRAFO_EJEMPLO, 0, None)
        self.comparar(sim.GRAFO_EJEMPLO, 0, 4)
        self.assertEqual(sim.traza_dijkstra_cola(sim.GRAFO_EJEMPLO, 0)[-1]["dist"][:5],
                         [0.0, 3.0, 1.0, 4.0, 7.0])

    def test_grafos_al_azar(self):
        rng = random.Random(2026)
        for _ in range(40):
            n = rng.randint(2, 9)
            adj = grafo_al_azar(rng, n)
            self.comparar(adj, rng.randrange(n), rng.choice([None] + list(range(n))))


class TestTrazaEnvolvente(unittest.TestCase):
    def test_mismo_resultado(self):
        rng = random.Random(2026)
        for n in list(range(1, 12)) + [20, 40]:
            puntos = [(rng.randint(0, 30), rng.randint(0, 30)) for _ in range(n)]
            unicos, pasos = sim.traza_envolvente(puntos)
            self.assertEqual(pasos[-1]["casco"], envolvente_convexa(puntos))
            self.assertEqual((pasos[-1]["lo"], pasos[-1]["hi"]), (0, len(unicos)))

    def test_puntos_al_azar_son_distintos(self):
        puntos = sim.puntos_al_azar(16, 2026)
        self.assertEqual(len(set(puntos)), 16)
        self.assertEqual(puntos, sim.puntos_al_azar(16, 2026))


class TestTrazasTSP(unittest.TestCase):
    def test_caso_del_spec(self):
        hk = sim.traza_held_karp(sim.MATRIZ_EJEMPLO, 0, [1, 2, 3])[-1]
        self.assertEqual((hk["total"], hk["ruta"]), (35, [0, 1, 3, 2, 0]))
        vm = sim.traza_vecino(sim.MATRIZ_EJEMPLO, 0, [1, 2, 3])[-1]
        self.assertEqual((vm["acumulado"], vm["ruta"]), (39, [0, 1, 2, 3, 0]))

    def test_matrices_al_azar(self):
        rng = random.Random(2026)
        for _ in range(30):
            n = rng.randint(2, 7)
            T = matriz_al_azar(rng, n)
            lugares = list(range(1, n))
            hk = sim.traza_held_karp(T, 0, lugares)[-1]
            self.assertEqual((hk["total"], hk["ruta"]), held_karp(T, 0, lugares))
            vm = sim.traza_vecino(T, 0, lugares)[-1]
            self.assertEqual((vm["acumulado"], vm["ruta"]), vecino_mas_cercano(T, 0, lugares))


if __name__ == "__main__":
    unittest.main()
