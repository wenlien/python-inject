import unittest
from mock import Mock

from inject import errors
from inject.injections import AttributeInjection, ParamInjection


class AttributeInjectionTestCase(unittest.TestCase):
    
    def setUp(self):
        class DummyAttributeInjection(AttributeInjection):
            injection_class = Mock()
        
        self.injection_class = DummyAttributeInjection
    
    def testInjection(self):
        '''Attribute injection should get an instance from an injection.'''
        class A(object): pass
        class B(object):
            a = self.injection_class('a', A)
        
        a = A()
        injection = B.a.injection
        injection.get_instance.return_value = a
        
        b = B()
        self.assertTrue(b.a is a)
        self.assertTrue(injection.get_instance.called)
    
    def testInheritance(self):
        '''Attribute injection should support inheritance.'''
        class A(object): pass
        class B(object):
            a = self.injection_class('a', A)
        class C(B): pass
        
        a = A()
        injection = B.a.injection
        injection.get_instance.return_value = a
        
        b = B()
        c = C()
        self.assertTrue(b.a is a)
        self.assertTrue(c.a is a)
        self.assertEqual(injection.get_instance.call_count, 2)
    
    def testSettingAttr(self):
        '''Attribute injection should set an attribute of an object.'''
        class A(object): pass
        class B(object):
            a = self.injection_class('a', A)
        
        a = A()
        injection = B.a.injection
        injection.get_instance.return_value = a
        
        b = B()
        self.assertTrue(b.a is a)
        self.assertTrue(b.a is a)
        self.assertEqual(injection.get_instance.call_count, 1)


class ParamTestCase(unittest.TestCase):
    
    def setUp(self):
        class DummyParamInjection(ParamInjection):
            injection_class = Mock()
        
        self.injection_class = DummyParamInjection
    
    def testInjection(self):
        '''ParamInjection should inject dependencies as kwargs.'''
        class A(object): pass
        a = A()
        
        @self.injection_class('a', A)
        def func(a):
            return a
        
        func.injections['a'].get_instance.return_value = a
        
        self.assertTrue(func() is a)
    
    def testMultipleInjection(self):
        '''Multiple ParamInjection injections should be combined into one.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        
        @self.injection_class('a', A)
        @self.injection_class('b', B)
        def func(b, a):
            return b, a
        
        injections = func.injections
        injections['a'] = Mock()
        injections['b'] = Mock()
        injections['a'].get_instance.return_value = a
        injections['b'].get_instance.return_value = b
        
        b2, a2 = func()
        
        self.assertTrue(b2 is b)
        self.assertTrue(a2 is a)
    
    def testInjectNonGivenParams(self):
        '''ParamInjection should injection only non-given dependencies.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        
        @self.injection_class('a', A)
        @self.injection_class('b', B)
        def func(a, b):
            return a, b
        
        injections = func.injections
        injections['a'] = Mock()
        injections['b'] = Mock()
        injections['a'].get_instance.return_value = a
        injections['b'].get_instance.return_value = b
        
        a2, b2 = func(b='b')
        self.assertTrue(a2 is a)
        self.assertEqual(b2, 'b')
    
    def testCreateWrapper(self):
        '''Create wrapper should return a func with set attrs.'''
        def func(): pass
        wrapper = self.injection_class.create_wrapper(func)
        
        self.assertTrue(wrapper.func is func)
        self.assertEqual(wrapper.injections, {})
        self.assertTrue(wrapper.injection_wrapper)
    
    def testAddInjection(self):
        '''Add injection should add an inj to injections dict.'''
        def func(arg): pass
        wrapper = self.injection_class.create_wrapper(func)
        
        # Noraml injection.
        self.injection_class.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionNoParamError(self):
        '''Add injection should raise NoParamError when no such a param.'''
        # NoParamError.
        def func(): pass
        wrapper = self.injection_class.create_wrapper(func)
        self.assertRaises(errors.NoParamError,
                          self.injection_class.add_injection,
                          wrapper, 'arg2', 'inj')
    
    def testAddInjectionArgs(self):
        '''Add injection should not raise NoParamError, when *args given.'''
        def func2(*args): pass
        wrapper = self.injection_class.create_wrapper(func2)
        self.injection_class.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionKwargs(self):
        '''Add injection should not raise NoParamError, when **kwargs.'''
        def func3(**kwargs): pass
        wrapper = self.injection_class.create_wrapper(func3)
        self.injection_class.add_injection(wrapper, 'kwarg', 'inj')
        self.assertEqual(wrapper.injections['kwarg'], 'inj')
