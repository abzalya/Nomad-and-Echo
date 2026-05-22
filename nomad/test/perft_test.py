import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, _HERE)
from nomad.core.board import GameState
from perft import perft

#Compare my implementation against known values from ChessProgramming Wiki
#depth  -   nodes
#1      	20
#2	        400
#3      	8,902
#4      	197,281
#5      	4,865,609
#TOO DEEP
#6      	119,060,324
#7	        3,195,901,860
#8	        84,998,978,956
#9	        2,439,530,234,167
#10	        69,352,859,712,417
#11	        2,097,651,003,696,806
#12	        62,854,969,236,701,747 
#13	        1,981,066,775,000,396,239
#14	        61,885,021,521,585,529,237 
#15	        2,015,099,950,053,364,471,960

gs = GameState()
print("Depth 1 -", "PASS" if perft(gs, 1) == 20      else "FAIL")
print("Depth 2 -", "PASS" if perft(gs, 2) == 400     else "FAIL")
print("Depth 3 -", "PASS" if perft(gs, 3) == 8902    else "FAIL")
print("Depth 4 -", "PASS" if perft(gs, 4) == 197281  else "FAIL")
print("Depth 5 -", "PASS" if perft(gs, 5) == 4865609 else "FAIL")