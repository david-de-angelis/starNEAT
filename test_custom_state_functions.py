import unittest
from unittest.mock import patch
from types import SimpleNamespace as dynObj
from catanatron.game import Color, Player
from catanatron.models.enums import BuildingType

import constants
import custom_state_functions as csf


class TestCustomStateFunctions(unittest.TestCase):

#region setUp / tearDown
    @classmethod
    def setUpClass(cls):
        pass
    def setUp(self):
        pass
    def tearDown(self):
        pass
    @classmethod
    def tearDownClass(cls):
        pass
#endregion

    def test_get_trinary_road_ownership(test):
      game = dynObj()
      game.state = dynObj()
      game.state.board = dynObj()
      game.state.board.roads = { 
        (0 , 1 ): Color.BLUE , (1 , 0 ): Color.BLUE ,
        (33, 34): Color.BLUE , (34, 33): Color.BLUE , 
        (17, 39): Color.RED  , (39, 17): Color.RED  ,
        (1 , 2 ): Color.RED  , (2 , 1 ): Color.RED  ,
        (15, 17): Color.WHITE, (17, 15): Color.WHITE,
        (39, 41): Color.WHITE, (41, 39): Color.WHITE
      }

      # Retrieve Trinary Road Ownership from Blue Perspective
      result = csf.get_trinary_road_ownership(game, Color.BLUE)

      # Blue Roads
      test.assertEqual(result[constants.road_tuple_to_index[0 , 1 ]], 1, "should be marked as owned (1)")
      test.assertEqual(result[constants.road_tuple_to_index[33, 34]], 1, "should be marked as owned (1)")

      # Unowned Roads
      test.assertEqual(result[constants.road_tuple_to_index[2 , 3 ]], 0, "should be marked as vacant (0)")
      test.assertEqual(result[constants.road_tuple_to_index[3 , 12]], 0, "should be marked as vacant (0)")

      # Red Roads
      test.assertEqual(result[constants.road_tuple_to_index[17, 39]], -1, "should be marked as enemy-owned (-1)")
      test.assertEqual(result[constants.road_tuple_to_index[1 , 2 ]], -1, "should be marked as enemy-owned (-1)")

      # White Roads
      test.assertEqual(result[constants.road_tuple_to_index[15, 17]], -1, "should be marked as enemy-owned (-1)")
      test.assertEqual(result[constants.road_tuple_to_index[39, 41]], -1, "should be marked as enemy-owned (-1)")
      

      # Retrieve Trinary Road Ownership from Another (Red) Perspective
      result = csf.get_trinary_road_ownership(game, Color.RED)

      # Blue Roads
      test.assertEqual(result[constants.road_tuple_to_index[0 , 1 ]], -1, "should be marked as enemy-owned (-1)")
      test.assertEqual(result[constants.road_tuple_to_index[33, 34]], -1, "should be marked as enemy-owned (-1)")

      # Unowned Roads
      test.assertEqual(result[constants.road_tuple_to_index[2 , 3 ]], 0, "should be marked as vacant (0)")
      test.assertEqual(result[constants.road_tuple_to_index[3 , 12]], 0, "should be marked as vacant (0)")

      # Red Roads
      test.assertEqual(result[constants.road_tuple_to_index[17, 39]], 1, "should be marked as owned (1)")
      test.assertEqual(result[constants.road_tuple_to_index[1 , 2 ]], 1, "should be marked as owned (1)")

      # White Roads
      test.assertEqual(result[constants.road_tuple_to_index[15, 17]], -1, "should be marked as enemy-owned (-1)")
      test.assertEqual(result[constants.road_tuple_to_index[39, 41]], -1, "should be marked as enemy-owned (-1)")


    def test_get_all_road_allocation(test):
      game = dynObj()
      game.state = dynObj()
      game.state.players = [Player(Color.BLUE), Player(Color.RED), Player(Color.WHITE)]
      game.state.board = dynObj()
      game.state.board.roads = { 
        (0 , 1 ): Color.BLUE , (1 , 0 ): Color.BLUE ,
        (33, 34): Color.BLUE , (34, 33): Color.BLUE , 
        (17, 39): Color.RED  , (39, 17): Color.RED  ,
        (1 , 2 ): Color.RED  , (2 , 1 ): Color.RED  ,
        (15, 17): Color.WHITE, (17, 15): Color.WHITE,
        (39, 41): Color.WHITE, (41, 39): Color.WHITE
      }

      # Retrieve all road allocations from Blue Perspective
      result = csf.get_all_road_allocation(game, Color.BLUE)

      test.assertEqual(len(result), len(game.state.players), "the returned array should have the same number elements as there were players")

      # Blue Road Ownership
      focus = result[0]
      test.assertEqual(len(focus), 72)

      test.assertEqual(focus[constants.road_tuple_to_index[0 , 1 ]], 1, "should be marked as owned (1)")
      test.assertEqual(focus[constants.road_tuple_to_index[33, 34]], 1, "should be marked as owned (1)")

      test.assertEqual(focus[constants.road_tuple_to_index[2 , 3 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[3 , 12]], 0, "should be marked as not owned (0)")
      
      test.assertEqual(focus[constants.road_tuple_to_index[17, 39]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[1 , 2 ]], 0, "should be marked as not owned (0)")

      test.assertEqual(focus[constants.road_tuple_to_index[15, 17]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[39, 41]], 0, "should be marked as not owned (0)")

      # Red Road Ownership
      focus = result[1]
      test.assertEqual(len(focus), 72)

      test.assertEqual(focus[constants.road_tuple_to_index[0 , 1 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[33, 34]], 0, "should be marked as not owned (0)")

      test.assertEqual(focus[constants.road_tuple_to_index[2 , 3 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[3 , 12]], 0, "should be marked as not owned (0)")
      
      test.assertEqual(focus[constants.road_tuple_to_index[17, 39]], 1, "should be marked as owned (1)")
      test.assertEqual(focus[constants.road_tuple_to_index[1 , 2 ]], 1, "should be marked as owned (1)")

      test.assertEqual(focus[constants.road_tuple_to_index[15, 17]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[39, 41]], 0, "should be marked as not owned (0)")

      # White Road Ownership
      focus = result[2]
      test.assertEqual(len(focus), 72)

      test.assertEqual(focus[constants.road_tuple_to_index[0 , 1 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[33, 34]], 0, "should be marked as not owned (0)")

      test.assertEqual(focus[constants.road_tuple_to_index[2 , 3 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[3 , 12]], 0, "should be marked as not owned (0)")
      
      test.assertEqual(focus[constants.road_tuple_to_index[17, 39]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[1 , 2 ]], 0, "should be marked as not owned (0)")

      test.assertEqual(focus[constants.road_tuple_to_index[15, 17]], 1, "should be marked as owned (1)")
      test.assertEqual(focus[constants.road_tuple_to_index[39, 41]], 1, "should be marked as owned (1)")


    def test_get_enemy_road_allocation(test):
      game = dynObj()
      game.state = dynObj()
      game.state.players = [Player(Color.BLUE), Player(Color.RED), Player(Color.WHITE)]
      game.state.board = dynObj()
      game.state.board.roads = { 
        (0 , 1 ): Color.BLUE , (1 , 0 ): Color.BLUE ,
        (33, 34): Color.BLUE , (34, 33): Color.BLUE , 
        (17, 39): Color.RED  , (39, 17): Color.RED  ,
        (1 , 2 ): Color.RED  , (2 , 1 ): Color.RED  ,
        (15, 17): Color.WHITE, (17, 15): Color.WHITE,
        (39, 41): Color.WHITE, (41, 39): Color.WHITE
      }

      # Retrieve all road allocations from Blue Perspective
      result = csf.get_enemy_road_allocation(game, Color.BLUE)

      test.assertEqual(len(result), len(game.state.players) - 1, "the returned array should have one less number of elements as there were players")

      # Red Road Ownership
      focus = result[0]
      test.assertEqual(len(focus), 72)

      test.assertEqual(focus[constants.road_tuple_to_index[0 , 1 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[33, 34]], 0, "should be marked as not owned (0)")

      test.assertEqual(focus[constants.road_tuple_to_index[2 , 3 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[3 , 12]], 0, "should be marked as not owned (0)")
      
      test.assertEqual(focus[constants.road_tuple_to_index[17, 39]], 1, "should be marked as owned (1)")
      test.assertEqual(focus[constants.road_tuple_to_index[1 , 2 ]], 1, "should be marked as owned (1)")

      test.assertEqual(focus[constants.road_tuple_to_index[15, 17]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[39, 41]], 0, "should be marked as not owned (0)")

      # White Road Ownership
      focus = result[1]
      test.assertEqual(len(focus), 72)

      test.assertEqual(focus[constants.road_tuple_to_index[0 , 1 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[33, 34]], 0, "should be marked as not owned (0)")

      test.assertEqual(focus[constants.road_tuple_to_index[2 , 3 ]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[3 , 12]], 0, "should be marked as not owned (0)")
      
      test.assertEqual(focus[constants.road_tuple_to_index[17, 39]], 0, "should be marked as not owned (0)")
      test.assertEqual(focus[constants.road_tuple_to_index[1 , 2 ]], 0, "should be marked as not owned (0)")

      test.assertEqual(focus[constants.road_tuple_to_index[15, 17]], 1, "should be marked as owned (1)")
      test.assertEqual(focus[constants.road_tuple_to_index[39, 41]], 1, "should be marked as owned (1)")


    def test_get_own_cities(test):
      game = dynObj()
      game.state = dynObj()
      game.state.board = dynObj()
      game.state.board.buildings = { 
        0: (Color.BLUE , BuildingType.CITY),
        1: (Color.BLUE , BuildingType.SETTLEMENT),
        2: (Color.RED  , BuildingType.CITY),
        3: (Color.RED  , BuildingType.SETTLEMENT),
        4: (Color.WHITE, BuildingType.CITY),
        5: (Color.WHITE, BuildingType.SETTLEMENT),
      }

      #Blue perspective
      result = csf.get_own_cities(game, Color.BLUE)
      test.assertEqual(len(result), 54, "should be data for all 54 nodes")

      test.assertEqual(result[0], 1, "should have a city at this node")
      test.assertEqual(result[1], 0, "should not detect settlements")
      test.assertEqual(result[2], 0, "should not detect enemy cities")
      test.assertEqual(result[3], 0, "should not detect enemy settlements")
      test.assertEqual(result[4], 0, "should not detect enemy cities")
      test.assertEqual(result[5], 0, "should not detect enemy settlements")


    # def test_monthly_schedule(self):
    #     with patch('employee.requests.get') as mocked_get:
    #         mocked_get.return_value.ok = True
    #         mocked_get.return_value.text = 'Success'

    #         schedule = self.emp_1.monthly_schedule('May')
    #         mocked_get.assert_called_with('http://company.com/Schafer/May')
    #         self.assertEqual(schedule, 'Success')

    #         mocked_get.return_value.ok = False

    #         schedule = self.emp_2.monthly_schedule('June')
    #         mocked_get.assert_called_with('http://company.com/Smith/June')
    #         self.assertEqual(schedule, 'Bad Response!')


if __name__ == '__main__':
    unittest.main()