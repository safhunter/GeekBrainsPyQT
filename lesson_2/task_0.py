from pprint import pprint
"""
    Тестирую класс из лекции 2 на возможность использования его как метакласса.
    В выводе получаем исключение:
    Traceback (most recent call last):
      File "...\task_0.py", line 20, in <module>
        class TestMeta(metaclass=MyMeta):
    TypeError: list expected at most 1 argument, got 3
    Параметр metaclass= требует передачи в него callable объекта, принимающего 3 порядковых параметра и возвращающего 
    callable объект.
    Класс MyMeta, наследник класса list, этим условиям не удовлетворяет и метаклассом не является.
    Для того чтобы сделать его метаклассом, нужно унаследовать его от type вместо list, т.е. заменить (list,) во 
    втором параметре вызова type(,,) на (type,)
"""

MyMeta = type('MyMeta', (list, ), dict(x=5, y=6))


class MyMeta2(list):
    x = 5
    y = 6

# MyMeta = type('MyMeta', (type, ), dict(x=5, y=6))
#
#
# class MyMeta2(type):
#     x = 5
#     y = 6


pprint(f'type(MyMeta): {type(MyMeta)}')
pprint(f'MyMeta.__dict__: {MyMeta.__dict__}')
pprint(f'type(MyMeta2): {type(MyMeta2)}')
pprint(f'MyMeta2.__dict__: {MyMeta2.__dict__}')


class TestMeta(metaclass=MyMeta):
    x = 10


class TestMeta2(metaclass=MyMeta2):
    x = 10


test = TestMeta()
test2 = TestMeta2()

pprint(f'type(test): {type(test)}')
pprint(f'test: {test}')
pprint(f'type(test2): {type(test2)}')
pprint(f'test2: {test2}')


# ---------------------------------------------------------------------------------------------------------------------
"""
    Если не учитывать, что метакласс должен как-то взаимодействовать с исходным классом и возвращать класс, 
    то можно в качестве метакласса использовать просто функцию, возвращающую произвольный callable объект.
    В этом примере наш метакласс meta_func превращает любой класс в функцию, возвращающую None
"""


def meta_func(a, b, c):
    def empty_func():
        pass
    return empty_func


class TestMeta3(metaclass=meta_func):
    x = 10


pprint(f'type(TestMeta3): {type(TestMeta3)}')
pprint(f'TestMeta3.__dict__: {TestMeta3.__dict__}')
test3 = TestMeta3()
pprint(f'type(test3): {type(test3)}')


# ---------------------------------------------------------------------------------------------------------------------
"""
    ... ну или в int. 
"""


def meta_func_int(*args):
    return int


class TestMeta4(metaclass=meta_func_int):
    x = 10


pprint(f'type(TestMeta4): {type(TestMeta4)}')
pprint(f'TestMeta4.__dict__: {TestMeta4.__dict__}')
test4 = TestMeta4()
pprint(f'type(test4): {type(test4)}')
pprint(f'test4: {test4}')

"""
    В заключение, type в python это класс с перегруженным конструктором и вот почему я так считаю:
    1. Можно создать экземпляр type (в сущности, любой класс является экземпляром type, в т.ч. class 'function'). 
    Экземпляр функции создать нельзя
    2. Можно унаследоваться от type, наследование от функции невозможно.
    3. В CPython обработка вызова type производится функцией static PyObject *
    type_call(PyTypeObject *type, PyObject *args, PyObject *kwds), в которой проверяется 
    количество переданных аргументов:
    
    ...
     if (type == &PyType_Type) {
        assert(args != NULL && PyTuple_Check(args));
        assert(kwds == NULL || PyDict_Check(kwds));
        Py_ssize_t nargs = PyTuple_GET_SIZE(args);
        Проверка что передан строго один порядковый аргумент    
        if (nargs == 1 && (kwds == NULL || !PyDict_GET_SIZE(kwds))) {
            obj = (PyObject *) Py_TYPE(PyTuple_GET_ITEM(args, 0)); Возвращаем тип(класс) этого агрумента
            Py_INCREF(obj);
            return obj;
        }

        /* SF bug 475327 -- if that didn't trigger, we need 3
           arguments. But PyArg_ParseTuple in type_new may give
           a msg saying type() needs exactly 3. */
        Если нет 3х порядковых аргументов, то кидаем исключение
        if (nargs != 3) {
            PyErr_SetString(PyExc_TypeError,
                            "type() takes 1 or 3 arguments");
            return NULL;
        }
    }

    проверка на наличие конструтора экземпляра
    if (type->tp_new == NULL) {
        _PyErr_Format(tstate, PyExc_TypeError,
                      "cannot create '%s' instances", type->tp_name);
        return NULL;
    }

    Запускаем конструтор c полученными аргументами, проверяем что вернулся не NULL
    obj = type->tp_new(type, args, kwds);
    obj = _Py_CheckFunctionResult(tstate, (PyObject*)type, obj, NULL);
    if (obj == NULL)
        return NULL;
    ...
    
    Что и является перегрузкой по количеству аргументов.
"""
