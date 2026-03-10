"""
测试与pytest-xdist的兼容性
对应需求文档中的分布式测试示例
"""
import time
from dynamic_params import param_generator, with_dynamic_params


@param_generator(scope="session", cache=True)
def session_data():
    """生成会话级别的数据，在所有 worker 中共享"""
    return {"timestamp": time.time()}


@param_generator(scope="function")
def function_data(session_data, worker_id):
    """生成函数级别的数据，每个 worker 独立生成"""
    return {
        "session_timestamp": session_data["timestamp"],
        "worker_id": worker_id,
        "function_timestamp": time.time()
    }


class TestXdistCompatibility:
    """测试与pytest-xdist兼容性的测试类"""
    
    @with_dynamic_params(
        session_data=session_data,
        function_data=function_data
    )
    def test_xdist_compatibility(self, session_data, function_data, worker_id):
        """测试与 pytest-xdist 的兼容性"""
        # 验证 session 数据在所有 worker 中相同
        assert "timestamp" in session_data
        
        # 验证 function 数据包含 worker 信息
        assert function_data["worker_id"] == worker_id
        assert "session_timestamp" in function_data
        assert "function_timestamp" in function_data