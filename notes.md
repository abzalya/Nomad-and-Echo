1. Board Representation - what to do:
I have either piece centric or square centric approaches available. Square centric is easy but will be slow. Then, we should do what most people do. Piece centric, bitboards for each piece type. Cant be that hard can it ?
Bit-wise operatiosn are fast. 

2. ray loops:
#the loop version is fine for correctness but slow. The standard optimization is the o^(o-2r) Hyperbola Quintessence trick or precomputed magic bitboards — worth knowing for later once the logic is solid.
