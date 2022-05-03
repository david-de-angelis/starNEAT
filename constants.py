#initialising all roads into the dictionary, with a default value of un-owned (0)
all_roads = { 
  0:  0,
  1:  0,
  2:  0,
  3:  0,
  4:  0,
  5:  0,
  6:  0,
  7:  0,
  8:  0,
  9:  0,
  10: 0,
  11: 0,
  12: 0,
  13: 0,
  14: 0,
  15: 0,
  16: 0,
  17: 0,
  18: 0,
  19: 0,
  20: 0,
  21: 0,
  22: 0,
  23: 0,
  24: 0,
  25: 0,
  26: 0,
  27: 0,
  28: 0,
  29: 0,
  30: 0,
  31: 0,
  32: 0,
  33: 0,
  34: 0,
  35: 0,
  36: 0,
  37: 0,
  38: 0,
  39: 0,
  40: 0,
  41: 0,
  42: 0,
  43: 0,
  44: 0,
  45: 0,
  46: 0,
  47: 0,
  48: 0,
  49: 0,
  50: 0,
  51: 0,
  52: 0,
  53: 0,
  54: 0,
  55: 0,
  56: 0,
  57: 0,
  58: 0,
  59: 0,
  60: 0,
  61: 0,
  62: 0,
  63: 0,
  64: 0,
  65: 0,
  66: 0,
  67: 0,
  68: 0,
  69: 0,
  70: 0,
  71: 0
}

road_index_to_tuple = {
  0: (0, 5),
  1: (0, 1),
  2: (0, 20),
  3: (1, 2),
  4: (1, 6),
  5: (2, 3),
  6: (2, 9),
  7: (3, 4),
  8: (3, 12),
  9: (4, 5),
  10: (4, 15),
  11: (5, 16),
  12: (6, 7),
  13: (6, 23),
  14: (7, 8),
  15: (7, 24),
  16: (8, 9),
  17: (8, 27),
  18: (9, 10),
  19: (10, 11),
  20: (10, 29),
  21: (11, 12),
  22: (11, 32),
  23: (12, 13),
  24: (13, 14),
  25: (13, 34),
  26: (14, 15),
  27: (14, 37),
  28: (15, 17),
  29: (16, 18),
  30: (16, 21),
  31: (17, 18),
  32: (17, 39),
  33: (18, 40),
  34: (19, 21),
  35: (19, 20),
  36: (19, 46),
  37: (20, 22),
  38: (21, 43),
  39: (22, 23),
  40: (22, 49),
  41: (23, 52),
  42: (24, 25),
  43: (24, 53),
  44: (25, 26),
  45: (26, 27),
  46: (27, 28),
  47: (28, 29),
  48: (29, 30),
  49: (30, 31),
  50: (31, 32),
  51: (32, 33),
  52: (33, 34),
  53: (34, 35),
  54: (35, 36),
  55: (36, 37),
  56: (37, 38),
  57: (38, 39),
  58: (39, 41),
  59: (40, 42),
  60: (40, 44),
  61: (41, 42),
  62: (43, 44),
  63: (43, 47),
  64: (45, 47),
  65: (45, 46),
  66: (46, 48),
  67: (48, 49),
  68: (49, 50),
  69: (50, 51),
  70: (51, 52),
  71: (52, 53)
}

# includes bi-directional mapping
road_tuple_to_index = {
  (0, 5): 0,
  (5, 0): 0,
  (0, 1): 1,
  (1, 0): 1,
  (0, 20): 2,
  (20, 0): 2,
  (1, 2): 3,
  (2, 1): 3,
  (1, 6): 4,
  (6, 1): 4,
  (2, 3): 5,
  (3, 2): 5,
  (2, 9): 6,
  (9, 2): 6,
  (3, 4): 7,
  (4, 3): 7,
  (3, 12): 8,
  (12, 3): 8,
  (4, 5): 9,
  (5, 4): 9,
  (4, 15): 10,
  (15, 4): 10,
  (5, 16): 11,
  (16, 5): 11,
  (6, 7): 12,
  (7, 6): 12,
  (6, 23): 13,
  (23, 6): 13,
  (7, 8): 14,
  (8, 7): 14,
  (7, 24): 15,
  (24, 7): 15,
  (8, 9): 16,
  (9, 8): 16,
  (8, 27): 17,
  (27, 8): 17,
  (9, 10): 18,
  (10, 9): 18,
  (10, 11): 19,
  (11, 10): 19,
  (10, 29): 20,
  (29, 10): 20,
  (11, 12): 21,
  (12, 11): 21,
  (11, 32): 22,
  (32, 11): 22,
  (12, 13): 23,
  (13, 12): 23,
  (13, 14): 24,
  (14, 13): 24,
  (13, 34): 25,
  (34, 13): 25,
  (14, 15): 26,
  (15, 14): 26,
  (14, 37): 27,
  (37, 14): 27,
  (15, 17): 28,
  (17, 15): 28,
  (16, 18): 29,
  (18, 16): 29,
  (16, 21): 30,
  (21, 16): 30,
  (17, 18): 31,
  (18, 17): 31,
  (17, 39): 32,
  (39, 17): 32,
  (18, 40): 33,
  (40, 18): 33,
  (19, 21): 34,
  (21, 19): 34,
  (19, 20): 35,
  (20, 19): 35,
  (19, 46): 36,
  (46, 19): 36,
  (20, 22): 37,
  (22, 20): 37,
  (21, 43): 38,
  (43, 21): 38,
  (22, 23): 39,
  (23, 22): 39,
  (22, 49): 40,
  (49, 22): 40,
  (23, 52): 41,
  (52, 23): 41,
  (24, 25): 42,
  (25, 24): 42,
  (24, 53): 43,
  (53, 24): 43,
  (25, 26): 44,
  (26, 25): 44,
  (26, 27): 45,
  (27, 26): 45,
  (27, 28): 46,
  (28, 27): 46,
  (28, 29): 47,
  (29, 28): 47,
  (29, 30): 48,
  (30, 29): 48,
  (30, 31): 49,
  (31, 30): 49,
  (31, 32): 50,
  (32, 31): 50,
  (32, 33): 51,
  (33, 32): 51,
  (33, 34): 52,
  (34, 33): 52,
  (34, 35): 53,
  (35, 34): 53,
  (35, 36): 54,
  (36, 35): 54,
  (36, 37): 55,
  (37, 36): 55,
  (37, 38): 56,
  (38, 37): 56,
  (38, 39): 57,
  (39, 38): 57,
  (39, 41): 58,
  (41, 39): 58,
  (40, 42): 59,
  (42, 40): 59,
  (40, 44): 60,
  (44, 40): 60,
  (41, 42): 61,
  (42, 41): 61,
  (43, 44): 62,
  (44, 43): 62,
  (43, 47): 63,
  (47, 43): 63,
  (45, 47): 64,
  (47, 45): 64,
  (45, 46): 65,
  (46, 45): 65,
  (46, 48): 66,
  (48, 46): 66,
  (48, 49): 67,
  (49, 48): 67,
  (49, 50): 68,
  (50, 49): 68,
  (50, 51): 69,
  (51, 50): 69,
  (51, 52): 70,
  (52, 51): 70,
  (52, 53): 71,
  (53, 52): 71,
}

#initialising all buildings into the dictionary, with a default value of un-owned (0)
all_buildings = { 
  0:  0,
  1:  0,
  2:  0,
  3:  0,
  4:  0,
  5:  0,
  6:  0,
  7:  0,
  8:  0,
  9:  0,
  10: 0,
  11: 0,
  12: 0,
  13: 0,
  14: 0,
  15: 0,
  16: 0,
  17: 0,
  18: 0,
  19: 0,
  20: 0,
  21: 0,
  22: 0,
  23: 0,
  24: 0,
  25: 0,
  26: 0,
  27: 0,
  28: 0,
  29: 0,
  30: 0,
  31: 0,
  32: 0,
  33: 0,
  34: 0,
  35: 0,
  36: 0,
  37: 0,
  38: 0,
  39: 0,
  40: 0,
  41: 0,
  42: 0,
  43: 0,
  44: 0,
  45: 0,
  46: 0,
  47: 0,
  48: 0,
  49: 0,
  50: 0,
  51: 0,
  52: 0,
  53: 0
}