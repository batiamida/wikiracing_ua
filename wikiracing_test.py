import unittest

from wikiracing import WikiRacer


class WikiRacerTest(unittest.TestCase):

    racer = WikiRacer(max_depth=4)

    def test_1(self):
        path = self.racer.find_path('Дружба', 'Рим')
        self.assertEqual(path, ['Дружба', 'Якопо Понтормо', 'Рим'])

    def test_2(self):
        path = self.racer.find_path('Мітохондріальна ДНК', 'Вітамін K')
        self.assertEqual(path, ['Мітохондріальна ДНК', 'Бактерії', 'Вітамін K'])

    def test_3(self):
        path = self.racer.find_path('Марка (грошова одиниця)', 'Китайський календар')
        self.assertEqual(path, ['Марка (грошова одиниця)', '2017', 'Китайський календар'])

    def test_4(self):
        path = self.racer.find_path('Фестиваль', 'Пілястра')
        self.assertEqual(path, ['Фестиваль', 'Бароко', 'Пілястра'])

    def test_5(self):
        path = self.racer.find_path('Дружина (військо)', '6 жовтня')
        self.assertEqual(path, ['Дружина (військо)', 'Друга світова війна', '6 жовтня'])

    # ------------------------------- ADDITIONAL TESTS -------------------------------

    def test_7(self):
        self.racer.change_maxdepth(4)
        path = self.racer.find_path('Марка (грошов одиниця)', 'Чингісхан')
        # There is no such page
        self.assertEqual(path, [])

if __name__ == '__main__':
    unittest.main()
