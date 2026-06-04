import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#paragei to heatmap
def render_figure(result, figsize=(11, 9)) -> plt.Figure:
    #dymiourgia figure kai elenhos apotelesmaton
    n = len(result.files)
    fig, ax = plt.subplots(figsize=figsize)

    if n == 0:
        ax.text(0.5, 0.5, "No files to display.", ha="center", va="center",
                transform=ax.transAxes, fontsize=14, color="gray")
        ax.set_axis_off()
        fig.tight_layout()
        return fig
    #proetimasia tags
    matrix = result.similarity_matrix
    max_label = 18
    labels = [
        (f[:max_label] + "…") if len(f) > max_label else f
        for f in result.files
    ]
#annotations 
    annot = n <= 20
    fmt = ".2f" if annot else ""
#dymiourgia mask diagoiniou
    mask = np.eye(n, dtype=bool)
#1o heatmap pragmarika dedomena
    sns.heatmap(
        matrix,
        ax=ax,
        annot=annot,
        fmt=fmt,
        mask=mask,
        cmap="YlOrRd",
        vmin=0.0,
        vmax=1.0,
        linewidths=0.4 if n <= 30 else 0.0,
        linecolor="#cccccc",
        xticklabels=labels,
        yticklabels=labels,
        cbar_kws={"label": "Combined Similarity Score", "shrink": 0.8},
        square=True,
    )
#2o heatmap gri diagonios
    sns.heatmap(
        matrix,
        ax=ax,
        mask=~mask,
        annot=False,
        cmap=["#e8e8e8"],
        vmin=0, vmax=1,
        xticklabels=labels,
        yticklabels=labels,
        cbar=False,
        square=True,
        linewidths=0.4 if n <= 30 else 0.0,
        linecolor="#cccccc",
    )
#decoration tou graph
    ax.set_title(
        f"File Similarity Heatmap  [{result.language}]",
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.set_xlabel("Files", fontsize=10)
    ax.set_ylabel("Files", fontsize=10)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)
    fig.tight_layout()
    return fig
