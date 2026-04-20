1. We need to code the actual chess game
2. The "Engine" is essentially an evaluate the position and make the best decision. That feeds into minimax with alpha beta pruning to make computer.
3. Evaluation metrics of the project. - Engine decision time and approx. elo. How to improve? 
3.1 Saw this already but for later, to maximise the chance of pruning we order the moves in the most logical order as well. But how?


NO AI
python -m venv venv && pip install -r requirements.txt