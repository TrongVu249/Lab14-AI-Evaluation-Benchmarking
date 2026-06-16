from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Kiểm tra xem ít nhất một tài liệu chính xác (trong expected_ids) 
        có xuất hiện trong top_k tài liệu được truy xuất thực tế hay không.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
            
        top_retrieved = retrieved_ids[:top_k]
        top_retrieved_strs = [str(x).strip() for x in top_retrieved]
        expected_strs = [str(x).strip() for x in expected_ids]
        
        hit = any(doc_id in top_retrieved_strs for doc_id in expected_strs)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Tính toán Mean Reciprocal Rank (MRR).
        Tìm vị trí đầu tiên của một expected_id trong retrieved_ids (1-indexed).
        MRR = 1 / position. Nếu không tìm thấy thì trả về 0.0.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
            
        retrieved_strs = [str(x).strip() for x in retrieved_ids]
        expected_strs = [str(x).strip() for x in expected_ids]
        
        for i, doc_id in enumerate(retrieved_strs):
            if doc_id in expected_strs:
                return 1.0 / (i + 1)
        return 0.0

    async def evaluate_batch(self, dataset: List[Dict], retrieved_results: List[List[str]]) -> Dict:
        """
        Đánh giá hàng loạt tập dữ liệu.
        dataset: Danh sách các test cases (chứa expected_retrieval_ids).
        retrieved_results: Danh sách các ID tài liệu mà Agent thực tế đã truy xuất tương ứng với từng test case.
        """
        total_cases = len(dataset)
        if total_cases == 0:
            return {"avg_hit_rate": 0.0, "avg_mrr": 0.0}

        total_hit_rate = 0.0
        total_mrr = 0.0

        for case, retrieved_ids in zip(dataset, retrieved_results):
            expected_ids = case.get("expected_retrieval_ids", [])
            total_hit_rate += self.calculate_hit_rate(expected_ids, retrieved_ids)
            total_mrr += self.calculate_mrr(expected_ids, retrieved_ids)

        return {
            "avg_hit_rate": total_hit_rate / total_cases,
            "avg_mrr": total_mrr / total_cases
        }

