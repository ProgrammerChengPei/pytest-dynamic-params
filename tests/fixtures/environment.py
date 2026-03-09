"""环境相关fixtures"""

import pytest


@pytest.fixture(params=["dev", "test", "prod"])
def environment(request):
    """环境配置fixture"""
    return {"env": request.param, "timeout": 30}
