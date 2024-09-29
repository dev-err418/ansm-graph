import csv
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Any
from bdm_file_parser import Parser
from bdm_files import files
from bdm_client import download_http_file

@dataclass
class IndexKey:
    value: str
    unique: bool

@dataclass
class Index:
    _keys: List[IndexKey]
    _indexes: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        for key in self._keys:
            self._indexes[key.value] = {}

    def add_object(self, obj):
        dynamic_obj = obj if isinstance(obj, DynamicObject) else DynamicObject(**obj)
        for key in self._keys:
            id_value = getattr(dynamic_obj, key.value)
            index = self._indexes[key.value]
            existing = index.get(id_value)
            if existing and key.unique:
                raise ValueError(f"Duplicate key in {key.value}: {id_value}")
            elif existing:
                if isinstance(existing, list):
                    existing.append(dynamic_obj)
                else:
                    index[id_value] = [existing, dynamic_obj]
            else:
                index[id_value] = [dynamic_obj] if not key.unique else dynamic_obj
        return dynamic_obj

def map_to_index(array, key, index):
    keys = list(set(getattr(obj, key) for obj in array))
    return [index.get(k) for k in sorted(keys) if k in index]

class DynamicObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._getters = {}

    def __getattr__(self, name):
        if name in self._getters:
            return self._getters[name](self)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

def add_getter(obj, field, getter):
    obj._getters[field] = getter
    
async def process_stream(stream_promise, fn, filename):
    stream = await stream_promise
    parser = Parser(filename)
    i = -1
    async for line in stream:
        i += 1
        if not parser.is_valid_line(line):
            print(f"{filename}: line {i} ignored:\n\t\"{line}\"")
            continue
        parsed_data = parser.parse_line(line)
        dynamic_obj = DynamicObject(**parsed_data)
        fn(dynamic_obj)
    print(f"Processed {filename}")

async def process_streams(stream_promises, fns):
    tasks = []
    for key in fns:
        filename = files[key]
        fn = fns[key]
        task = process_stream(stream_promises[key], fn, filename)
        tasks.append(task)
    await asyncio.gather(*tasks)

def safe_get_attribute(obj, attr):
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None
    
async def build_graph():
    print("Building graph...")    

    streams = {key: download_http_file(filename) for key, filename in files.items()}

    indexes = {
        "presentations": Index([
            IndexKey('CIP7', True),
            IndexKey('CIP13', True),
            IndexKey('CIS', False),
        ]),
        "substances": Index([
            IndexKey('code_substance', False),
            IndexKey('CIS', False),
        ]),
        "groupesGeneriques": Index([
            IndexKey('id', False),
        ]),
        "medicaments": Index([
            IndexKey('CIS', True),
        ]),
        "conditions": Index([
            IndexKey('CIS', False),
        ]),
    }

    await process_streams(streams, {
        "groupesGeneriques": indexes["groupesGeneriques"].add_object,
        "conditions": lambda c: (
            indexes["conditions"].add_object(c),
            # print(f"Added condition for CIS: {c.CIS}, conditions_prescription: {safe_get_attribute(c, 'conditions_prescription') or 'N/A'}")
        ),
        "substances": lambda s: (
            indexes["substances"].add_object(s),
            add_getter(s, 'medicament', lambda self: indexes["medicaments"]._indexes['CIS'].get(self.CIS)),
            add_getter(s, 'medicaments', lambda self: map_to_index(
                indexes["substances"]._indexes['code_substance'].get(self.code_substance, []),
                'CIS',
                indexes["medicaments"]._indexes['CIS']
            ))
        ),
        "presentations": lambda p: (
            indexes["presentations"].add_object(p),
            add_getter(p, 'medicament', lambda self: indexes["medicaments"]._indexes['CIS'].get(self.CIS))
        ),
        "medicaments": lambda m: (
            indexes["medicaments"].add_object(m),
            add_getter(m, 'presentations', lambda self: indexes["presentations"]._indexes['CIS'].get(self.CIS, [])),
            add_getter(m, 'substances', lambda self: indexes["substances"]._indexes['CIS'].get(self.CIS, [])),
            add_getter(m, 'groupes_generiques', lambda self: indexes["groupesGeneriques"]._indexes['CIS'].get(self.CIS, []) if isinstance(indexes["groupesGeneriques"]._indexes['CIS'].get(self.CIS), list) else []),
            add_getter(m, 'conditions_prescription', lambda self: [
                safe_get_attribute(o, 'conditions_prescription')
                for o in indexes["conditions"]._indexes['CIS'].get(self.CIS, [])
                if safe_get_attribute(o, 'conditions_prescription')
            ])
        ),
    })

    for substances in indexes["substances"]._indexes['code_substance'].values():
        denominations = list(set(s.denomination for s in substances))
        for s in substances:
            s.denominations = denominations

    indexes["groupesGeneriques"]._indexes['CIS'] = {}
    groupesGeneriquesById = indexes["groupesGeneriques"]._indexes['id']
    groupesGeneriquesByCIS = indexes["groupesGeneriques"]._indexes['CIS']

    for id, all in groupesGeneriquesById.items():
        g = {"id": id, "libelle": all[0].libelle}
        meds = [[], [], [], None, []]
        for o in all:
            cis = o.CIS
            if cis not in groupesGeneriquesByCIS:
                groupesGeneriquesByCIS[cis] = []
            groupesGeneriquesByCIS[cis].append(g)
            medicament = indexes["medicaments"]._indexes['CIS'].get(cis)
            if medicament:
                type_ = int(o.type)
                meds[type_].append(medicament)
        meds.pop(3)
        g["princeps"], g["generiques"], g["generiques_complementarite_posologique"], g["generiques_substituables"] = meds
        groupesGeneriquesById[id] = g

    with open("ansm.csv", mode="r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            specid = row['specid']
            indications = row['indications']
            posologie = row['posologie']
            medicament = indexes["medicaments"]._indexes['CIS'].get(specid)
            if medicament:
                medicament.indications = indications
                medicament.posologie = posologie

    graph = {
        "substances": {code: substances[0] for code, substances in indexes["substances"]._indexes['code_substance'].items()},
        "medicaments": indexes["medicaments"]._indexes['CIS'],
        "presentations": indexes["presentations"]._indexes,
        "groupes_generiques": groupesGeneriquesById,
    }

    print("Graph built done.")
    return graph

if __name__ == "__main__":
    asyncio.run(build_graph())