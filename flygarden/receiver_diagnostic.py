"""Conditional receiver-input partitions; never alters the imported graph."""
import numpy as np
from scipy.sparse import csr_matrix


def receiver_partitions(weights, pn_rows, dna_rows, dm1_sources, aotu_sources):
    """Return intact, PN-afferent-only and paired AOTU-removal matrices.

    Rows are recipients, columns recorded sources. Unchanged recipient rows
    provide controls. Source activity stays fixed in every counterfactual.
    """
    rows = [np.asarray(x, dtype=int) for x in (pn_rows, dna_rows)]
    sources = [np.asarray(x, dtype=int) for x in (dm1_sources, aotu_sources)]
    if (any(x.ndim != 1 or not len(x) or len(np.unique(x)) != len(x) for x in rows+sources)
            or any(np.any(x < 0) or np.any(x >= weights.shape[0]) for x in rows)
            or any(np.any(x < 0) or np.any(x >= weights.shape[1]) for x in sources)
            or np.intersect1d(*rows).size or not np.isfinite(weights.data).all()):
        raise ValueError('Invalid receiver/source mapping')
    w = weights.tocoo(copy=True)
    pn_keep = ~np.isin(w.row, rows[0]) | np.isin(w.col, sources[0])
    dna_keep = ~(np.isin(w.row, rows[1]) & np.isin(w.col, sources[1]))
    def selected(mask):
        result = csr_matrix((w.data[mask], (w.row[mask], w.col[mask])), shape=w.shape)
        result.sum_duplicates();result.sort_indices()
        return result
    return {'intact': selected(np.ones(len(w.data), dtype=bool)),
            'pn_dm1_only': selected(pn_keep),
            'dna_without_aotu019': selected(dna_keep)}
