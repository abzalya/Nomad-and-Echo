# Move Generation
from core.move import Move, MoveFlag
from core.bitboard import iterateBits, RANK_18
from core.attacks import pawnActions, pawnAttacks, pawnMoves, knightMoves, kingMoves, bishopAttacks, rookAttacks, queenAttacks, isSquareAttacked, KING_ATTACKS, attackedBy, PAWN_ATTACKS, KNIGHT_ATTACKS
from core.apply_move import applyMove, undoMove
from core.ray_attacks import RAY_ATTACKS

def generateMoves(gs):
    allMoves = []
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    allPieces = whitePieces | blackPieces

    if gs.whiteToMove:
        ownPieces = whitePieces
        enemyPieces = blackPieces
    else:
        ownPieces = blackPieces
        enemyPieces = whitePieces

    pinned_mask, pin_rays = findPinnedPieces(gs)
    #using rays is pin_rays[sq] - returns a bitmap of the ray so we & the moves with it

    attacked_bb = attackedBy(gs, exclude_defender_king=True)
    #will use this bb to create only legal moves for the king
    in_check = False
    num_checks, check_mask, check_rays = findCheck(gs)
    #if num_checks > 2, only king moves
    #if num_checks = 1, king move, capture or block check
    #if num_checks = 0, standard

    if num_checks >= 2:
        in_check = True
        for sq in iterateBits(gs.whiteKing if gs.whiteToMove else gs.blackKing):
            bb = kingMoves(sq, ownPieces, allPieces, gs, attacked_bb)
            #remove illegal moves stepping into an attack,
            bb_legal = bb & ~attacked_bb
            for to_sq in iterateBits(bb_legal):
                if (1 << to_sq) & enemyPieces:
                    flag = MoveFlag.CAPTURE
                else:
                    flag = MoveFlag.NORMAL
                allMoves.append(Move(sq, to_sq, flag))

    if num_checks == 1:
        in_check = True
        #if the checker is a slider, we extract the ray, and add it to check_mask to have a mask of all possible allowed sqs
        ray_check_sq = check_mask.bit_length() - 1
        if ray_check_sq in check_rays:
            check_mask |= check_rays[ray_check_sq]
        #normal move generation EXCEPT its & with check_mask, plus pin_rays if pinned
        for sq in iterateBits(gs.whitePawns if gs.whiteToMove else gs.blackPawns):
            if (1 << sq) & pinned_mask: #if a pawn is a pinned piece
                bb = pawnActions(sq, gs.whiteToMove, ownPieces, enemyPieces, gs.epSquare)
                pin_bb = bb & pin_rays[sq] & check_mask
                for to_sq in iterateBits(pin_bb):
                    if to_sq == gs.epSquare:
                        flag = MoveFlag.EN_PASSANT
                    elif (1 << to_sq) & enemyPieces:
                        flag = MoveFlag.CAPTURE
                    else:
                        flag = MoveFlag.NORMAL
                    promo_piece = None

                    if ((1 << to_sq) & RANK_18):
                        flag |= MoveFlag.PROMOTION
                        if gs.whiteToMove:
                            promotions = ["whiteQueens", "whiteRooks", "whiteBishops", "whiteKnights"]
                        else:
                            promotions = ["blackQueens", "blackRooks", "blackBishops", "blackKnights"]
                        for promotion in promotions:
                            allMoves.append(Move(sq, to_sq, flag, promotion))
                    else:
                        allMoves.append(Move(sq, to_sq, flag, promo_piece))
            else:
                bb = pawnActions(sq, gs.whiteToMove, ownPieces, enemyPieces, gs.epSquare) & check_mask
                for to_sq in iterateBits(bb):
                    if to_sq == gs.epSquare:
                        flag = MoveFlag.EN_PASSANT
                    elif (1 << to_sq) & enemyPieces:
                        flag = MoveFlag.CAPTURE
                    else:
                        flag = MoveFlag.NORMAL
                    promo_piece = None

                    if ((1 << to_sq) & RANK_18):
                        flag |= MoveFlag.PROMOTION
                        if gs.whiteToMove:
                            promotions = ["whiteQueens", "whiteRooks", "whiteBishops", "whiteKnights"]
                        else:
                            promotions = ["blackQueens", "blackRooks", "blackBishops", "blackKnights"]
                        for promotion in promotions:
                            allMoves.append(Move(sq, to_sq, flag, promotion))
                    else:
                        allMoves.append(Move(sq, to_sq, flag, promo_piece))
        
        for sq in iterateBits(gs.whiteKnights if gs.whiteToMove else gs.blackKnights):
            if (1 << sq) & pinned_mask: #pinned knight can never move along a ray
                continue
            bb = knightMoves(sq, ownPieces) & check_mask
            for to_sq in iterateBits(bb):
                flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteKing if gs.whiteToMove else gs.blackKing):
            bb = kingMoves(sq, ownPieces, allPieces, gs, attacked_bb)
            #remove illegal moves stepping into an attack,
            bb_legal = bb & ~attacked_bb
            for to_sq in iterateBits(bb_legal):
                if (1 << to_sq) & enemyPieces:
                    flag = MoveFlag.CAPTURE
                else:
                    flag = MoveFlag.NORMAL
                allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteBishops if gs.whiteToMove else gs.blackBishops):
            if (1 << sq) & pinned_mask: #if a pinned piece
                bb = bishopAttacks(sq, allPieces, ownPieces)
                pin_bb = bb & pin_rays[sq] & check_mask
                for to_sq in iterateBits(pin_bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))
            else:
                bb = bishopAttacks(sq, allPieces, ownPieces) & check_mask
                for to_sq in iterateBits(bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteRooks if gs.whiteToMove else gs.blackRooks):
            if (1 << sq) & pinned_mask: #if a pinned piece
                bb = rookAttacks(sq, allPieces, ownPieces)
                pin_bb = bb & pin_rays[sq] & check_mask
                for to_sq in iterateBits(pin_bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))
            else:
                bb = rookAttacks(sq, allPieces, ownPieces) & check_mask
                for to_sq in iterateBits(bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteQueens if gs.whiteToMove else gs.blackQueens):
            if (1 << sq) & pinned_mask: #if a pinned piece
                bb = queenAttacks(sq, allPieces, ownPieces)
                pin_bb = bb & pin_rays[sq] & check_mask
                for to_sq in iterateBits(pin_bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))
            else:
                bb = queenAttacks(sq, allPieces, ownPieces) & check_mask
                for to_sq in iterateBits(bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))

            

        
    if num_checks == 0:
        for sq in iterateBits(gs.whitePawns if gs.whiteToMove else gs.blackPawns):
            #add the pinned pieces first
            if (1 << sq) & pinned_mask: #if a pawn is a pinned piece
                bb = pawnActions(sq, gs.whiteToMove, ownPieces, enemyPieces, gs.epSquare)
                pin_bb = bb & pin_rays[sq]
                for to_sq in iterateBits(pin_bb):
                    if to_sq == gs.epSquare:
                        flag = MoveFlag.EN_PASSANT
                    elif (1 << to_sq) & enemyPieces:
                        flag = MoveFlag.CAPTURE
                    else:
                        flag = MoveFlag.NORMAL
                    promo_piece = None

                    if ((1 << to_sq) & RANK_18):
                        flag |= MoveFlag.PROMOTION
                        if gs.whiteToMove:
                            promotions = ["whiteQueens", "whiteRooks", "whiteBishops", "whiteKnights"]
                        else:
                            promotions = ["blackQueens", "blackRooks", "blackBishops", "blackKnights"]
                        for promotion in promotions:
                            allMoves.append(Move(sq, to_sq, flag, promotion))
                    else:
                        allMoves.append(Move(sq, to_sq, flag, promo_piece))


            else:
                bb = pawnActions(sq, gs.whiteToMove, ownPieces, enemyPieces, gs.epSquare)
                for to_sq in iterateBits(bb):
                    if to_sq == gs.epSquare:
                        flag = MoveFlag.EN_PASSANT
                    elif (1 << to_sq) & enemyPieces:
                        flag = MoveFlag.CAPTURE
                    else:
                        flag = MoveFlag.NORMAL
                    promo_piece = None

                    if ((1 << to_sq) & RANK_18):
                        flag |= MoveFlag.PROMOTION
                        if gs.whiteToMove:
                            promotions = ["whiteQueens", "whiteRooks", "whiteBishops", "whiteKnights"]
                        else:
                            promotions = ["blackQueens", "blackRooks", "blackBishops", "blackKnights"]
                        for promotion in promotions:
                            allMoves.append(Move(sq, to_sq, flag, promotion))
                    else:
                        allMoves.append(Move(sq, to_sq, flag, promo_piece))

        for sq in iterateBits(gs.whiteKnights if gs.whiteToMove else gs.blackKnights):
            if (1 << sq) & pinned_mask: #if a knigh is a pinned piece
                continue #pinned knight can never move along a ray
            bb = knightMoves(sq, ownPieces)
            for to_sq in iterateBits(bb):
                flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteKing if gs.whiteToMove else gs.blackKing):
            #king is a bit different
            bb = kingMoves(sq, ownPieces, allPieces, gs, attacked_bb)
            #remove illegal moves stepping into an attack,
            bb_legal = bb & ~attacked_bb
            for to_sq in iterateBits(bb_legal):
                if (1 << to_sq) & enemyPieces:
                    flag = MoveFlag.CAPTURE
                else:
                    flag = MoveFlag.NORMAL
                if (to_sq - sq) == 2:
                    flag |= MoveFlag.CASTLE_K
                if (to_sq - sq) == -2:
                    flag |= MoveFlag.CASTLE_Q
                allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteBishops if gs.whiteToMove else gs.blackBishops):
            if (1 << sq) & pinned_mask: #if a pinned piece
                bb = bishopAttacks(sq, allPieces, ownPieces)
                pin_bb = bb & pin_rays[sq]
                for to_sq in iterateBits(pin_bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))
            else:
                bb = bishopAttacks(sq, allPieces, ownPieces)
                for to_sq in iterateBits(bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteRooks if gs.whiteToMove else gs.blackRooks):
            if (1 << sq) & pinned_mask: #if a pinned piece
                bb = rookAttacks(sq, allPieces, ownPieces)
                pin_bb = bb & pin_rays[sq]
                for to_sq in iterateBits(pin_bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))
            else:
                bb = rookAttacks(sq, allPieces, ownPieces)
                for to_sq in iterateBits(bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))

        for sq in iterateBits(gs.whiteQueens if gs.whiteToMove else gs.blackQueens):
            if (1 << sq) & pinned_mask: #if a pinned piece
                bb = queenAttacks(sq, allPieces, ownPieces)
                pin_bb = bb & pin_rays[sq]
                for to_sq in iterateBits(pin_bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))
            else:
                bb = queenAttacks(sq, allPieces, ownPieces)
                for to_sq in iterateBits(bb):
                    flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
                    allMoves.append(Move(sq, to_sq, flag))

    return allMoves, in_check

def legalMoves(gs):
    allLegalMoves = []
    moves, _ = generateMoves(gs)
    for move in moves:
        applyMove(gs, move)
        gs.whiteToMove = not gs.whiteToMove  # flip back to check own king
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        if not isSquareAttacked(sq, gs):
            allLegalMoves.append(move)
        gs.whiteToMove = not gs.whiteToMove  # restore before undo
        undoMove(gs)
    return allLegalMoves

def captureMovesOnly(gs):
    allLegalMoves = legalMoves(gs)
    allCaptureMoves = []
    for move in allLegalMoves:
        if move.flags & MoveFlag.CAPTURE:
            allCaptureMoves.append(move)
    return allCaptureMoves

#generating captures and promotion moves only specially for quiescence to eliminate all move overhead from that search
def generateQuiescence(gs):
    allMoves = []
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    allPieces = whitePieces | blackPieces

    if gs.whiteToMove:
        ownPieces = whitePieces
        enemyPieces = blackPieces
        own_pawns   = gs.whitePawns
        own_knights = gs.whiteKnights
        own_bishops = gs.whiteBishops
        own_rooks   = gs.whiteRooks
        own_queens  = gs.whiteQueens
        own_king    = gs.whiteKing
        promo_pieces = ("whiteQueens", "whiteRooks", "whiteBishops", "whiteKnights")
    else:
        ownPieces = blackPieces
        enemyPieces = whitePieces
        own_pawns   = gs.blackPawns
        own_knights = gs.blackKnights
        own_bishops = gs.blackBishops
        own_rooks   = gs.blackRooks
        own_queens  = gs.blackQueens
        own_king    = gs.blackKing
        promo_pieces = ("blackQueens", "blackRooks", "blackBishops", "blackKnights")

    ep_sq = gs.epSquare

    #Pawns: captures + EP via pawnAttacks; quiet promotions via pawnMoves filtered to last rank
    for sq in iterateBits(own_pawns):
        cap_bb = pawnAttacks(sq, gs.whiteToMove, enemyPieces, ep_sq)
        for to_sq in iterateBits(cap_bb):
            if to_sq == ep_sq:
                allMoves.append(Move(sq, to_sq, MoveFlag.EN_PASSANT))
            elif (1 << to_sq) & RANK_18:
                flag = MoveFlag.CAPTURE | MoveFlag.PROMOTION
                for promo in promo_pieces:
                    allMoves.append(Move(sq, to_sq, flag, promo))
            else:
                allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))
        #quiet promotion with no capture
        for to_sq in iterateBits(pawnMoves(sq, gs.whiteToMove, allPieces) & RANK_18):
            for promo in promo_pieces:
                allMoves.append(Move(sq, to_sq, MoveFlag.PROMOTION, promo))

    #Other pieces: attack masked to enemy squares only
    for sq in iterateBits(own_knights):
        for to_sq in iterateBits(knightMoves(sq, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    for sq in iterateBits(own_bishops):
        for to_sq in iterateBits(bishopAttacks(sq, allPieces, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    for sq in iterateBits(own_rooks):
        for to_sq in iterateBits(rookAttacks(sq, allPieces, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    for sq in iterateBits(own_queens):
        for to_sq in iterateBits(queenAttacks(sq, allPieces, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    #King captures only
    for sq in iterateBits(own_king):
        for to_sq in iterateBits(KING_ATTACKS[sq] & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    return allMoves

def findPinnedPieces(gs):
    pinned_mask = 0
    pin_rays = {}
    
    ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    allPieces = whitePieces | blackPieces
    if gs.whiteToMove:
        ownPieces, enemyPieces = whitePieces, blackPieces
        enemy_rook_queen = gs.blackRooks | gs.blackQueens
        enemy_bishop_queen = gs.blackBishops | gs.blackQueens
    else:
        ownPieces, enemyPieces = blackPieces, whitePieces
        enemy_rook_queen = gs.whiteRooks | gs.whiteQueens
        enemy_bishop_queen = gs.whiteBishops | gs.whiteQueens

    sq = ownKing.bit_length() - 1
    #msb relevant 3, 4, 5, 6, se, s, sw, w
    #lsb relevant 0, 1, 2, 7, n, ne, e, nw

    for direction in range(8):
        is_lsb = direction in (0, 1, 2, 7)
        ray = RAY_ATTACKS[direction][sq]
        blockers = ray & allPieces
        #if none on ray = not a pin
        if blockers == 0:
            continue
    
        if is_lsb:
            first_blocker = blockers & -blockers
        else:
            first_blocker_sq = blockers.bit_length() - 1
            first_blocker = 1 << first_blocker_sq

        #if first blocker is NOT our piece = not a pin
        if not (first_blocker & ownPieces):
            continue

        rest = blockers ^ first_blocker
        #if only one piece on ray = not a pin
        if rest == 0:
            continue

        if is_lsb:
            second_blocker = rest & -rest
            second_blocker_sq = second_blocker.bit_length() - 1
            #ray upto and including pinner, rest irrelevant
            pin_ray = ray & ((1 << (second_blocker_sq + 1)) - 1)
        else:
            second_blocker_sq = rest.bit_length() - 1
            second_blocker = 1 << second_blocker_sq
            pin_ray = ray & ~((1 << second_blocker_sq) - 1)

        relevant_sliders = enemy_rook_queen if direction % 2 == 0 else enemy_bishop_queen
        #if second blocker is not an relevant enemy slider = not a pin
        if not (second_blocker & relevant_sliders):
            continue
            
        #save the bitboard of all pinned pieces and the rays they are pinned along
        first_blocker_sq = first_blocker.bit_length() - 1
        pinned_mask |= first_blocker
        pin_rays[first_blocker_sq] = pin_ray
    return pinned_mask, pin_rays
    #i need to reuse this for ray attacks of the slider pieces. jsut adopt it for first blocker only i think

def findCheck(gs):
    num_checks = 0
    check_mask = 0
    check_rays = {}
    
    ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    allPieces = whitePieces | blackPieces
    if gs.whiteToMove:
        ownPieces, enemyPieces = whitePieces, blackPieces
        enemy_rook_queen = gs.blackRooks | gs.blackQueens
        enemy_bishop_queen = gs.blackBishops | gs.blackQueens
        enemyPawns = gs.blackPawns
        enemyKnights = gs.blackKnights
    else:
        ownPieces, enemyPieces = blackPieces, whitePieces
        enemy_rook_queen = gs.whiteRooks | gs.whiteQueens
        enemy_bishop_queen = gs.whiteBishops | gs.whiteQueens
        enemyPawns = gs.whitePawns
        enemyKnights = gs.whiteKnights

    sq = ownKing.bit_length() - 1
    
    pawn_check = PAWN_ATTACKS[0 if gs.whiteToMove else 1][sq] & enemyPawns
    if pawn_check: 
        num_checks += 1
        check_mask |= pawn_check
    knight_check = KNIGHT_ATTACKS[sq] & enemyKnights
    if knight_check:
        num_checks += 1
        check_mask |= knight_check
    #ray_checks
    for direction in range(8):
        is_lsb = direction in (0, 1, 2, 7)
        ray = RAY_ATTACKS[direction][sq]
        blockers = ray & allPieces

        if blockers == 0:
            continue
    
        if is_lsb:
            first_blocker = blockers & -blockers
            first_blocker_sq = first_blocker.bit_length() - 1
        else:
            first_blocker_sq = blockers.bit_length() - 1
            first_blocker = 1 << first_blocker_sq

        #if first blocker is our piece = not a check
        if (first_blocker & ownPieces):
            continue

        if is_lsb:
            #ray upto and including checker, rest irrelevant
            check_ray = ray & ((1 << (first_blocker_sq + 1)) - 1)
        else:
            check_ray = ray & ~((1 << first_blocker_sq) - 1)

        relevant_sliders = enemy_rook_queen if direction % 2 == 0 else enemy_bishop_queen
        #if first blocker is not an relevant enemy slider = not a check
        if not (first_blocker & relevant_sliders):
            continue

        #save check piece and the ray
        num_checks += 1    
        check_mask |= first_blocker
        check_rays[first_blocker_sq] = check_ray
    return num_checks, check_mask, check_rays