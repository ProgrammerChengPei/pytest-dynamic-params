from typing import Any, Dict, List, Optional


class LazyResult:
    """
    懒加载结果类，用于延迟执行生成器函数
    """

    def __init__(self, generator, context: Dict[str, Any], cache_key: str):
        """
        初始化懒加载结果

        Args:
            generator: 生成器对象
            context: 上下文字典
            cache_key: 缓存键
        """
        self.generator = generator
        self.context = context
        self.cache_key = cache_key
        self._result = None
        self._executed = False

    def __str__(self):
        """字符串表示"""
        if self._executed:
            return str(self._result)
        return f"LazyResult(generator={self.generator.func.__name__})"

    def __repr__(self):
        """repr表示"""
        return (
            f"LazyResult(generator={self.generator.func.__name__}, "
            f"executed={self._executed})"
        )

    def __eq__(self, other):
        """相等比较"""
        if not isinstance(other, LazyResult):
            return False
        return (
            self.generator == other.generator
            and self.context == other.context
            and self.cache_key == other.cache_key
        )

    def __hash__(self):
        """哈希值"""
        return hash((self.generator, self.cache_key))

    def execute(self) -> Any:
        """
        执行生成器函数，获取结果

        Returns:
            生成器函数的返回值
        """
        if not self._executed:
            self._result = self.generator._execute_generator(self.context)
            self._executed = True
        return self._result

    @property
    def result(self) -> Any:
        """
        获取结果（懒加载）

        Returns:
            生成器函数的返回值
        """
        return self.execute()


def generate_lazy_combinations(
    static_params: Dict[str, List[Any]],
    dynamic_generators: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    生成静态参数和动态生成器的组合

    Args:
        static_params: 静态参数字典，键为参数名，值为参数值列表
        dynamic_generators: 动态生成器字典，键为参数名，值为生成器函数
        context: 上下文参数

    Returns:
        参数字典列表
    """
    if context is None:
        context = {}

    static_combinations = _generate_static_combinations(static_params)
    return _generate_dynamic_combinations(
        static_combinations, dynamic_generators, context
    )


def _generate_static_combinations(
    static_params: Dict[str, List[Any]],
) -> List[Dict[str, Any]]:
    """
    生成静态参数的所有可能组合

    Args:
        static_params: 静态参数字典，键为参数名，值为参数值列表

    Returns:
        静态参数字典的列表，每个字典代表一种组合
    """
    static_combinations: List[Dict[str, Any]] = [{}]
    for param_name, values in static_params.items():
        new_combinations = []
        for combo in static_combinations:
            for value in values:
                new_combo = combo.copy()
                new_combo[param_name] = value
                new_combinations.append(new_combo)
        static_combinations = new_combinations
    return static_combinations


def _generate_dynamic_combinations(
    static_combinations: List[Dict[str, Any]],
    dynamic_generators: Any,
    context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    为每个静态参数组合生成动态参数

    Args:
        static_combinations: 静态参数字典的列表
        dynamic_generators: 动态生成器字典或列表，字典键为参数名，值为生成器函数；列表元素为生成器对象
        context: 上下文参数

    Returns:
        包含静态和动态参数的字典列表
    """
    result = []
    for static_combo in static_combinations:
        combined_context = {**context, **static_combo}
        dynamic_combo = static_combo.copy()

        # 处理字典类型的动态生成器
        if isinstance(dynamic_generators, dict):
            for param_name, generator in dynamic_generators.items():
                # 执行生成器获取动态参数值
                value = generator.get_result(combined_context)
                dynamic_combo[param_name] = value
        # 处理列表类型的动态生成器
        elif isinstance(dynamic_generators, list):
            for generator in dynamic_generators:
                # 从生成器对象中获取参数名
                param_name = getattr(generator, "name", None) or getattr(
                    generator, "param_name", None
                )
                if param_name:
                    # 执行生成器获取动态参数值
                    value = generator.get_result(combined_context)
                    dynamic_combo[param_name] = value

        result.append(dynamic_combo)

    return result
