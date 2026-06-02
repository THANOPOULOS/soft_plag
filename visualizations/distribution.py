import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def render_figure(result, bins: int = 20, figsize=(10, 6)) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)

    scores = [pr.combined for pr in result.pair_results]

    if not scores:
        ax.text(0.5, 0.5, "No pairs to display.\nSelect a folder with at least 2 files.",
                ha="center", va="center", transform=ax.transAxes, fontsize=13, color="gray")
        ax.set_axis_off()
        fig.tight_layout()
        return fig

    edges = np.linspace(0.0, 1.0, bins + 1)
    low_scores    = [s for s in scores if s < 0.40]
    medium_scores = [s for s in scores if 0.40 <= s < 0.70]
    high_scores   = [s for s in scores if s >= 0.70]

    ax.hist(low_scores,    bins=edges, color="#4caf50", alpha=0.85, label="Low (<40%)",    edgecolor="white", linewidth=0.6)
    ax.hist(medium_scores, bins=edges, color="#ff9800", alpha=0.85, label="Medium (40–70%)", edgecolor="white", linewidth=0.6)
    ax.hist(high_scores,   bins=edges, color="#f44336", alpha=0.85, label="High (≥70%)",   edgecolor="white", linewidth=0.6)

    ax.axvline(0.40, color="#e65100", linestyle="--", linewidth=1.6, label="Medium threshold (0.40)")
    ax.axvline(0.70, color="#b71c1c", linestyle="--", linewidth=1.6, label="High threshold (0.70)")

    total = len(scores)
    n_high = len(high_scores)
    n_med  = len(medium_scores)
    n_low  = len(low_scores)
    info = (
        f"Total pairs: {total}  |  "
        f"High: {n_high} ({100*n_high/total:.0f}%)  "
        f"Medium: {n_med} ({100*n_med/total:.0f}%)  "
        f"Low: {n_low} ({100*n_low/total:.0f}%)"
    )
    ax.set_title(f"Similarity Score Distribution  [{result.language}]",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Combined Similarity Score", fontsize=11)
    ax.set_ylabel("Number of File Pairs", fontsize=11)
    ax.set_xlim(0.0, 1.0)
    ax.legend(fontsize=9, loc="upper center")
    ax.text(0.5, -0.13, info, ha="center", va="top", transform=ax.transAxes,
            fontsize=9, color="#555555")
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig
