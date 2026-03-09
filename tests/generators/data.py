"""数据处理相关参数生成器"""

from dynamic_params import param_generator


@param_generator
def get_raw_data(data_source, size):
    """获取原始数据"""
    return [{"id": i + 1, "source": data_source} for i in range(size)]


@param_generator
def process_data(raw_data, algorithm):
    """处理数据 - 简化版的算法应用"""
    if algorithm == "algo1":
        return [{"id": item["id"], "processed": item["id"] * 2} for item in raw_data]
    else:  # algo2
        return [{"id": item["id"], "processed": item["id"] * 3} for item in raw_data]


@param_generator
def validate_results(processed_data, threshold):
    """验证结果 - 检查所有处理值是否大于等于阈值"""
    return all(item["processed"] >= threshold for item in processed_data)
