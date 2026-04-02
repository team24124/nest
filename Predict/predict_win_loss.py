def get_expected_win_rate(score_diff: float, c: float = 400.0) -> float:
    """
    Calculates the expected win rate based on the score difference between two alliances.
    
    Formula: P(win) = 1 / (1 + 10^((Score_Opponent - Score_Self) / C))
    
    :param score_diff: The score difference (Opponent Total - Self Total).
                       Negative if self is leading.
    :param c: Scaling constant. Larger values result in smoother win rate fluctuations;
              smaller values result in more extreme win rate changes for small score differences.
              (Default: 120.0, can be optimized )
    """
    return 1 / (1 + 10 ** (score_diff / c))

def predict_match_outcome(
    red_auto: float, red_tele: float, red_end: float,
    blue_auto: float, blue_tele: float, blue_end: float,
    c: float = 120.0
):
    """
    Predicts the outcome using weighted components (Phase 3 Optimized).
    Weights: Auto=1.2, Tele=1.0, Endgame=0.8
    """
    red_eff = 1.2 * red_auto + 1.0 * red_tele + 0.8 * red_end
    blue_eff = 1.2 * blue_auto + 1.0 * blue_tele + 0.8 * blue_end
    
    # Calculate difference (Opponent - Self) relative to Red as self
    score_diff = blue_eff - red_eff
    return get_expected_win_rate(score_diff, c)

def predict_match_outcome_total(red_total: float, blue_total: float, c: float = 50.0):
    """Fallback for total-score-only prediction (Phase 2 Optimal C=50)"""
    return get_expected_win_rate(blue_total - red_total, c)
