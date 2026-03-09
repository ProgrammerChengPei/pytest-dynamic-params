"""依赖解析模块"""

from typing import Dict, List, Set

from .core.generator import ParamGenerator


def resolve_dependency_order(generators: List[ParamGenerator]) -> List[ParamGenerator]:
    """解析生成器依赖顺序，使用拓扑排序并检测循环依赖"""
    # 构建依赖图
    graph: Dict[str, Set[str]] = {}
    generator_map: Dict[str, ParamGenerator] = {}
    
    for gen in generators:
        generator_map[gen.param_name] = gen
        graph[gen.param_name] = set(gen.dependencies)
    
    # 拓扑排序并检测循环依赖
    visited: Set[str] = set()
    temp_visited: Set[str] = set()
    result: List[ParamGenerator] = []
    
    def dfs(node: str):
        if node in temp_visited:
            # 发现循环依赖
            cycle_path = CircularDependencyError.find_cycle_path(graph, node, temp_visited)
            raise CircularDependencyError(cycle_path, node)
        
        if node in visited:
            return
            
        temp_visited.add(node)
        
        # 访问所有依赖节点
        for dep in graph.get(node, set()):
            if dep in generator_map:  # 只处理动态参数之间的依赖
                dfs(dep)
        
        temp_visited.remove(node)
        visited.add(node)
        result.append(generator_map[node])
    
    for gen in generators:
        if gen.param_name not in visited:
            dfs(gen.param_name)
    
    return result


class CircularDependencyError(Exception):
    """循环依赖错误"""
    
    def __init__(self, cycle_path: List[str], node: str):
        self.cycle_path = cycle_path
        self.node = node
        message = f"检测到循环依赖: {' -> '.join(cycle_path)} -> {node}"
        super().__init__(message)
    
    @staticmethod
    def find_cycle_path(graph: Dict[str, Set[str]], start_node: str, temp_visited: Set[str]) -> List[str]:
        """静态方法：查找循环依赖路径"""
        # 从起始节点开始，追踪路径直到回到起始节点
        path = []
        current = start_node
        
        # 为了找到循环路径，我们遍历临时访问集合中的节点
        visited_in_path = set()
        queue = [(start_node, [])]
        
        while queue:
            node, current_path = queue.pop(0)
            
            if node == start_node and len(current_path) > 0:
                return current_path
                
            if node in visited_in_path or node not in temp_visited:
                continue
                
            visited_in_path.add(node)
            
            for dep in graph.get(node, set()):
                if dep in temp_visited:
                    queue.append((dep, current_path + [node]))
        
        return []