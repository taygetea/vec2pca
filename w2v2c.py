#!/usr/bin/python3

from spyre import server

import pandas as pd
import json

class StockExample(server.App):

    inputs = [{"type":'dropdown',
                "label": 'Corpus',
                "options" : [ {"label": "Lesswrong", "value":"lw"},
                              {"label": "HG Wells", "value":"hgw"},
                              {"label": "Hacker News", "value": "hn"},
                              {"label": "John Stuart Mill", "value":"jsm"}],
                "value":'lw',
                "key": 'ticker',
                "action_id": "update_data"},
            {"type": "dropdown",
                "label": "Plot",
                "value": "12",
                "key": "components",
                "action_id": "update_data",
                "options":
                          [{"label": "1,2", "value": "12"},
                           {"label": "1,3", "value": "13"},
                           {"label": "2,3", "value": "23"}]
            },
            {"type": "slider",
                "label": "Words",
                "min": 5, "max": 50, "step":1, "value":10,
                "key": "numwords",
                "action_id": "update_data"}]


    controls = [{ "type": "hidden",
		  "id": "update_data"}]

    tabs = ["Table", "Plot"]

    outputs = [{"type" : "html",
                "id" : "plot",
                "control_id" : "update_data",
                "tab" : "Plot"},
                {"type" : "table",
                "id" : "table_id",
                "control_id" : "update_data",
                "tab" : "Table",
                "on_page_load" : True }]

    def getData(self, params):
        corpus = params['ticker']
        length = params['numwords']
        df = pd.read_csv("%s_components.csv" % corpus)
        df2 = pd.concat([df.head(length), df.tail(length)], axis=0)
        df2.rename(columns=lambda x: "PC"+str(x), inplace=True)
        return df2

    def getHTML(self, params):
        corpus = params['ticker']
        comps = params['components']
        print("%s_comp_%s.html" % (corpus, comps))
        with open("%s_comp_%s.html" % (corpus, comps)) as f:
            return f.read()

    def getCustomHead(self):
        html = """
        <h1>Word Vector Principal Components</h1>
        <h4 style=\"font-size: 20px;\">This tool visualizes the <a href=\"https://en.wikipedia.org/wiki/Principal_component_analysis\">principal components</a> of the <a href=\"https://en.wikipedia.org/wiki/Word2vec\">word vectors</a> of a text corpus.</h4>
        """
        return html

#	def getPlot(self, params):
#		df = self.getData(params)
#		plt_obj = df.set_index('Date').drop(['volume'],axis=1).plot()
#		plt_obj.set_ylabel("Price")
#		plt_obj.set_title(self.company_name)
#		fig = plt_obj.get_figure()
#		return fig
if __name__ == '__main__':
    app = StockExample()
    app.launch(port=9093)
