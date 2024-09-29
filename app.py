from ariadne import QueryType, make_executable_schema, gql
from ariadne.asgi import GraphQL
from typing import List, Optional
import asyncio
from scrapper import get_ansm_content

# Assuming you have these functions implemented
from index_builder import build_graph
from filters import apply_date_filters, apply_string_filters
from utils import remove_leading_zeros

def get_values_by_sorted_key(obj):
    # Get the keys of the dictionary, sort them, and then map to their values
    return [obj[k] for k in sorted(obj.keys())]

def slice_array(array, from_index=0, limit=None):
    # If from_index is greater than or equal to the length of the array, return an empty list
    if from_index >= len(array):
        return []
    # Slice the array from the from_index to from_index + limit
    return array[from_index:from_index + limit if limit else None]

# Load your schema
with open("schema.graphql", "r") as schema_file:
    type_defs = gql(schema_file.read())

# Define your resolvers
query = QueryType()

@query.field("medicaments")
def resolve_medicaments(_, info, CIS=None, limit=None, from_=None, date_AMM=None,
                        denomination=None, forme_pharmaceutique=None,
                        voies_administration=None, statut_admin_AMM=None,
                        type_procedure_AMM=None, etat_commercialisation=None,
                        statut_BDM=None, numero_autorisation_europeenne=None):
    results = graph['medicaments']

    if CIS:
        results = {k: v for k, v in results.items() if k in CIS}

    results = list(results.values())

    if from_ is not None:
        results = results[from_:]
    if limit is not None:
        results = results[:limit]

    return results

@query.field("substances")
def resolve_substances(_, info, codes_substances=None, limit=None, from_=None, denomination=None):
    results = graph['substances']
    
    if codes_substances:
        results = {k: v for k, v in results.items() if k in codes_substances}
    
    results = list(results.values())
    
    print(results)
    
    if from_ is not None:
        results = results[from_:]
    if limit is not None:
        results = results[:limit]
    
    return results

@query.field("presentations")
def resolve_presentations(_, info, CIP=None, limit=None, from_=None, libelle=None,
                          statut_admin=None, etat_commercialisation=None,
                          indications_remboursement=None):
    results = graph['presentations']
    
    # Apply filters...
    
    if from_ is not None:
        results = results[from_:]
    if limit is not None:
        results = results[:limit]
    
    return results

@query.field("groupes_generiques")
def resolve_groupes_generiques(_, info, ids=None, limit=None, from_=None, libelle=None):
    results = graph['groupes_generiques']
    
    # Apply filters...
    
    if from_ is not None:
        results = results[from_:]
    if limit is not None:
        results = results[:limit]
    
    return results

@query.field("ansmContent")
async def resolve_ansm_content(_, info, id: int):
    try:
        content = await get_ansm_content(id)
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

schema = make_executable_schema(type_defs, query)
graph = asyncio.run(build_graph())
app = GraphQL(schema, debug=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)