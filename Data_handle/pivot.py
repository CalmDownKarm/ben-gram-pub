import pandas as pd 

def parse_sheets(excelfile, sheetname, part):
    df = excelfile.parse(sheetname)
    df['ANNOTATOR'] = sheetname
    return df

def pivot(essays_file, emails_file, filename='overlaps', old_pivots=None):
    essays = pd.ExcelFile(essays_file)
    emails = pd.ExcelFile(emails_file)
    essays = [parse_sheets(essays, sheet, 'PART B') for sheet in essays.sheet_names]
    emails = [parse_sheets(emails, sheet, 'PART A') for sheet in emails.sheet_names]
    if old_pivots:
        old_pivots = pd.read_excel(old_pivots)
        old_unpivots = old_pivots.melt(id_vars='ORIGINAL', var_name='ANNOTATOR', value_name='ANNOTATION')\
            .dropna(subset=['ANNOTATION'])
        emails += [old_unpivots]
    total = pd.concat(emails+essays)
    pivoted = total.dropna(subset=['ANNOTATION'])\
        .drop_duplicates(subset=['ORIGINAL', 'ANNOTATOR'])\
        .pivot(index='ORIGINAL', columns='ANNOTATOR', values='ANNOTATION')
    pivoted.reset_index().to_excel(f'{filename}.xlsx')
    