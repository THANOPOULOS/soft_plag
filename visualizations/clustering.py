import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

try:
    import networkx as nx
    _HAS_NX = True
except ImportError:
    _HAS_NX = False

try:
    from sklearn.manifold import MDS
    from sklearn.cluster import AgglomerativeClustering
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False
#10 diaforetiaka hromata gia ta clusters
_CLUSTER_COLORS = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
    "#ff7f00", "#a65628", "#f781bf", "#999999",
    "#17becf", "#bcbd22",
]

#kaleitai apo to results panel organonei olh tin diadikaisia clustering kai dimiourgei to figure me ta 2 subplots (graph kai mds)
def render_figure(result, threshold: float = 0.50, figsize=(14, 7)) -> plt.Figure:
    n = len(result.files)
    fig = plt.figure(figsize=figsize)

    if n < 2:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Need at least 2 files to show clustering.",
                ha="center", va="center", transform=ax.transAxes, fontsize=13, color="gray")
        ax.set_axis_off()
        fig.tight_layout()
        return fig

    ax_graph = fig.add_subplot(1, 2, 1)
    ax_mds   = fig.add_subplot(1, 2, 2)

    matrix = result.similarity_matrix
    files  = result.files

    cluster_labels = _compute_clusters(matrix, n)
    node_colors = [_CLUSTER_COLORS[c % len(_CLUSTER_COLORS)] for c in cluster_labels]

    _draw_network(ax_graph, matrix, files, node_colors, threshold, result.language)
    _draw_mds(ax_mds, matrix, files, node_colors, cluster_labels, result.language)

    fig.suptitle(f"File Clustering Analysis  [{result.language}]",
                 fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    return fig

#apofasizei se poio cluster anikei kathe arheio
def _compute_clusters(matrix: np.ndarray, n: int) -> list:
    if not _HAS_SKLEARN or n < 2:
        return list(range(n))
    dist = 1.0 - matrix
    np.fill_diagonal(dist, 0.0)
    dist = np.clip(dist, 0.0, None)
    n_clusters = min(max(2, n // 3), n)
    try:
        agg = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric="precomputed",
            linkage="average",
        )
        return agg.fit_predict(dist).tolist()
    except Exception:
        return list(range(n))

#zografizei to graph diktiou ston aristero aksona
def _draw_network(ax, matrix, files, node_colors, threshold, language):
    if not _HAS_NX:
        ax.text(0.5, 0.5, "networkx not installed", ha="center", va="center",
                transform=ax.transAxes, color="gray")
        ax.set_axis_off()
        return

    G = nx.Graph()
    n = len(files)
    short = [_short(f) for f in files]
    for i, s in enumerate(short):
        G.add_node(i, label=s)

    edge_weights = []
    for i in range(n):
        for j in range(i + 1, n):
            w = matrix[i][j]
            if w >= threshold:
                G.add_edge(i, j, weight=float(w))
                edge_weights.append(float(w))

    pos = nx.spring_layout(G, weight="weight", seed=42, k=1.8 / max(n ** 0.5, 1))

    nx.draw_networkx_nodes(
        G, pos, ax=ax, node_color=node_colors,
        node_size=420, alpha=0.92, linewidths=1.0, edgecolors="white",
    )
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        labels={i: short[i] for i in range(n)},
        font_size=7, font_color="white", font_weight="bold",
    )

    if edge_weights:
        edges = list(G.edges(data="weight"))
        widths  = [2.5 * w + 0.3 for *_, w in edges]
        alphas  = [0.3 + 0.7 * w for *_, w in edges]
        for (u, v, w), wd, al in zip(edges, widths, alphas):
            nx.draw_networkx_edges(
                G, pos, edgelist=[(u, v)], ax=ax,
                width=wd, alpha=al, edge_color="#555555",
            )

    ax.set_title(f"Similarity Graph (threshold ≥ {threshold:.0%})", fontsize=11)
    ax.set_axis_off()

#zografizei to scatter plot me MDS ston deksio aksona
def _draw_mds(ax, matrix, files, node_colors, cluster_labels, language):
    n = len(files)
    short = [_short(f) for f in files]

    if not _HAS_SKLEARN or n < 2:
        ax.text(0.5, 0.5, "scikit-learn not installed", ha="center", va="center",
                transform=ax.transAxes, color="gray")
        ax.set_axis_off()
        return

    dist = 1.0 - matrix
    np.fill_diagonal(dist, 0.0)
    dist = np.clip(dist, 0.0, None)
    rng = np.random.default_rng(42)
    dist += rng.uniform(0, 1e-6, dist.shape)
    dist = (dist + dist.T) / 2

    try:
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42, normalized_stress="auto")
        coords = mds.fit_transform(dist)
    except Exception:
        coords = rng.standard_normal((n, 2))

    ax.scatter(
        coords[:, 0], coords[:, 1],
        c=node_colors, s=160, alpha=0.88, zorder=3,
        edgecolors="white", linewidths=1.2,
    )
    for i, label in enumerate(short):
        ax.annotate(
            label, (coords[i, 0], coords[i, 1]),
            textcoords="offset points", xytext=(6, 4),
            fontsize=7, color="#333333",
        )

    unique_clusters = sorted(set(cluster_labels))
    patches = [
        mpatches.Patch(color=_CLUSTER_COLORS[c % len(_CLUSTER_COLORS)], label=f"Cluster {c + 1}")
        for c in unique_clusters
    ]
    ax.legend(handles=patches, fontsize=8, loc="best", framealpha=0.7)
    ax.set_title("MDS Similarity Scatter", fontsize=11)
    ax.set_xlabel("MDS Dimension 1", fontsize=9)
    ax.set_ylabel("MDS Dimension 2", fontsize=9)
    ax.grid(alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

#mikrenei to filename gia na xwraei sto graph kai to scatter plot
def _short(filename: str, max_len: int = 14) -> str:
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    return (stem[:max_len] + "…") if len(stem) > max_len else stem
