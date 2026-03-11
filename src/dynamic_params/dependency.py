"""依赖解析模块"""

from typing import Dict, List, Set

from .core.generator import ParamGenerator
from .errors import CircularDependencyError


def resolve_dependency_order(generators: List[ParamGenerator]) -> List[ParamGenerator]:
    """解析生成器依赖顺序，使用拓扑排序并检测循环依赖"""
    # 构建依赖图
    graph: Dict[str, Set[str]] = {}
    generator_map: Dict[str, ParamGenerator] = {}

    # 首先创建参数名到生成器的映射
    for gen in generators:
        generator_map[gen.param_name] = gen

    # 构建依赖图，确保依赖的参数名与生成器的param_name匹配
    # 注意：graph[node] 表示 node 依赖的节点列表
    for gen in generators:
        dependencies = set()
        for dep in gen.dependencies:
            # 检查依赖是否是另一个生成器的参数名
            if dep in generator_map:
                dependencies.add(dep)
        graph[gen.param_name] = dependencies

    # 使用Kahn算法进行拓扑排序，更高效且易于理解
    in_degree: Dict[str, int] = {}
    for node in graph:
        in_degree[node] = 0

    # 构建反向依赖图（用于快速查找依赖某个节点的所有节点）
    # reverse_graph[node] 表示依赖 node 的节点列表
    reverse_graph: Dict[str, List[str]] = {}
    for node in graph:
        for dep in graph[node]:
            # 计算入度：node 依赖于 dep，所以 node 的入度增加
            in_degree[node] += 1
            # 构建反向依赖图：dep 被 node 依赖
            if dep not in reverse_graph:
                reverse_graph[dep] = []
            reverse_graph[dep].append(node)

    # 初始化队列，包含所有入度为0的节点
    from collections import deque

    queue = deque([node for node in in_degree if in_degree[node] == 0])
    result: List[ParamGenerator] = []

    while queue:
        node = queue.popleft()
        result.append(generator_map[node])

        # 处理依赖当前节点的所有节点
        for dependent_node in reverse_graph.get(node, []):
            if dependent_node in in_degree:
                in_degree[dependent_node] -= 1
                if in_degree[dependent_node] == 0:
                    queue.append(dependent_node)

    # 检查是否存在循环依赖
    if len(result) != len(generators):
        # 找出循环依赖的节点
        remaining = [node for node in in_degree if in_degree[node] > 0]
        if remaining:
            # 构建循环路径
            cycle_path = []
            visited = set()

            def find_cycle(node):
                if node in visited:
                    return []
                if node in cycle_path:
                    # 找到循环起点
                    idx = cycle_path.index(node)
                    return cycle_path[idx:]

                cycle_path.append(node)
                visited.add(node)

                for dep in graph.get(node, []):
                    if dep in in_degree and in_degree[dep] > 0:
                        cycle = find_cycle(dep)
                        if cycle:
                            return cycle

                cycle_path.pop()
                return []

            for node in remaining:
                cycle = find_cycle(node)
                if cycle:
                    raise CircularDependencyError(cycle)

            # 如果没有找到循环路径，仍然抛出异常
            raise CircularDependencyError(remaining)

    return result
