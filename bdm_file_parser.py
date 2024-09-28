import re
# from datetime import datetime
from bdm_files import files, schemas
from utils import str_to_date, remove_leading_zeros

def format_float_number(value):
    if value:
        value = re.sub(r',([0-9]+)$', r'.\1', value).replace(',', '')
    return value

mappings = {
    files['medicaments']: {
        'CIS': remove_leading_zeros,
        'surveillance_renforcee': lambda v: oui_non_to_booleans(v),
        'date_AMM': lambda v: str_to_date(v) if v else v,
        'titulaires': lambda v: v.split(';') if v else [],
    },
    files['presentations']: {
        'CIS': remove_leading_zeros,
        'taux_remboursement': lambda v: v.replace('%', '').strip() if v else v,
        'agrement_collectivites': lambda v: oui_non_to_booleans(v),
        'prix_sans_honoraires': format_float_number,
        'prix_avec_honoraires': format_float_number,
        'honoraires': format_float_number,
        'date_declaration_commercialisation': lambda v: str_to_date(v) if v else v,
    },
    files['substances']: {
        'CIS': remove_leading_zeros,
        'code_substance': remove_leading_zeros,
    },
    files['groupesGeneriques']: {
        'CIS': remove_leading_zeros,
    },
}

def oui_non_to_booleans(value):
    if value:
        if value.lower() == 'non':
            return False
        if value.lower() == 'oui':
            return True
    return value

class Parser:
    def __init__(self, filename):
        self.filename = filename

    def parse_line(self, content):
        schema = schemas[self.filename]
        if not self.is_valid_line(content):
            raise ValueError(f'Invalid line in {self.filename}: "{content}"')
        parts = self.split_line(content)
        obj = {}
        mappings_ = mappings.get(self.filename, {})
        for i, p in enumerate(parts):
            p = p.strip() or None  # empty values are set to None
            prop = schema[i]
            mapping = mappings_.get(prop)
            if mapping:
                p = mapping(p)
            obj[prop] = p
        return obj

    def split_line(self, content):
        content = content.rstrip()  # Remove trailing whitespace
        return content.split('\t')

    def is_valid_line(self, content):
        schema = schemas[self.filename]
        parts = self.split_line(content)
        return parts and len(parts) <= len(schema)
