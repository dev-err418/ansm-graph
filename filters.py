from typing import List, Dict, Any, Callable
from datetime import date

def apply_filters(objects: List[Dict[str, Any]], filters: List[Dict[str, Any]], 
                  fields: List[str], filter_function: Callable) -> List[Dict[str, Any]]:
    def filter_object(obj: Dict[str, Any]) -> bool:
        for i, filter_ in enumerate(filters):
            if not filter_ or len(filter_) == 0:
                continue
            if not filter_function(filter_, obj.get(fields[i])):
                return False
        return True

    return list(filter(filter_object, objects))

def apply_date_filters(objects: List[Dict[str, Any]], filters: List[Dict[str, Any]], 
                       fields: List[str]) -> List[Dict[str, Any]]:
    def date_filter(filter_: Dict[str, date], date_value: date) -> bool:
        before = filter_.get('before')
        after = filter_.get('after')
        return (not before or date_value <= before) and (not after or date_value >= after)

    return apply_filters(objects, filters, fields, date_filter)

def apply_string_filters(objects: List[Dict[str, Any]], filters: List[Dict[str, Any]], 
                         fields: List[str]) -> List[Dict[str, Any]]:
    def string_filter(f: Dict[str, List[str]], str_value: str) -> bool:
        if not str_value:
            return False
        str_value = str_value.lower()

        if 'contains_one_of' in f and not any(s.lower() in str_value for s in f['contains_one_of']):
            return False
        
        if 'starts_with_one_of' in f and not any(str_value.startswith(s.lower()) for s in f['starts_with_one_of']):
            return False
        
        if 'ends_with_one_of' in f and not any(str_value.endswith(s.lower()) for s in f['ends_with_one_of']):
            return False
        
        if 'contains_all' in f and not all(s.lower() in str_value for s in f['contains_all']):
            return False
        
        return True

    return apply_filters(objects, filters, fields, string_filter)