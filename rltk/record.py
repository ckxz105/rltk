import re


re_record_id = re.compile(r'^[^*]{1,255}$')


class Record(object):
    """
    Record representation. Properties should be defined for further usage.
    
    Args:
        raw_object (object): Raw data which will be used to create properties.
    """

    remove_raw_object = False

    def __init__(self, raw_object):
        self.raw_object = raw_object

    @property
    def id(self):
        """
        Required property. Type has to be utf-8 string.
        """
        raise NotImplementedError

    def __eq__(self, other):
        """
        Only if both instances have the same class and id.
        
        Returns:
            bool: Equal or not.
        """
        if not isinstance(other, self.__class__):  # class should be exactly the same
            return False
        return self.id == other.id


class cached_property(property):
    """
    Decorator.
    If a Record property is decorated, the final value of it will be pre-calculated.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        """
        Args:
            obj (object): Record instance
            cls (class): Record class
        Returns:
            object: cached value
        """
        if obj is None:
            return self

        # create property if it's not there
        cached_name = self.func.__name__
        if cached_name not in obj.__dict__:
            obj.__dict__[cached_name] = self.func(obj)

        value = obj.__dict__.get(cached_name)
        return value

    def __reduce__(self):
        return cached_property.__new__, (cached_property,), {'func': self.func}


def remove_raw_object(cls):
    """
    Decorator.
    If a Record class is decorated, raw_object will be removed once all mark properties are cached.
    """
    cls.remove_raw_object = True
    return cls


def generate_record_property_cache(obj):
    """
    Generate final value on all cached_property decorated methods.
    
    Args:
        obj (Record): Record instance.
    """
    for prop_name, prop_type in obj.__class__.__dict__.items():
        if isinstance(prop_type, cached_property):
            getattr(obj, prop_name)

    validate_record(obj)

    if obj.__class__.remove_raw_object:
        del obj.__dict__['raw_object']


def validate_record(obj):
    """
    Property validator of record instance.
    
    Args:
        obj (Record): Record instance.
        
    Raises:
        TypeError: if id is not valid
    """
    if not isinstance(obj.id, str):
        raise TypeError('Id in {} should be an utf-8 encoded string.'.format(obj.__class__.__name__))
    if not re_record_id.match(obj.id):
        raise ValueError('Id is not valid')


def get_property_names(cls: type):
    """
    Get keys of property and cached_property from a record class.
    
    Args:
        cls (type): Record class
    
    Returns:
        list: Property names in class
    """
    keys = []
    for prop_name, prop_type in cls.__dict__.items():
        if not isinstance(prop_type, property) and not isinstance(prop_type, cached_property):
            continue
        keys.append(prop_name)
    return keys


@remove_raw_object
class AutoGeneratedRecord(Record):
    """
    Properties are auto generated based on the keys in `raw_object`.

    `raw_object` has to contain `id` which used as id in record.

    Args:
        raw_object (object): Raw data which will be used to create properties.
    """

    def __init__(self, raw_object):
        super().__init__(raw_object)
        for k, v in raw_object.items():
            if k == 'id':
                continue
            setattr(self, k, v)

    @cached_property
    def id(self):
        return self.raw_object['id']
