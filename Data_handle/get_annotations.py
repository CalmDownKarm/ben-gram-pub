from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import pandas as pd
import fire

engine = create_engine('postgresql://postgres:docker@localhost:5432/postgres')

def get_rows(samples=1000,num_annotators=7, emailoverlap=0.3, essayoverlap=0.1):
    '''
    batch1, batch2, batch3, return an excel file of samples, split amongst number of annotators
    with an overlap percentage.
    '''
    query_string = 'select * from all_rows'
    rows = pd.read_sql(query_string, engine)
    annotations = pd.read_sql('select * from annotations', engine)
    all_annotated = annotations.ORIGINAL.unique()
    unannotated = rows[~rows['ORIGINAL'].isin(all_annotated)]
    unannotated.drop_duplicates(subset='ORIGINAL', inplace=True)
    unannotated['CEFR-J'] = unannotated['CEFR-J'].fillna('dunno')
    partA = unannotated[unannotated['PART']=='PART A']
    partB = unannotated[unannotated['PART']=='PART B']
    
    _, x_TA, _, y_TA = train_test_split(partA[['ORIGINAL', 'PART',]], partA['CEFR-J'], 
                                      test_size = samples//2, random_state=42,
                                      stratify=partA['CEFR-J'])
    _, x_TB, _, y_TB = train_test_split(partB[['ORIGINAL', 'PART']], partB['CEFR-J'], 
                                      test_size = samples//2, random_state=42,
                                      stratify=partB['CEFR-J'])
    
    partA = pd.concat([x_TA, y_TA], axis=1)
    partB = pd.concat([x_TB, y_TB], axis=1)
    
    commonA = partA.sample(frac=emailoverlap)
    commonB = partB.sample(frac=essayoverlap)
    
    uniqueA = partA[~partA.ORIGINAL.isin(commonA.ORIGINAL.values)]
    uniqueB = partB[~partB.ORIGINAL.isin(commonB.ORIGINAL.values)]
   
    unique = pd.concat([uniqueA, uniqueB])
    common = pd.concat([commonA, commonB])
    
    num_rows = len(unique.index)//num_annotators
    
    seperated = [unique[num_rows*a:num_rows*(a+1)] for a in range(0, num_annotators)]
    seperated = [pd.concat([common, un]) for un in seperated]
    
    for ind, batch in enumerate(seperated):
        batch.to_excel(f'Annotator_{ind}.xlsx', index=None)
    
if __name__ == '__main__':
    fire.Fire(get_rows)
