import unittest

from src.ruta_optima.itinerario import armar_itinerario

# Todos los desplazamientos cuestan 10 s. Partida 0; atractivos 1, 2 y 3.
T = [[0, 10, 10, 10], [10, 0, 10, 10], [10, 10, 0, 10], [10, 10, 10, 0]]
DUR = {1: 100, 2: 200, 3: 300}


class TestItinerario(unittest.TestCase):
    def test_cabe(self):
        r = armar_itinerario(T, 0, [1, 2, 3], DUR, jornada_s=1000)
        self.assertTrue(r["cabe"])
        self.assertEqual((r["viaje_s"], r["visitas_s"], r["total_s"]), (40, 600, 640))
        self.assertEqual(r["quitados"], [])

    def test_no_cabe_quita_el_que_menos_desperdicia(self):
        # total 640 > 500. Quitar 1 deja 530 (no cabe), quitar 2 deja 430, quitar 3 deja 330.
        # Cabe quitando 2 o 3; se quita el 2 porque deja el total más cercano a 500 (430).
        r = armar_itinerario(T, 0, [1, 2, 3], DUR, jornada_s=500)
        self.assertEqual(r["quitados"], [(2, 640, 430)])
        self.assertEqual(r["total_s"], 430)
        self.assertEqual(sorted(r["atractivos"]), [1, 3])
        self.assertTrue(r["cabe"])

    def test_quita_varios_cuando_hace_falta(self):
        # jornada 250: quitando uno solo no cabe (530, 430, 330); hay que quitar dos
        r = armar_itinerario(T, 0, [1, 2, 3], DUR, jornada_s=250)
        self.assertEqual(len(r["quitados"]), 2)
        self.assertTrue(r["cabe"])


if __name__ == "__main__":
    unittest.main()