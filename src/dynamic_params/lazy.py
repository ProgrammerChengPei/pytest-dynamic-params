"""
集中管理所有懒加载和性能优化相关实现
"""

from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from .core.generator import ParamGenerator


class LazyResult:
    """懒加载结果包装器"""

    def __init__(
        self, generator: "ParamGenerator", context: Dict[str, Any], cache_key: str
    ):
        self.generator = generator
        self.context = context
        self.cache_key = cache_key
        self._result = None
        self._executed = False

    def execute(self) -> Any:
        """执行生成器获取结果"""
        if self._executed:
            return self._result

        # 执行生成器，获取结果
        self._result = self.generator._execute_generator(self.context)
        self._executed = True
        return self._result

    def __eq__(self, other):
        """支持与实际值的比较"""
        return self.execute() == other

    def __str__(self):
        """支持字符串表示"""
        return str(self.execute())

    def __repr__(self):
        """支持repr表示"""
        return repr(self.execute())

    def __getitem__(self, key):
        """支持字典访问"""
        return self.execute()[key]


def generate_lazy_combinations(
    static_params: Dict[str, List[Any]], generators: List["ParamGenerator"]
) -> List[Dict[str, Any]]:
    """生成懒加载参数组合"""
    import itertools

    # 生成立即参数的所有组合
    immediate_combinations = []
    if static_params:
        param_names = list(static_params.keys())
        param_values = list(static_params.values())

        for combo in itertools.product(*param_values):
            combination = dict(zip(param_names, combo))
            immediate_combinations.append(combination)
    else:
        immediate_combinations = [{}]

    # 为每个立即组合创建懒加载生成器
    all_combinations = []
    for combo in immediate_combinations:
        new_combo = combo.copy()

        for generator in generators:
            # 创建懒加载结果
            lazy_result = LazyResult(
                generator=generator,
                context=combo,
                cache_key=generator._make_cache_key(combo),
            )
            new_combo[generator.param_name] = lazy_result

        all_combinations.append(new_combo)

    return all_combinations
