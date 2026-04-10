# Error definitions for pytest-dynamic-params

class DynamicParamsError(Exception):
    """Base exception class for dynamic params plugin"""
    pass

class DependencyError(DynamicParamsError):
    """Error related to dependency resolution"""
    pass

class CircularDependencyError(DependencyError):
    """Error raised when a circular dependency is detected"""
    pass

class GeneratorError(DynamicParamsError):
    """Error related to parameter generators"""
    pass

class GeneratorNotFoundError(GeneratorError):
    """Error raised when a generator is not found"""
    pass

class ParametrizeError(DynamicParamsError):
    """Error related to parameterization"""
    pass



class ConfigError(DynamicParamsError):
    """Error related to configuration"""
    pass

class ConfigurationError(ConfigError):
    """Alias for ConfigError"""
    pass
