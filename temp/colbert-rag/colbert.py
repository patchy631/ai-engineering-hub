import torch

def compute_relevance_scores(query_embeddings, document_embeddings, k):
    """
    Compute relevance scores for top-k documents given a query.
    
    :param query_embeddings: Tensor representing the query embeddings, shape: [num_query_terms, embedding_dim]
    :param document_embeddings: Tensor representing embeddings for k documents, shape: [k, max_doc_length, embedding_dim]
    :param k: Number of top documents to re-rank
    :return: Sorted document indices based on their relevance scores
    """
    
    # Ensure document_embeddings is a 3D tensor: [k, max_doc_length, embedding_dim]
    # Pad the k documents to their maximum length for batch operations
    # Note: Assuming document_embeddings is already padded and moved to GPU
    
    # Compute batch dot-product of Eq (query embeddings) and D (document embeddings)
    # Resulting shape: [k, num_query_terms, max_doc_length]
    scores = torch.matmul(query_embeddings.unsqueeze(0), document_embeddings.transpose(1, 2))
    
    print("scores_shape", scores.shape)
    # Apply max-pooling across document terms (dim=2) to find the max similarity per query term
    # Shape after max-pool: [k, num_query_terms]
    max_scores_per_query_term = scores.max(dim=2).values
    print("max_scores_per_query_term_shape", max_scores_per_query_term.shape)
    # Sum the scores across query terms to get the total score for each document
    # Shape after sum: [k]
    total_scores = max_scores_per_query_term.sum(dim=1)
    print("total_scores", total_scores)
    # Sort the documents based on their total scores
    sorted_indices = total_scores.argsort(descending=True)
    
    return sorted_indices

def test_compute_relevance_scores():
    # Set dimensions
    num_query_terms = 3  # number of tokens in query
    embedding_dim = 5    # dimension of each embedding
    k = 7               # number of documents to rerank
    max_doc_length = 4  # example document length
    
    # Create sample query embeddings: shape [3, 5]
    query_embeddings = torch.tensor([
        [0.1, 0.2, 0.3, 0.4, 0.5],  # embedding for first query token
        [0.2, 0.3, 0.4, 0.5, 0.6],  # embedding for second query token
        [0.3, 0.4, 0.5, 0.6, 0.7]   # embedding for third query token
    ])
    
    # Create sample document embeddings: shape [7, 4, 5]
    document_embeddings = torch.randn(k, max_doc_length, embedding_dim)
    
    # Compute relevance scores
    sorted_indices = compute_relevance_scores(query_embeddings, document_embeddings, k)
    
    # Test assertions
    assert sorted_indices.shape == torch.Size([k]), "Output shape should be [k]"
    assert len(torch.unique(sorted_indices)) == k, "All indices should be unique"
    assert all(0 <= idx < k for idx in sorted_indices), "Indices should be in range [0, k)"
    
    print("Test passed successfully!")
    print("Sorted indices:", sorted_indices.tolist())

# Run the test
test_compute_relevance_scores()

# scores_shape torch.Size([7, 3, 4])
# max_scores_per_query_term_shape torch.Size([7, 3])
# total_scores tensor([-0.1476,  0.7772,  2.1757,  3.3793,  4.8741,  4.0813,  1.8585])
# Test passed successfully!
# Sorted indices: [4, 5, 3, 2, 6, 1, 0]