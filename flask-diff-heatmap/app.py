import json
import pandas as pd

from flask import Flask, render_template
import itertools

#import sys
#sys.path.append("/Users/dteng/miniconda3/lib/python3.8/site-packages")

# T-test or MWU test?
from scipy.stats import ttest_ind, mannwhitneyu
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import TTestIndPower


app = Flask(__name__)


def get_group_arrays(colnames_ls):
    """Given a list of sample names, allocate them to their respective groups.
    Assumes that the sample names are affixed with the group name, delimited by '_'. 
    e.g. a sample name "g1_sample1" belongs to group "g1". 
    
    PARAMS
    ------
    colnames_ls: list of string
    
    RETURNS
    -------
    groups_dict: dictionary of sample names. 
    keys are group names, values are list of sample names. 
    """
    groups_set_ls = list(set([x.split("_")[0] for x in colnames_ls]))
    
    groups_dict = {}
    for gname in groups_set_ls:
        groups_dict[gname] = []
    
    for cname in colnames_ls:
        for gname in groups_set_ls:
            if cname.split("_")[0] == gname:
                groups_dict[gname].append(cname)

    return groups_dict


@app.route("/")
def index():
    # df = pd.read_csv("./static/data/heatmap_data.csv").drop("Open", axis=1)
    # chart_data = df.to_dict(orient='records')
    # chart_data = json.dumps(chart_data, indent=2)
    # data = {'chart_data': chart_data}
    # this will be passed to index.html as an array of JS objects

    #d0 = pd.read_csv("./static/data/heatmap_data.csv")
    d0 = pd.read_csv("/Users/dteng/Documents/zdata/sample-luca-data-3classes.csv")
    # do all possible comparisons
    data_colnames_ls = list(d0.columns)[3:] # get this by ignoring the first 3 cols
    gdict = get_group_arrays(data_colnames_ls)
    comparisons_ls = [list(x) for x in list(set(itertools.combinations(list(gdict.keys()), 2)))]
    d0["feature_id"] = d0.apply(lambda row: str(int(row[d0.columns[0]]))+"_"+str(round(row[d0.columns[1]], 4))+"@"+str(round(row[d0.columns[2]], 4)), axis=1)

    # Do all multiple comparisons
    comparison_result_ls = []
    for comparison in comparisons_ls:
        for i in range(len(d0)):
            arr0 = d0.iloc[i][gdict[comparison[0]]].values
            arr1 = d0.iloc[i][gdict[comparison[1]]].values
            
            t_stat, p_val = ttest_ind(arr0, arr1, equal_var = False)
            comparison_result_ls.append([d0.iloc[i]["feature_id"], "_v_".join(comparison), t_stat, p_val])
            
    d1 = pd.DataFrame(data=comparison_result_ls, columns=["feature_id", "comparison", "t_stat", "p_val"])
    result = multipletests(list(d1["p_val"]), alpha=0.05, method="fdr_bh")
    d1["q_val"] = result[1]

    # this next list can be hardcoded because d1 is generated in this script anyway
    colnames_to_viz_ls = ["feature_id", "comparison", "q_val"]
    chart_data = []
    for i in range(len(d1)):
        new_row_dict = {}
        for cname in colnames_to_viz_ls:
            new_row_dict[cname] = str(d1.iloc[i][cname])
        chart_data.append(new_row_dict)
    
    chart_data = json.dumps(chart_data, indent=2)
    flask_data = {'chart_data': chart_data}

    return render_template("index.html", flask_data=flask_data)


if __name__ == "__main__":
    app.run(debug=True)