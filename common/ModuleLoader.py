"""
    Module Loader
    Create by: FlyingBlade
    Create Time: 2018/6/12 19:04
"""


class ModuleLoader(object):
    def __init__(self, module_dir, module_names):
        self.__modules = []
        for module_name in module_names:
            module = __import__(module_dir + '.' + module_name, fromlist=(module_name,)).Module()
            module.name = module_name
            self.__modules.append(module)

    def get_modules(self) -> list:
        return self.__modules
