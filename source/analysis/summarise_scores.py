"""Print the tables that summarise a scoring run.

Part of the analysis package.
"""

from .config import PERIOD_NAMES


def summarise_scores(scores, group_column=None):
    """Print the mean errors of a scoring run, by room and period, by room and weekday, and overall.

    Input:
        scores: the table made by score_rooms.
        group_column: optional. The name of a column of scores (e.g. "group") to give an extra
            overall line for each of its values.

    Output:
        A short text of the overall result (also printed after the tables).
        Nothing is printed if no subset was scored.

    Errors:
        None.
    """
    scored = scores.dropna(subset=["svr_mae"]).copy()
    if scored.empty:
        print("No subset had enough dates to be scored.")
        return "No subset was scored."
    scored["svr_wins"] = scored.svr_mae < scored.median_mae
    print(f"Scored {len(scored)} subsets ({len(scores) - len(scored)} had too few dates). "
          f"Mean MAE (people), SVR vs constant median:")
    by_period = scored.groupby(["room", "period"]).agg(subsets=("svr_mae", "size"), svr_mae=("svr_mae", "mean"),
                                                       median_mae=("median_mae", "mean"), svr_wins=("svr_wins", "sum"))
    print(by_period.reindex(PERIOD_NAMES, level="period").round(3).to_string())
    print("\nBy weekday:")
    print(scored.groupby(["room", "weekday"]).agg(subsets=("svr_mae", "size"), svr_mae=("svr_mae", "mean"),
                                                  median_mae=("median_mae", "mean")).round(3).to_string())
    overall = (f"Overall: SVR {scored.svr_mae.mean():.3f}, median {scored.median_mae.mean():.3f}; "
               f"SVR is better in {int(scored.svr_wins.sum())} of {len(scored)} subsets.")
    if group_column is not None:
        print()
        for name, part in scored.groupby(group_column):
            print(f"{name}: SVR {part.svr_mae.mean():.3f}, median {part.median_mae.mean():.3f}; "
                  f"better in {int(part.svr_wins.sum())} of {len(part)} subsets.")
    print("\n" + overall)
    return overall
