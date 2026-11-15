import csv
import os
import random
import unittest

from src.caminos.dijkstra import dijkstra_cola, dijkstra_lineal, reconstruir_ruta, ruta_minima

INF = float("inf")

# Caso de la spec R2 (resuelto a mano): adj[i] = lista de (j, tiempo)
ADJ = [
    [(1, 4.0), (2, 1.0)],   # 0
    [(3, 1.0)],             # 1
    [(1, 2.0), (3, 5.0)],   # 2
    [(4, 3.0)],             # 3
    [],                     # 4
    [(0, 1.0)],             # 5 (a él no llega nadie)
]


def bellman_ford(adj, origen):
    """Implementación propia e independiente para contrastar Dijkstra."""
    n = len(adj)
    d = [INF] * n
    d[origen] = 0.0
    for _ in range(n - 1):
        cambio = False
        for u in range(n):
            if d[u] == INF:
                continue
            for v, w in adj[u]:
                if d[u] + w < d[v]:
                    d[v] = d[u] + w
                    cambio = True
        if not cambio:
            break
    return d


class TestCasoAMano(unittest.TestCase):
    def test_distancias(self):
        for f in (dijkstra_cola, dijkstra_lineal):
            dist, _, _ = f(ADJ, 0)
            self.assertEqual(dist[:5], [0.0, 3.0, 1.0, 4.0, 7.0])
            self.assertEqual(dist[5], INF)

    def test_ruta(self):
        t, ruta, _ = ruta_minima(ADJ, 0, 4)
        self.assertEqual((t, ruta), (7.0, [0, 2, 1, 3, 4]))

    def test_inalcanzable(self):
        t, ruta, _ = ruta_minima(ADJ, 0, 5)
        self.assertEqual((t, ruta), (INF, []))

    def test_misma_cantidad_explorados(self):
        _, _, ex_c = dijkstra_cola(ADJ, 0, 4)
        _, _, ex_l = dijkstra_lineal(ADJ, 0, 4)
        self.assertEqual(ex_c, ex_l)


class TestAleatorios(unittest.TestCase):
    def test_contra_bellman_ford(self):
        rng = random.Random(2026)
        for _ in range(200):
            n = rng.randint(2, 12)
            adj = [[(rng.randrange(n), float(rng.randint(1, 20)))
                    for _ in range(rng.randint(0, 4))] for _ in range(n)]
            o = rng.randrange(n)
            esperado = bellman_ford(adj, o)
            for f in (dijkstra_cola, dijkstra_lineal):
                dist, pred, _ = f(adj, o)
                self.assertEqual(dist, esperado)
            for d in range(n):
                t, ruta, ex_c = ruta_minima(adj, o, d)
                self.assertEqual(t, esperado[d])
                if t < INF:
                    self.assertEqual((ruta[0], ruta[-1]), (o, d))
                _, _, ex_l = dijkstra_lineal(adj, o, d)
                self.assertEqual(ex_c, ex_l)


class TestMatriz(unittest.TestCase):
    def test_formato(self):
        ruta = "data/processed/matriz_tiempos.csv"
        if not os.path.exists(ruta):
            self.skipTest("falta la matriz")
        with open(ruta, encoding="utf-8", newline="") as f:
            filas = list(csv.reader(f))
        ids = filas[0][1:]
        self.assertEqual(len(ids), 40)
        self.assertEqual(len(filas) - 1, 40)
        for i, fila in enumerate(filas[1:]):
            self.assertEqual(fila[0], ids[i])
            self.assertTrue(all(c != "" for c in fila))
            self.assertEqual(float(fila[1 + i]), 0.0)


class TestContraNetworkX(unittest.TestCase):
    def test_pares_del_catalogo(self):
        try:
            import networkx as nx
            import osmnx as ox
            from src.caminos.grafo import cargar_grafo, cargar_lugares
        except ImportError:
            self.skipTest("faltan networkx u osmnx")
        if not os.path.exists("data/processed/componente.graphml"):
            self.skipTest("falta el grafo procesado")
        ids, indice, adj, _ = cargar_grafo()
        G = ox.load_graphml("data/processed/componente.graphml")
        lugares = cargar_lugares(indice)
        rng = random.Random(2026)
        for _ in range(5):
            a, b = rng.sample(lugares, 2)
            t, ruta, _ = ruta_minima(adj, a["idx"], b["idx"])
            esperado = nx.dijkstra_path_length(G, ids[a["idx"]], ids[b["idx"]], weight="travel_time")
            self.assertAlmostEqual(t, esperado, places=6)


if __name__ == "__main__":
    unittest.main()
