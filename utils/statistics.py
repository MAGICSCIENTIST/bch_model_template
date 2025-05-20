import sys
import multiprocessing

def detect_effective_parallel(n_jobs=None):
    """估算实际并行线程数（最多返回 4）"""
    cpu_cores = n_jobs
    if n_jobs is None or n_jobs < 0:
        cpu_cores = multiprocessing.cpu_count()
    effective_parallel = min(n_jobs, cpu_cores)
    return effective_parallel


def get_deep_size(obj, seen=None):
    """递归统计对象实际内存大小"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum(get_deep_size(v, seen) for v in obj.values())
        size += sum(get_deep_size(k, seen) for k in obj.keys())
    elif hasattr(obj, '__dict__'):
        size += get_deep_size(obj.__dict__, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(get_deep_size(i, seen) for i in obj)

   
    return size

def estimate_rf_inference_memory(rf,img_shape, n_jobs=1, mode='predict', dtype_size=4):
    """
    更接近真实情况的 scikit-learn 随机森林推理内存估计（MB）

    参数:
    - img_shape: (H, W, C)
    - rf: 已训练 RandomForestClassifier 或 Regressor
    - n_jobs: 并发线程数
    - mode: 'predict' 或 'predict_proba'
    - dtype_size: 输入特征每个值的字节数（float32=4）

    返回:
    - 字典：各部分内存和总内存（MB）
    """
    H, W, C = img_shape
    N = H * W
    n_estimators = len(rf.estimators_)
    n_classes = getattr(rf, "n_classes_", 1)

    # 1. 模型体积（准确遍历 tree_）
    model_bytes = sum(
        arr.nbytes
        for est in rf.estimators_
        for attr in dir(est.tree_)
        if not attr.startswith("_")
        and hasattr(getattr(est.tree_, attr), 'nbytes')
        for arr in [getattr(est.tree_, attr)]
    )
    M_model = model_bytes / 1024 / 1024

    # 2. 输入特征矩阵
    M_input = (N * C * dtype_size) / 1024 / 1024

    # 3. 推理中间结构：每棵树单独预测路径（假设每棵树保留一个 int32 路径数组）
    # 假设每棵树占用 1 × N × 4 B
    # M_trees_temp = (n_estimators * N * 4) / 1024 / 1024
    M_trees_temp = (N * 4 * 2) / 1024 / 1024

    # 4. 多分类结果投票矩阵
    if mode == 'predict_proba':
        M_result_matrix = (N * n_classes * 8) / 1024 / 1024  # float64
    else:
        M_result_matrix = (N * 4) / 1024 / 1024  # int32 class index

    # 5. 并行线程引入的输入副本（假设输入+每树缓存 × 线程）
    # 理论上 joblib 不总复制，但为保守估计，我们乘上 (n_jobs - 1) × 0.5
    effective_jobs = detect_effective_parallel(n_jobs=n_jobs)
    M_parallel_copy = (M_input + M_trees_temp + M_result_matrix) * (effective_jobs - 1) * 0.5

    # 总内存
    M_total = M_model + M_input + M_trees_temp + M_result_matrix + M_parallel_copy

    return M_total, M_model,M_input, M_trees_temp, M_result_matrix, M_parallel_copy
