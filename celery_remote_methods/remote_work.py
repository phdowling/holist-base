app = None


def initialize(app_):
    global app
    app = app_


import new

class_table = dict()
bound_delay_registry = dict()

class _RemoteWorkerMeta(type):
    instances = dict()
    num_instances = 0

    def __call__(cls, *args, **kwargs):
        __instance_id__ = kwargs.get("__instance_id__", cls.num_instances)
        kwargs.pop("__instance_id__", None)


        if (__instance_id__, cls) in cls.instances:
            _instance, instantiation_args = cls.instances[(__instance_id__, cls)]
        else:
            __call__init = kwargs.get("__call_init", not cls.__remote_only__)
            kwargs.pop("__call_init", None)

            _instance = cls.__new__(cls, *args, **kwargs)

            if __call__init:
                _instance.__init__(*args, **kwargs)

            for a_name in filter(lambda a: not a.startswith("__"), dir(_instance))[:]:
                attr = getattr(_instance, a_name)
                if getattr(attr, "__is_remote__", False):
                    new_name = a_name + "_delay"
                    setattr(_instance, new_name, new.instancemethod(bound_delay_registry[attr.__task_name__], _instance, cls))

            _instance.__instance_id__ = __instance_id__
            cls.instances[(__instance_id__, cls)] = (_instance, (args, kwargs))
            cls.num_instances += 1

        return _instance


def RemoteWorker(*decorator_args, **decorator_kwargs):
    no_args = False
    if len(decorator_args) == 1 and not decorator_kwargs and callable(decorator_args[0]):
        # We were called without args
        cls_ = decorator_args[0]
        no_args = True

    remote_only = decorator_kwargs.get("remote_only", False)

    def _RemoteWorker(cls):
        __name = str(cls.__name__)
        __bases = tuple(cls.__bases__)
        __dict = dict(cls.__dict__)
        for each_slot in __dict.get("__slots__", tuple()):
            __dict.pop(each_slot, None)

        __dict["__metaclass__"] = _RemoteWorkerMeta
        __dict["__wrapped__"] = cls
        __dict["__remote_only__"] = remote_only

        newcls = _RemoteWorkerMeta(__name, __bases, __dict)
        class_table[cls.__name__] = newcls
        return newcls

    if no_args:
        return _RemoteWorker(cls_)
    else:
        return _RemoteWorker


def remote_task(*decorator_args, **decorator_kwargs):
    no_args = False
    if len(decorator_args) == 1 and not decorator_kwargs and callable(decorator_args[0]):
        # We were called without args
        method_ = decorator_args[0]
        no_args = True

    task_name_ = decorator_kwargs.get("task_name", None)

    def remote_task_decorator(method):
        method_name = method.__name__
        task_name = task_name_ or method_name

        @app.task(name=task_name)
        def method_using_local_class_instance(*args, **kwargs):
            __class_name__ = kwargs["__class_name__"]
            __instance_id__ = kwargs["__instance_id__"]
            r_args, r_kwargs = kwargs["__instantiation_args__"]
            #print "will instantiate with: ", r_args, r_kwargs
            del kwargs["__class_name__"]
            del kwargs["__instance_id__"]
            del kwargs["__instantiation_args__"]

            method_class = class_table[__class_name__]
            _instance = method_class(*r_args, __instance_id__=__instance_id__, __call_init=True,  **r_kwargs)
            actual_local_method = getattr(_instance, method_name)
            return actual_local_method(*args, **kwargs)

        def method_delay(self, *args, **kwargs):
            __instance_id__ = self.__instance_id__
            _, instantiation_args = self.__class__.instances[(__instance_id__, self.__class__)]
            kwargs.update({
                "__class_name__": self.__class__.__name__,
                "__instance_id__": __instance_id__,
                "__instantiation_args__": instantiation_args
            })
            res = app.send_task(task_name, args, kwargs)
            return res

        method.__task_name__ = task_name
        method.__is_remote__ = True

        bound_delay_registry[task_name] = method_delay

        return method

    if no_args:
        return remote_task_decorator(method_)
    else:
        return remote_task_decorator


