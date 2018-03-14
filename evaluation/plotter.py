import matplotlib.pyplot as plt
import pandas
import numpy
from collections import Counter
import os


# This can be calculated from the data
all_concepts = {2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                21, 23, 24, 25, 27, 28, 31, 32, 33, 34, 35, 36, 37, 38, 40, 42,
                43, 44, 45, 46, 48, 49, 52, 53, 55, 56, 57, 59, 60, 64, 65, 66,
                67, 68, 70, 72, 73, 76, 77, 78, 80, 81, 82, 83, 84, 85, 86, 88,
                89, 90, 92, 93, 95, 96, 97, 98, 100, 101, 102, 105, 107, 108,
                109, 110, 111, 112, 113, 116, 117, 119, 121, 122, 123, 124,
                126, 127, 128, 129, 132, 133, 134, 135, 136, 137, 138, 139,
                140, 141, 142, 144, 146, 148, 151, 153, 154, 155, 156, 157,
                158, 159, 160, 161, 162, 163, 164, 166, 167, 168, 169, 170,
                171, 172, 173, 174, 175, 176, 178, 179, 180, 181, 183, 184,
                185, 186, 189, 190, 191, 192, 193, 194, 195, 196, 197, 199,
                200, 201, 202, 203, 204, 205, 206, 208, 210, 211, 212, 213,
                214, 215, 216, 218, 219, 221, 223, 224, 225, 227, 228, 230,
                231, 232, 233, 234, 236, 237, 238, 239, 240, 241, 242, 243,
                244, 245, 247, 248, 249, 250, 251, 254, 255, 256, 257, 258,
                259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270,
                271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 283,
                284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295,
                296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307,
                308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319,
                320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331,
                332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343,
                344, 345, 346, 347, 348, 349, 351, 352, 354, 355, 356, 357,
                358, 359, 360, 361, 362, 363, 365, 366, 367, 369, 371, 372,
                374, 375, 376, 377, 378, 379, 380, 381, 383, 384, 386, 387,
                388, 389, 390, 391, 392, 393, 394, 395, 397, 398, 399, 400,
                402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413,
                414, 415, 416, 417, 418, 419, 420, 421, 424, 425, 426, 427,
                429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440,
                441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452,
                453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 465, 474,
                475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486,
                488, 489, 490, 492, 493, 496, 497, 498, 499, 501, 502, 503,
                504, 505, 506, 507, 509, 513, 514, 516, 518, 522, 525, 526,
                531, 539, 544, 552, 554, 568, 569, 570, 571, 573, 576, 578,
                579, 580, 581, 582, 584, 585, 586, 587, 588, 589, 590, 591,
                592, 593, 594, 595, 596, 597, 598, 599, 601, 602, 603, 604,
                605, 606, 607, 609, 610, 611, 612, 613, 614, 615, 616, 617,
                618, 619, 620, 621, 622, 623, 624, 626, 627, 628, 629, 630,
                631, 632, 633, 634, 635, 636, 638, 639, 640, 641, 642, 643,
                644, 645, 646, 647, 648, 649, 650, 652, 653, 654, 655, 656,
                657, 658, 660, 661, 662, 663, 665, 666, 667, 668, 670, 671,
                672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683,
                684, 686, 687, 688, 689, 690, 691, 692, 694, 695, 696, 698,
                699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710,
                711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722,
                723, 724, 725, 727, 728, 729, 730, 731, 732, 733, 734, 735,
                736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747,
                748, 749, 750, 752, 753, 754, 755, 757, 758, 759, 760, 761,
                762, 763, 765, 767, 768, 769, 770, 771, 772, 773, 777, 778,
                779, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791,
                792, 793, 794, 796, 797, 798, 799, 800, 801, 802, 803, 804,
                805, 806, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817,
                818, 819, 820, 822, 827, 828, 829, 832, 833, 834, 836, 837,
                838, 840, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852,
                853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864,
                865, 866, 867, 868, 870, 871, 873, 874, 875, 876, 877, 878,
                879, 881, 882, 883, 884, 886, 887, 889, 890, 891, 892, 894,
                895, 896, 897, 899, 900, 901, 902, 904, 906, 907, 908, 910,
                911, 912, 913, 914, 915, 916, 917, 919, 920, 921, 922, 923,
                924, 925, 926, 928, 930, 931, 932, 933, 934, 935, 936, 937,
                938, 941, 942, 943, 945, 946, 947, 948, 950, 951, 952, 953,
                954, 956, 957, 958, 960, 961, 962, 963, 964, 965, 966, 968,
                969, 970, 971, 972, 974, 976, 977, 978, 979, 980, 981, 983,
                984, 987, 988, 989, 991, 994, 996, 997, 998, 1000, 1001, 1002,
                1003, 1005, 1006, 1007, 1008, 1010, 1011, 1012, 1013, 1014,
                1018, 1019, 1021, 1022, 1024, 1025, 1026, 1027, 1028, 1029,
                1032, 1033, 1034, 1035, 1038, 1039, 1040, 1041, 1042, 1044,
                1045, 1046, 1047, 1048, 1049, 1051, 1052, 1058, 1059, 1060,
                1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070,
                1071, 1072, 1074, 1075, 1076, 1077, 1079, 1081, 1082, 1084,
                1085, 1086, 1087, 1088, 1090, 1091, 1092, 1093, 1095, 1096,
                1098, 1100, 1102, 1103, 1104, 1105, 1106, 1107, 1109, 1110,
                1111, 1112, 1113, 1115, 1116, 1117, 1119, 1121, 1122, 1123,
                1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133,
                1134, 1135, 1136, 1137, 1139, 1140, 1141, 1142, 1143, 1144,
                1145, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156,
                1157, 1158, 1159, 1160, 1161, 1162, 1165, 1167, 1169, 1170,
                1171, 1172, 1173, 1174, 1175, 1176, 1178, 1179, 1180, 1181,
                1182, 1183, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192,
                1193, 1194, 1195, 1197, 1198, 1199, 1200, 1201, 1202, 1203,
                1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213,
                1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223,
                1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233,
                1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243,
                1244, 1245, 1246, 1247, 1248, 1250, 1251, 1252, 1253, 1254,
                1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265,
                1267, 1268, 1269, 1270, 1272, 1273, 1274, 1275, 1276, 1277,
                1278, 1279, 1280, 1281, 1282, 1283, 1284, 1286, 1287, 1288,
                1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298,
                1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308,
                1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1318, 1320,
                1321, 1322, 1323, 1324, 1325, 1326, 1327, 1329, 1330, 1331,
                1332, 1333, 1335, 1336, 1337, 1338, 1339, 1340, 1342, 1343,
                1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353,
                1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363,
                1364, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374,
                1375, 1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384,
                1385, 1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394,
                1395, 1396, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405,
                1406, 1407, 1408, 1409, 1410, 1411, 1413, 1414, 1415, 1416,
                1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426,
                1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436,
                1437, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447,
                1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457,
                1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1467, 1468,
                1469, 1470, 1471, 1472, 1474, 1475, 1476, 1477, 1478, 1479,
                1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489,
                1490, 1491, 1493, 1494, 1495, 1496, 1497, 1498, 1500, 1501,
                1502, 1503, 1504, 1506, 1507, 1508, 1509, 1510, 1511, 1513,
                1514, 1515, 1517, 1518, 1519, 1521, 1523, 1524, 1525, 1526,
                1527, 1528, 1529, 1530, 1531, 1533, 1534, 1535, 1536, 1537,
                1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547,
                1548, 1550, 1551, 1553, 1554, 1555, 1556, 1557, 1558, 1559,
                1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569,
                1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580,
                1581, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591,
                1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601,
                1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611,
                1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621,
                1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631,
                1632, 1633, 1634, 1635, 1638, 1639, 1640, 1641, 1642, 1643,
                1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1653, 1654,
                1655, 1656, 1657, 1659, 1660, 1662, 1663, 1664, 1665, 1666,
                1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676,
                1677, 1678, 1679, 1680, 1681, 1682, 1683, 1685, 1686, 1687,
                1689, 1690, 1692, 1693, 1694, 1695, 1696, 1697, 1699, 1700,
                1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711,
                1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721,
                1722, 1723, 1724, 1725, 1726, 1728, 1729, 1730, 1731, 1732,
                1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1743,
                1744, 1745, 1747, 1749, 1750, 1752, 1753, 1754, 1755, 1756,
                1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766,
                1767, 1768, 1769, 1770, 1772, 1773, 1774, 1775, 1776, 1778,
                1779, 1781, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789,
                1790, 1791, 1792, 1793, 1794, 1799, 1801, 1802, 1803, 1804,
                1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814,
                1815, 1816, 1817, 1818, 1819, 1820, 1821, 1823, 1824, 1825,
                1826, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1836, 1837,
                1838, 1839, 1840, 1841, 1843, 1844, 1845, 1846, 1847, 1848,
                1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858,
                1859, 1860, 1862, 1864, 1865, 1866, 1867, 1868, 1869, 1870,
                1871, 1872, 1873, 1874, 1875, 1876, 1877, 1879, 1881, 1882,
                1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892,
                1893, 1895, 1896, 1897, 1898, 1899, 1901, 1902, 1903, 1904,
                1905, 1906, 1909, 1910, 1911, 1913, 1914, 1915, 1916, 1917,
                1920, 1921, 1922, 1923, 1924, 1926, 1927, 1928, 1929, 1931,
                1932, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942,
                1943, 1944, 1945, 1946, 1948, 1949, 1950, 1951, 1954, 1957,
                1958, 1959, 1961, 1962, 1963, 1964, 1966, 1967, 1970, 1971,
                1972, 1973, 1974, 1976, 1977, 1978, 1979, 1981, 1982, 1983,
                1984, 1985, 1986, 1987, 1989, 1990, 1991, 1992, 1994, 1996,
                1997, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
                2012, 2013, 2014, 2017, 2018, 2019, 2020, 2021, 2022, 2023,
                2024, 2025, 2027, 2030, 2031, 2034, 2035, 2036, 2037, 2038,
                2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048,
                2049, 2051, 2052, 2053, 2055, 2056, 2057, 2058, 2059, 2060,
                2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070,
                2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2080, 2081,
                2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2092,
                2093, 2094, 2102, 2112, 2113, 2117, 2118, 2124, 2125, 2130,
                2131, 2132, 2133, 2134, 2135, 2136, 2137, 2138, 2139, 2144,
                2146, 2148, 2149, 2150, 2151, 2152, 2153, 2154, 2155, 2156,
                2157, 2159, 2160, 2161, 2162, 2163, 2164, 2190, 2223, 2224,
                2235, 2239, 2241, 2243, 2249, 2250, 2252, 2253, 2254, 2255,
                2256, 2257, 2259, 2260, 2261, 2262, 2263, 2264, 2265, 2266,
                2267, 2271, 2273, 2306, 2308, 2319, 2327, 2334, 2336, 2350,
                2366, 2373, 2374, 2377, 2378, 2396, 2401, 2406, 2410, 2458,
                2466, 2467, 2468, 2470, 2482, 2483, 2486, 2492, 2493, 2504,
                2524, 2526, 2537, 2539, 2546, 2555, 2558, 2559, 2575, 2576,
                2604, 2615, 2638, 2648, 2708, 2837, 2845, 2846, 2847, 2848,
                2849, 2850, 2851, 2852, 2853, 2854, 2855, 2857, 2858, 2859,
                2860, 2861, 2862, 2863, 2864, 2865, 2866, 2867, 2868, 2869,
                2870, 2871, 2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879,
                2880, 2881, 2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889,
                2890, 2891, 2892, 2893, 2894, 2895, 2896, 2897, 2898, 2899,
                2900, 2901, 2902, 2903, 2904, 2905, 2906, 2907, 2908, 2909,
                2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2918, 2919,
                2920, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929,
                2930, 2931, 2932, 2933, 2934, 2935, 2936, 2937, 2938, 2939,
                2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949,
                2950, 2951, 2952, 2953, 2954, 2955, 2956, 2957, 2958, 2959,
                2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969,
                2970, 2971, 2972, 2973, 2974, 2975, 2976, 2977, 2978, 2979,
                2980, 2981, 2982, 2983, 2984, 2985, 2986, 2987, 2988, 2989,
                2990, 2991, 2992, 2993, 2994, 2995, 2996, 2997, 2998, 2999,
                3000, 3001, 3002, 3003, 3004, 3005, 3006}


def generate_random_concept_list(concepts, length=400):
    concepts = list(concepts)
    numpy.random.shuffle(concepts)
    return set(concepts[:length])


concept_list = generate_random_concept_list(all_concepts)
print("Concept list length:", len(concept_list))


def sample_data(data, relative=2 / 3, concepts=all_concepts, at_most=10000):
    for concept, words in data.groupby("Feature_ID"):
        if concept not in concepts:
            continue
        max_wt = max(words["Weight"])
        for i, word in words.sort_values(by="Weight").reset_index(
                drop=True).iterrows():
            if i > at_most:
                break
            if word["Weight"] <= max_wt * relative:
                break
            yield concept, word["Cognate_Set"]


def image_name(key):
    return "_".join([i.lower() for i in key.split()])


default_properties = {
    "i": "d199",
    "n": 0.004,
    "w": 2,
    "c": "degreesquared"}


def properties(file):
    if not (file.startswith("trivial_long_") and file.endswith(".csv")):
        return None
    props = default_properties.copy()
    props.update({s[0]: s[1:] for s in file[13:-4].split("_")})
    props["n"] = float(props["n"])
    props["w"] = float(props["w"])
    return props


def property_key(property):
    def key(file):
        value = default_properties[property]
        props = properties(file)
        if props is None:
            return None
        for k, v in props.items():
            if k == property:
                value = v
            elif k in default_properties and v != default_properties[k]:
                return None
        return value
    return key


def semantic_width(data, column="Cognate_Set"):
    """Calculate average synonym count.

    Calculate the average weighted semantic width in the language
    represented by data.

    """
    width = 0
    m = 0
    for form, meanings in data.groupby(column):
        width += (meanings["Weight"].sum() ** 2 /
                  (meanings["Weight"] ** 2).sum())
        m += 1
    return width / m


def synonymity(data):
    """Calculate average synonym count.

    Calculate the average weighted synonym count in the language
    represented by data.

    """
    return semantic_width(data, column="Feature_ID")


def load(key, path="../", sample_data=sample_data):
    """Load all files according to given key from directory path."""
    n = {}
    p = {}
    s = {}
    for file in os.listdir(path):
        weight = key(file)
        if weight is not None:
            all_data = pandas.read_csv(
                os.path.join(path, file),
                sep=",",
                na_values=[""],
                keep_default_na=False,
                encoding='utf-8')

            for language_id, language_data in all_data.groupby("Language_ID"):
                if int(language_id) > 8e6:
                    words = set()
                    polysemy = Counter()
                    synonymy = Counter()
                    for concept, word in sample_data(language_data):
                        words.add(word)
                        polysemy[word] += 1
                        synonymy[concept] += 1
                    n.setdefault(weight, []).append(
                        len(words))
                    p.setdefault(weight, []).append(
                        numpy.mean(list(polysemy.values())))
                    s.setdefault(weight, []).append(
                        numpy.mean(list(synonymy.values())))

    return n, p, s


def plot_something(n, labels, xlabel, ylabel, showfliers=True):
    plt.boxplot([n[i] for i in labels], labels=labels, showfliers=showfliers)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.gcf().set_size_inches(5, 4)
    plt.xticks(rotation=45)
    plt.savefig("{:s}_{:s}.pdf".format(
        image_name(xlabel), image_name(ylabel)))
