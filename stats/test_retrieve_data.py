import unittest

from numpy.ma.testutils import assert_equal


class TestRetrieveData(unittest.TestCase):
    def test_create_team_list(self):
        from event import create_team_list

        # Test retrieving the teams from Alberta Championship
        teams = create_team_list("CAABCMP")[0] # only retrieve the teams by accessing the first index
        self.assertTrue(len(teams) > 0)

    def test_create_game_matrix(self):
        from opr_epa import create_game_matrix
        from event import create_team_list

        teams = create_team_list("CAABCMP")[0]
        game_matrix = create_game_matrix("CAABCMP", teams)
        sample = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.assertEqual(game_matrix[0], sample)



if __name__ == '__main__':
    unittest.main()
