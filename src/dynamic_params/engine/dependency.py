"""依赖解析模块"""

from typing import Dict, List, Set

from ..errors import CircularDependencyError
from ..public.generators.generator import Generator


def resolve_dependency_order(generators: List[Generator]) -> List[Generator]:
    """解析生成器依赖顺序，使用拓扑排序并检测循环依赖"""
    generator_map = _build_generator_map(generators)
    graph = _build_dependency_graph(generators, generator_map)
    in_degree, reverse_graph = _build_in_degree_and_reverse_graph(graph)
    result = _topological_sort(generator_map, in_degree, reverse_graph)

    # 检查是否存在循环依赖
    if len(result) != len(generators):
        _detect_circular_dependency(graph, in_degree)

    return result


def _build_generator_map(generators: List[Generator]) -> Dict[str, Generator]:
    """构建参数名到生成器的映射"""
    generator_map: Dict[str, Generator] = {}
    for gen in generators:
        generator_map[gen.name] = gen
    return generator_map


def _build_dependency_graph(
    generators: List[Generator], generator_map: Dict[str, Generator]
) -> Dict[str, Set[str]]:
    """构建依赖图，确保依赖的参数名与生成器的name匹配"""
    graph: Dict[str, Set[str]] = {}
    for gen in generators:
        dependencies = set()
        for dep in gen.dependencies:
            # 检查依赖是否是另一个生成器的参数名
            if dep in generator_map:
                dependencies.add(dep)
        graph[gen.name] = dependencies
    return graph


def _build_in_degree_and_reverse_graph(
    graph: Dict[str, Set[str]],
) -> tuple[Dict[str, int], Dict[str, List[str]]]:
    """构建入度和反向依赖图"""
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

    return in_degree, reverse_graph


def _topological_sort(
    generator_map: Dict[str, Generator],
    in_degree: Dict[str, int],
    reverse_graph: Dict[str, List[str]],
) -> List[Generator]:
    """使用Kahn算法进行拓扑排序"""
    from collections import deque

    queue = deque([node for node in in_degree if in_degree[node] == 0])
    result: List[Generator] = []

    while queue:
        node = queue.popleft()
        result.append(generator_map[node])

        # 处理依赖当前节点的所有节点
        for dependent_node in reverse_graph.get(node, []):
            if dependent_node in in_degree:
                in_degree[dependent_node] -= 1
                if in_degree[dependent_node] == 0:
                    queue.append(dependent_node)

    return result


def _detect_circular_dependency(
    graph: Dict[str, Set[str]], in_degree: Dict[str, int]
) -> None:
    """检测循环依赖并抛出异常"""
    # 找出循环依赖的节点
    remaining = [node for node in in_degree if in_degree[node] > 0]
    if remaining:
        # 构建循环路径
        cycle_path: List[str] = []
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
