"""
示例5: 多个动态参数嵌套
对应 specs/需求.md 第389-421行的使用示例

这个测试展示了动态参数之间的复杂依赖链:
- raw_data 依赖 data_source 和 size
- processed_data 依赖 raw_data 和 algorithm
- is_valid 依赖 processed_data 和 threshold
"""
import pytest

from dynamic_params import with_dynamic_params
from tests.generators import get_raw_data, process_data, validate_results


class TestNestedDynamicParams:
    """测试嵌套动态参数的测试类"""
    
    @with_dynamic_params(
        raw_data=get_raw_data,
        processed_data=process_data,
        is_valid=validate_results
    )
    @pytest.mark.parametrize("data_source", ["api", "database"])
    @pytest.mark.parametrize("size", [5, 10])
    @pytest.mark.parametrize("algorithm", ["algo1", "algo2"])
    @pytest.mark.parametrize("threshold", [0.5, 0.8])
    def test_dynamic_params_nesting(
        self, data_source, size, algorithm, threshold,
        raw_data, processed_data, is_valid
    ):
        """
        动态参数依赖链：data_source/size → raw_data → processed_data → is_valid
        测试用例数量：2个data_source × 2个size × 2个algorithm × 2个threshold = 16个
        """
        # 验证原始数据
        assert len(raw_data) == size
        assert all(item["source"] == data_source for item in raw_data)
        assert all(item["id"] == i + 1 for i, item in enumerate(raw_data))

        # 验证处理后的数据
        assert len(processed_data) == size
        assert all(item["id"] == i + 1 for i, item in enumerate(processed_data))
        if algorithm == "algo1":
            assert all(item["processed"] == item["id"] * 2 for item in processed_data)
        else:
            assert all(item["processed"] == item["id"] * 3 for item in processed_data)

        # 验证结果
        assert isinstance(is_valid, bool)
    
    # 测试边界情况：空数据源和零大小
    @with_dynamic_params(
        raw_data=get_raw_data,
        processed_data=process_data,
        is_valid=validate_results
    )
    @pytest.mark.parametrize("data_source", ["", None])
    @pytest.mark.parametrize("size", [0])
    @pytest.mark.parametrize("algorithm", ["algo1"])
    @pytest.mark.parametrize("threshold", [0.0])
    def test_dynamic_params_edge_cases(
        self, data_source, size, algorithm, threshold,
        raw_data, processed_data, is_valid
    ):
        """
        测试边界情况：空数据源、零大小
        测试用例数量：2个data_source × 1个size × 1个algorithm × 1个threshold = 2个
        """
        # 验证原始数据
        assert len(raw_data) == size
        if size > 0:
            assert all(item["source"] == data_source for item in raw_data)
        
        # 验证处理后的数据
        assert len(processed_data) == size
        
        # 验证结果
        assert isinstance(is_valid, bool)
    
    # 测试更多算法类型
    @with_dynamic_params(
        raw_data=get_raw_data,
        processed_data=process_data,
        is_valid=validate_results
    )
    @pytest.mark.parametrize("data_source", ["api"])
    @pytest.mark.parametrize("size", [2])
    @pytest.mark.parametrize("algorithm", ["algo1", "algo2"])
    @pytest.mark.parametrize("threshold", [0.0, 10.0])
    def test_dynamic_params_more_algorithms(
        self, data_source, size, algorithm, threshold,
        raw_data, processed_data, is_valid
    ):
        """
        测试更多的算法和阈值组合
        测试用例数量：1个data_source × 1个size × 2个algorithm × 2个threshold = 4个
        """
        # 验证原始数据
        assert len(raw_data) == size
        
        # 验证处理后的数据
        assert len(processed_data) == size
        
        # 验证结果
        assert isinstance(is_valid, bool)